from fastapi import APIRouter
from pydantic import BaseModel

from backend.scheduler.solver import optimize_schedule


router = APIRouter(
    prefix="/schedule",
    tags=["Scheduling"]
)


class EmployeeInput(BaseModel):
    employee_id: str
    name: str
    hourly_rate: float
    max_hours: float


class ShiftInput(BaseModel):
    shift_id: str
    name: str
    duration_hours: float
    required_staff: int


class ScheduleRequest(BaseModel):
    employees: list[EmployeeInput]
    shifts: list[ShiftInput]


@router.post("/optimize")
def optimize(request: ScheduleRequest):

    employees = [
        employee.model_dump()
        for employee in request.employees
    ]

    shifts = [
        shift.model_dump()
        for shift in request.shifts
    ]

    result = optimize_schedule(
        employees,
        shifts
    )

    return result