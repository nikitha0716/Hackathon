from ortools.sat.python import cp_model


def optimize_schedule(employees, shifts):
    """
    Workforce scheduling optimization engine.

    Hard constraints:
    - Required staffing must be satisfied.
    - Employee maximum working hours cannot be exceeded.

    Objective:
    - Minimize total labor cost.
    """

    model = cp_model.CpModel()

    # --------------------------------------------------------
    # DECISION VARIABLES
    # --------------------------------------------------------

    assignments = {}

    for employee in employees:

        employee_id = employee["employee_id"]

        for shift in shifts:

            shift_id = shift["shift_id"]

            assignments[(employee_id, shift_id)] = model.NewBoolVar(
                f"assign_{employee_id}_{shift_id}"
            )

    # --------------------------------------------------------
    # CONSTRAINT 1: REQUIRED STAFFING
    # --------------------------------------------------------

    for shift in shifts:

        shift_id = shift["shift_id"]

        required_staff = int(
            shift["required_staff"]
        )

        model.Add(
            sum(
                assignments[
                    (employee["employee_id"], shift_id)
                ]
                for employee in employees
            )
            == required_staff
        )

    # --------------------------------------------------------
    # CONSTRAINT 2: MAXIMUM WORKING HOURS
    # --------------------------------------------------------

    for employee in employees:

        employee_id = employee["employee_id"]

        max_hours = int(
            employee["max_hours"]
        )

        model.Add(
            sum(
                assignments[
                    (employee_id, shift["shift_id"])
                ]
                * int(shift["duration_hours"])
                for shift in shifts
            )
            <= max_hours
        )

    # --------------------------------------------------------
    # OBJECTIVE: MINIMIZE LABOR COST
    # --------------------------------------------------------

    total_cost = sum(
        assignments[
            (employee["employee_id"], shift["shift_id"])
        ]
        * int(
            employee["hourly_rate"]
            * shift["duration_hours"]
        )
        for employee in employees
        for shift in shifts
    )

    model.Minimize(total_cost)

    # --------------------------------------------------------
    # SOLVER
    # --------------------------------------------------------

    solver = cp_model.CpSolver()

    status = solver.Solve(model)

    # --------------------------------------------------------
    # INFEASIBLE
    # --------------------------------------------------------

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    ):

        return {
            "status": "INFEASIBLE",
            "schedule": [],
            "total_cost": 0
        }

    # --------------------------------------------------------
    # BUILD RESULT
    # --------------------------------------------------------

    schedule = []

    total_cost_value = 0

    for employee in employees:

        employee_id = employee["employee_id"]

        for shift in shifts:

            shift_id = shift["shift_id"]

            is_assigned = solver.Value(
                assignments[
                    (employee_id, shift_id)
                ]
            )

            if is_assigned:

                duration = float(
                    shift["duration_hours"]
                )

                hourly_rate = float(
                    employee["hourly_rate"]
                )

                cost = hourly_rate * duration

                total_cost_value += cost

                schedule.append(
                    {
                        "employee_id": employee_id,
                        "employee_name": employee["name"],
                        "shift_id": shift_id,
                        "shift_name": shift["name"],
                        "duration_hours": duration,
                        "cost": cost
                    }
                )

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "status": (
            "OPTIMAL"
            if status == cp_model.OPTIMAL
            else "FEASIBLE"
        ),
        "schedule": schedule,
        "total_cost": total_cost_value
    }