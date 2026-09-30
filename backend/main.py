from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from ortools.sat.python import cp_model


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Workforce Optimization API",
    version="1.0.0",
    description="Multi-constraint workforce scheduling backend"
)


# ============================================================
# DATA MODELS
# ============================================================

class Employee(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str
    name: str
    department: str = ""
    role: str = ""
    skills: List[str] = []

    # Accept both names used by different versions of the app
    hourly_rate: Optional[float] = Field(
        default=None,
        alias="rate_per_hour"
    )

    max_hours: float = 40
    preferred_shift: str = "Flexible"


class Shift(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    shift_id: str

    # Accept both "name" and "shift_name"
    name: Optional[str] = None
    shift_name: Optional[str] = None

    duration_hours: float = 8

    # Accept both names
    required_staff: Optional[int] = None
    required_employees: Optional[int] = None

    def get_name(self):
        return self.name or self.shift_name or self.shift_id

    def get_required_staff(self):
        if self.required_staff is not None:
            return self.required_staff

        if self.required_employees is not None:
            return self.required_employees

        return 1


class ScheduleRequest(BaseModel):
    employees: List[Employee]
    shifts: List[Shift]


class Assignment(BaseModel):
    employee_id: str
    employee_name: str
    shift_id: str
    shift_name: str
    duration_hours: float
    cost: float


class ScheduleResponse(BaseModel):
    status: str
    schedule: List[Assignment]
    total_cost: float


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return "Workforce Optimization API is running"


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return "healthy"


# ============================================================
# EMPLOYEE TEST ENDPOINT
# ============================================================

@app.post("/employees")
def create_employee(employee: Employee):
    return {
        "message": "Employee received successfully",
        "employee": employee
    }


# ============================================================
# SCHEDULING ENGINE
# ============================================================

def generate_schedule(
    employees: List[Employee],
    shifts: List[Shift]
) -> ScheduleResponse:

    if not employees:
        raise ValueError("No employees provided.")

    if not shifts:
        raise ValueError("No shifts provided.")

    model = cp_model.CpModel()

    employee_count = len(employees)
    shift_count = len(shifts)

    # --------------------------------------------------------
    # DECISION VARIABLES
    #
    # x[e, s] = 1
    # employee e is assigned to shift s
    # --------------------------------------------------------

    x = {}

    for e in range(employee_count):
        for s in range(shift_count):

            x[e, s] = model.NewBoolVar(
                f"employee_{e}_shift_{s}"
            )

    # --------------------------------------------------------
    # CONSTRAINT 1
    #
    # Required number of employees for every shift
    # --------------------------------------------------------

    for s, shift in enumerate(shifts):

        required_staff = shift.get_required_staff()

        if required_staff < 0:
            required_staff = 0

        if required_staff > employee_count:
            raise ValueError(
                f"Shift '{shift.get_name()}' requires "
                f"{required_staff} employees, but only "
                f"{employee_count} employees are available."
            )

        model.Add(
            sum(
                x[e, s]
                for e in range(employee_count)
            )
            == required_staff
        )

    # --------------------------------------------------------
    # CONSTRAINT 2
    #
    # VERY IMPORTANT:
    # ONE EMPLOYEE CAN WORK ONLY ONE SHIFT
    #
    # This prevents:
    #
    # E003 -> Morning
    # E003 -> Evening
    #
    # --------------------------------------------------------

    for e in range(employee_count):

        model.Add(
            sum(
                x[e, s]
                for s in range(shift_count)
            )
            <= 1
        )

    # --------------------------------------------------------
    # CONSTRAINT 3
    #
    # Employee cannot work a shift longer than max hours
    # --------------------------------------------------------

    for e, employee in enumerate(employees):

        max_hours = employee.max_hours or 0

        for s, shift in enumerate(shifts):

            if shift.duration_hours > max_hours:

                model.Add(
                    x[e, s] == 0
                )

    # --------------------------------------------------------
    # OBJECTIVE
    #
    # Minimize:
    #
    # 1. Employee cost
    # 2. Small penalty if preferred shift doesn't match
    #
    # This makes the scheduler prefer employees who want
    # that shift while still minimizing cost.
    # --------------------------------------------------------

    objective_terms = []

    for e, employee in enumerate(employees):

        hourly_rate = (
            employee.hourly_rate
            if employee.hourly_rate is not None
            else 0
        )

        for s, shift in enumerate(shifts):

            duration = shift.duration_hours

            base_cost = hourly_rate * duration

            # ------------------------------------------------
            # Preference penalty
            # ------------------------------------------------

            preference_penalty = 0

            preferred = (
                employee.preferred_shift or ""
            ).strip().lower()

            shift_name = (
                shift.get_name() or ""
            ).strip().lower()

            if (
                preferred
                and preferred != "flexible"
                and preferred != shift_name
            ):
                preference_penalty = 100

            total_assignment_cost = (
                base_cost + preference_penalty
            )

            # CP-SAT works with integer objective values.
            objective_terms.append(
                int(total_assignment_cost * 100)
                * x[e, s]
            )

    model.Minimize(
        sum(objective_terms)
    )

    # ========================================================
    # SOLVE
    # ========================================================

    solver = cp_model.CpSolver()

    solver.parameters.max_time_in_seconds = 10

    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    # ========================================================
    # CHECK STATUS
    # ========================================================

    if status not in [
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ]:

        return ScheduleResponse(
            status="INFEASIBLE",
            schedule=[],
            total_cost=0
        )

    # ========================================================
    # BUILD RESULT
    # ========================================================

    assignments = []

    total_real_cost = 0

    for e, employee in enumerate(employees):

        hourly_rate = (
            employee.hourly_rate
            if employee.hourly_rate is not None
            else 0
        )

        for s, shift in enumerate(shifts):

            if solver.Value(x[e, s]) == 1:

                duration = shift.duration_hours

                real_cost = (
                    hourly_rate * duration
                )

                assignment = Assignment(
                    employee_id=employee.employee_id,
                    employee_name=employee.name,
                    shift_id=shift.shift_id,
                    shift_name=shift.get_name(),
                    duration_hours=duration,
                    cost=real_cost
                )

                assignments.append(
                    assignment
                )

                total_real_cost += real_cost

    # ========================================================
    # FINAL STATUS
    # ========================================================

    if status == cp_model.OPTIMAL:
        final_status = "OPTIMAL"
    else:
        final_status = "FEASIBLE"

    return ScheduleResponse(
        status=final_status,
        schedule=assignments,
        total_cost=total_real_cost
    )


# ============================================================
# MAIN SCHEDULE ENDPOINT
# ============================================================

@app.post(
    "/schedule",
    response_model=ScheduleResponse
)
def create_schedule(request: ScheduleRequest):

    try:

        result = generate_schedule(
            request.employees,
            request.shifts
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# OPTIMIZE ENDPOINT
#
# Kept as an additional endpoint so your frontend can use
# either /schedule or /optimize.
# ============================================================

@app.post(
    "/optimize",
    response_model=ScheduleResponse
)
def optimize_schedule(request: ScheduleRequest):

    try:

        result = generate_schedule(
            request.employees,
            request.shifts
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# DIRECT TEST ENDPOINT
# ============================================================

@app.get("/test-scheduler")
def test_scheduler():

    employees = [

        Employee(
            employee_id="E001",
            name="Rahul",
            department="AI",
            role="AI Engineer",
            skills=[
                "Python",
                "Machine Learning"
            ],
            rate_per_hour=300,
            max_hours=40,
            preferred_shift="Morning"
        ),

        Employee(
            employee_id="E002",
            name="Priya",
            department="AI",
            role="Data Scientist",
            skills=[
                "Python",
                "NLP"
            ],
            rate_per_hour=350,
            max_hours=40,
            preferred_shift="Evening"
        ),

        Employee(
            employee_id="E003",
            name="Sonu",
            department="Backend",
            role="Backend Developer",
            skills=[
                "Python",
                "SQL"
            ],
            rate_per_hour=280,
            max_hours=40,
            preferred_shift="Morning"
        ),

        Employee(
            employee_id="E004",
            name="Nikitha",
            department="AI",
            role="AI Engineer",
            skills=[
                "Python"
            ],
            rate_per_hour=1000,
            max_hours=8,
            preferred_shift="Morning"
        )
    ]

    shifts = [

        Shift(
            shift_id="S001",
            name="Morning",
            duration_hours=8,
            required_staff=2
        ),

        Shift(
            shift_id="S002",
            name="Evening",
            duration_hours=8,
            required_staff=1
        )
    ]

    return generate_schedule(
        employees,
        shifts
    )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )