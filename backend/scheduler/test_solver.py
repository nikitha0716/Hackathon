from solver import optimize_schedule


employees = [
    {
        "employee_id": "E001",
        "name": "Rahul",
        "hourly_rate": 300,
        "max_hours": 40
    },
    {
        "employee_id": "E002",
        "name": "Priya",
        "hourly_rate": 350,
        "max_hours": 40
    },
    {
        "employee_id": "E003",
        "name": "Arjun",
        "hourly_rate": 280,
        "max_hours": 40
    }
]


shifts = [
    {
        "shift_id": "S001",
        "name": "Morning",
        "duration_hours": 8,
        "required_staff": 2
    },
    {
        "shift_id": "S002",
        "name": "Evening",
        "duration_hours": 8,
        "required_staff": 1
    }
]


result = optimize_schedule(
    employees,
    shifts
)


print("\n===== SCHEDULING RESULT =====")

print("Status:", result["status"])

print("Total Cost:", result["total_cost"])

print("\nAssignments:")

for assignment in result["schedule"]:

    print(
        f"{assignment['employee_name']} "
        f"-> {assignment['shift_name']} "
        f"({assignment['duration_hours']} hours) "
        f"₹{assignment['cost']}"
    )