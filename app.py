import os
import requests
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="Workforce Optimization Platform",
    page_icon="📊",
    layout="wide"
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# DEMO EMPLOYEE DATA
# ============================================================

employee_data = [
    {
        "Employee ID": "E001",
        "Name": "Rahul",
        "Department": "AI",
        "Role": "AI Engineer",
        "Skills": "Python, Machine Learning",
        "Rate/hr": 300,
        "Max Hours": 40,
        "Preferred Shift": "Morning"
    },
    {
        "Employee ID": "E002",
        "Name": "Priya",
        "Department": "AI",
        "Role": "Data Scientist",
        "Skills": "Python, NLP",
        "Rate/hr": 350,
        "Max Hours": 40,
        "Preferred Shift": "Evening"
    },
    {
        "Employee ID": "E003",
        "Name": "Arjun",
        "Department": "Backend",
        "Role": "Backend Developer",
        "Skills": "Python, SQL",
        "Rate/hr": 280,
        "Max Hours": 40,
        "Preferred Shift": "Morning"
    }
]


# ============================================================
# SHIFT DATA
# ============================================================

shift_data = [
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


# ============================================================
# SESSION STATE
# ============================================================

if "employees" not in st.session_state:
    st.session_state["employees"] = pd.DataFrame(
        employee_data
    )

if "schedule_result" not in st.session_state:
    st.session_state["schedule_result"] = None

if "backend_connected" not in st.session_state:
    st.session_state["backend_connected"] = False


# ============================================================
# GEMINI EXPLANATION FUNCTION
# ============================================================

def explain_assignment(employee, assignment):
    """
    Gemini explains an already-created OR-Tools assignment.

    Gemini does NOT make the scheduling decision.
    OR-Tools makes the decision.
    """

    try:

        if not GEMINI_API_KEY:
            return (
                "Gemini API key is not configured. "
                "Add GEMINI_API_KEY to your .env file."
            )

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        employee_name = employee.get(
            "name",
            "Unknown"
        )

        department = employee.get(
            "department",
            "Unknown"
        )

        role = employee.get(
            "role",
            "Unknown"
        )

        skills = employee.get(
            "skills",
            []
        )

        preferred_shift = employee.get(
            "preferred_shift",
            "Unknown"
        )

        max_hours = employee.get(
            "max_hours",
            "Unknown"
        )

        hourly_rate = employee.get(
            "hourly_rate",
            0
        )

        shift_id = assignment.get(
            "shift_id",
            "Unknown"
        )

        shift_name = assignment.get(
            "shift_name",
            assignment.get(
                "name",
                "Unknown"
            )
        )

        duration = assignment.get(
            "duration_hours",
            0
        )

        cost = assignment.get(
            "cost",
            0
        )

        if isinstance(skills, list):
            skills_text = ", ".join(skills)
        else:
            skills_text = str(skills)

        prompt = f"""
You are an explainable AI assistant for a workforce scheduling platform.

IMPORTANT:
The scheduling decision has ALREADY been made by OR-Tools.
You must NOT make a new scheduling decision.
You must ONLY explain why the existing assignment is reasonable.

Employee information:
Name: {employee_name}
Department: {department}
Role: {role}
Skills: {skills_text}
Preferred Shift: {preferred_shift}
Maximum Hours: {max_hours}
Hourly Rate: ₹{hourly_rate}

Assignment:
Shift ID: {shift_id}
Shift Name: {shift_name}
Duration: {duration} hours
Assignment Cost: ₹{cost}

Explain the assignment using ONLY the information provided.

Consider:
- Whether the assigned shift matches the preferred shift
- Department alignment
- Role alignment
- Relevant skills
- Working hours
- Assignment cost

Do not invent:
- Experience
- Performance
- Availability
- Leave information
- Qualifications
- Certifications
- Personal information
- Any other facts not provided

Write a professional explanation in 3 to 5 sentences.
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

        return "Gemini did not return an explanation."

    except Exception as e:

        return (
            f"Gemini explanation failed.\n\n"
            f"{str(e)}"
        )


# ============================================================
# CONVERT EMPLOYEE DATA FOR BACKEND
# ============================================================

def prepare_employees_for_backend(dataframe):

    employees = []

    for _, row in dataframe.iterrows():

        skills = [
            skill.strip()
            for skill in str(
                row["Skills"]
            ).split(",")
            if skill.strip()
        ]

        employee = {
            "employee_id": str(
                row["Employee ID"]
            ),

            "name": str(
                row["Name"]
            ),

            "department": str(
                row["Department"]
            ),

            "role": str(
                row["Role"]
            ),

            "skills": skills,

            # IMPORTANT:
            # Backend expects hourly_rate
            "hourly_rate": float(
                row["Rate/hr"]
            ),

            "max_hours": float(
                row["Max Hours"]
            ),

            "preferred_shift": str(
                row["Preferred Shift"]
            )
        }

        employees.append(employee)

    return employees


# ============================================================
# PREPARE SHIFTS FOR BACKEND
# ============================================================

def prepare_shifts_for_backend():

    shifts = []

    for shift in shift_data:

        shifts.append(
            {
                "shift_id": shift["shift_id"],

                # Backend expects "name"
                "name": shift["name"],

                "duration_hours": shift[
                    "duration_hours"
                ],

                # Backend expects "required_staff"
                "required_staff": shift[
                    "required_staff"
                ]
            }
        )

    return shifts


# ============================================================
# CALL FASTAPI OPTIMIZATION ENGINE
# ============================================================

def generate_schedule(employees):

    payload = {
        "employees": prepare_employees_for_backend(
            employees
        ),

        "shifts": prepare_shifts_for_backend()
    }

    # Try the most likely optimization endpoints.
    endpoints = [
        "/schedule/optimize",
        "/optimize",
        "/schedule"
    ]

    last_error = None

    for endpoint in endpoints:

        try:

            response = requests.post(
                BACKEND_URL + endpoint,
                json=payload,
                timeout=30
            )

            if response.status_code == 404:
                continue

            if response.status_code == 422:

                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text

                return {
                    "success": False,
                    "error": (
                        "Backend validation error:\n\n"
                        f"{error_detail}"
                    )
                }

            if response.status_code >= 500:

                return {
                    "success": False,
                    "error": (
                        "FastAPI returned a server error:\n\n"
                        f"{response.text}"
                    )
                }

            if response.status_code == 200:

                return {
                    "success": True,
                    "data": response.json()
                }

            last_error = (
                f"HTTP {response.status_code}: "
                f"{response.text}"
            )

        except requests.exceptions.ConnectionError:

            return {
                "success": False,
                "error": (
                    "Could not connect to FastAPI.\n\n"
                    f"Make sure the backend is running at:\n"
                    f"{BACKEND_URL}"
                )
            }

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "error": (
                    "FastAPI request timed out."
                )
            }

        except Exception as e:

            last_error = str(e)

    return {
        "success": False,
        "error": (
            "Could not find a valid optimization endpoint.\n\n"
            f"Last error: {last_error}"
        )
    }


# ============================================================
# BACKEND HEALTH CHECK
# ============================================================

def check_backend():

    try:

        response = requests.get(
            BACKEND_URL + "/health",
            timeout=5
        )

        return response.status_code == 200

    except Exception:

        return False


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Workforce Optimization Platform"
)

st.subheader(
    "Intelligent Multi-Constraint Workforce Scheduling"
)

st.write(
    "Manage employees, shifts, availability, leave, "
    "projects, constraints and optimized schedules "
    "from one platform."
)

st.divider()


# ============================================================
# KPI CARDS
# ============================================================

current_employees = st.session_state[
    "employees"
]

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "👥 Employees",
        len(current_employees)
    )

with col2:

    st.metric(
        "📅 Shifts",
        len(shift_data)
    )

with col3:

    st.metric(
        "⚠️ Conflicts",
        0
    )

with col4:

    st.metric(
        "📋 Projects",
        0
    )


st.divider()


# ============================================================
# EMPLOYEE WORKSPACE
# ============================================================

st.header(
    "👥 Employee Workspace"
)

st.caption(
    "Edit employee information directly in "
    "the spreadsheet below."
)


edited_employee_df = st.data_editor(

    current_employees,

    num_rows="dynamic",

    use_container_width=True,

    hide_index=True,

    key="employee_editor",

    column_config={

        "Employee ID":
            st.column_config.TextColumn(
                "Employee ID"
            ),

        "Name":
            st.column_config.TextColumn(
                "Name"
            ),

        "Department":
            st.column_config.SelectboxColumn(
                "Department",
                options=[
                    "AI",
                    "Backend",
                    "Frontend",
                    "Testing",
                    "DevOps",
                    "HR"
                ]
            ),

        "Role":
            st.column_config.TextColumn(
                "Role"
            ),

        "Skills":
            st.column_config.TextColumn(
                "Skills",
                help="Separate skills using commas"
            ),

        "Rate/hr":
            st.column_config.NumberColumn(
                "Rate/hr",
                min_value=0,
                step=50,
                format="₹%d"
            ),

        "Max Hours":
            st.column_config.NumberColumn(
                "Max Hours",
                min_value=1,
                max_value=168,
                step=1
            ),

        "Preferred Shift":
            st.column_config.SelectboxColumn(
                "Preferred Shift",
                options=[
                    "Morning",
                    "Evening",
                    "Night",
                    "Flexible"
                ]
            )
    }
)


# ============================================================
# SAVE / RESET
# ============================================================

col_save, col_reset = st.columns(2)

with col_save:

    if st.button(
        "💾 Save Employee Changes",
        type="primary",
        use_container_width=True
    ):

        st.session_state[
            "employees"
        ] = edited_employee_df.copy()

        st.success(
            "Employee information updated successfully."
        )

        st.rerun()


with col_reset:

    if st.button(
        "↩️ Reset Demo Data",
        use_container_width=True
    ):

        st.session_state[
            "employees"
        ] = pd.DataFrame(
            employee_data
        )

        st.session_state[
            "schedule_result"
        ] = None

        st.rerun()


# ============================================================
# CURRENT EMPLOYEE DATA
# ============================================================

st.header(
    "📋 Current Employee Data"
)

st.dataframe(
    st.session_state["employees"],
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# BACKEND STATUS
# ============================================================

st.header(
    "🔌 Backend Status"
)

backend_status = check_backend()

if backend_status:

    st.success(
        "🟢 FastAPI backend is connected"
    )

else:

    st.error(
        "🔴 FastAPI backend is not running"
    )

    st.caption(
        f"Expected backend: {BACKEND_URL}"
    )


st.divider()


# ============================================================
# SCHEDULE OPTIMIZATION
# ============================================================

st.header(
    "🚀 Schedule Optimization"
)

st.caption(
    "Generate an optimized employee schedule "
    "using OR-Tools."
)


# ============================================================
# SHIFT REQUIREMENTS
# ============================================================

st.subheader(
    "🕐 Shift Requirements"
)

shift_df = pd.DataFrame(
    shift_data
)

st.dataframe(
    shift_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# GENERATE SCHEDULE
# ============================================================

if st.button(
    "🚀 Generate Optimized Schedule",
    type="primary",
    use_container_width=True
):

    if not backend_status:

        st.error(
            "FastAPI backend is not running. "
            "Start the backend first."
        )

    else:

        with st.spinner(
            "Running OR-Tools optimization..."
        ):

            result = generate_schedule(
                st.session_state["employees"]
            )

        if result["success"]:

            schedule_result = result["data"]

            st.session_state[
                "schedule_result"
            ] = schedule_result

            st.success(
                "✅ Optimized schedule generated successfully!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Schedule generation failed."
            )

            st.code(
                result["error"]
            )


# ============================================================
# DISPLAY OPTIMIZED SCHEDULE
# ============================================================

if st.session_state["schedule_result"]:

    result = st.session_state[
        "schedule_result"
    ]

    st.divider()

    st.header(
        "📊 Optimized Schedule"
    )

    status = result.get(
        "status",
        "UNKNOWN"
    )

    total_cost = result.get(
        "total_cost",
        0
    )

    assignments = result.get(
        "schedule",
        []
    )

    # --------------------------------------------------------
    # Result KPIs
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Optimization Status",
            status
        )

    with col2:

        st.metric(
            "Total Assignments",
            len(assignments)
        )

    with col3:

        st.metric(
            "Total Cost",
            f"₹{total_cost:,.0f}"
        )


    # --------------------------------------------------------
    # Assignment Table
    # --------------------------------------------------------

    if assignments:

        schedule_rows = []

        for assignment in assignments:

            schedule_rows.append(
                {
                    "Employee ID":
                        assignment.get(
                            "employee_id",
                            ""
                        ),

                    "Employee":
                        assignment.get(
                            "employee_name",
                            ""
                        ),

                    "Shift ID":
                        assignment.get(
                            "shift_id",
                            ""
                        ),

                    "Shift":
                        assignment.get(
                            "shift_name",
                            ""
                        ),

                    "Hours":
                        assignment.get(
                            "duration_hours",
                            0
                        ),

                    "Cost":
                        f"₹{assignment.get('cost', 0):,.0f}"
                }
            )

        schedule_df = pd.DataFrame(
            schedule_rows
        )

        st.subheader(
            "📋 Assignment Details"
        )

        st.dataframe(
            schedule_df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# BUILD EMPLOYEE LOOKUP
# ============================================================

    employee_lookup = {}

    current_employees = st.session_state[
        "employees"
    ]

    for _, employee_row in current_employees.iterrows():

        employee_id = str(
            employee_row["Employee ID"]
        )

        skills = [
            skill.strip()
            for skill in str(
                employee_row["Skills"]
            ).split(",")
            if skill.strip()
        ]

        employee_lookup[employee_id] = {

            "employee_id":
                employee_id,

            "name":
                str(
                    employee_row["Name"]
                ),

            "department":
                str(
                    employee_row["Department"]
                ),

            "role":
                str(
                    employee_row["Role"]
                ),

            "skills":
                skills,

            "hourly_rate":
                float(
                    employee_row["Rate/hr"]
                ),

            "max_hours":
                float(
                    employee_row["Max Hours"]
                ),

            "preferred_shift":
                str(
                    employee_row[
                        "Preferred Shift"
                    ]
                )
        }


# ============================================================
# WHY WERE THESE EMPLOYEES SELECTED?
# ============================================================

    st.divider()

    st.header(
        "🤖 Why Were These Employees Selected?"
    )

    st.caption(
        "OR-Tools makes the scheduling decision. "
        "Gemini explains the decision using the actual "
        "employee and assignment data."
    )


    if assignments:

        for index, assignment in enumerate(
            assignments
        ):

            employee_id = assignment.get(
                "employee_id"
            )

            employee = employee_lookup.get(
                str(employee_id)
            )

            if employee is None:

                st.warning(
                    f"Employee {employee_id} "
                    "was not found in employee data."
                )

                continue

            employee_name = employee[
                "name"
            ]

            shift_name = assignment.get(
                "shift_name",
                "Unknown"
            )

            st.subheader(
                f"👤 {employee_name} → {shift_name}"
            )

            col_info, col_button = st.columns(
                [3, 1]
            )

            with col_info:

                st.write(
                    f"**Role:** {employee['role']}"
                )

                st.write(
                    f"**Department:** "
                    f"{employee['department']}"
                )

                st.write(
                    f"**Skills:** "
                    f"{', '.join(employee['skills'])}"
                )

                st.write(
                    f"**Preferred Shift:** "
                    f"{employee['preferred_shift']}"
                )

            with col_button:

                explain_clicked = st.button(
                    "🤖 Explain Selection",
                    key=(
                        f"explain_"
                        f"{employee_id}_"
                        f"{index}"
                    ),
                    use_container_width=True
                )

            if explain_clicked:

                with st.spinner(
                    "Gemini is explaining the selection..."
                ):

                    explanation = (
                        explain_assignment(
                            employee,
                            assignment
                        )
                    )

                if explanation.startswith(
                    "Gemini explanation failed"
                ):

                    st.error(
                        explanation
                    )

                elif explanation.startswith(
                    "Gemini API key"
                ):

                    st.error(
                        explanation
                    )

                else:

                    st.success(
                        "✅ AI explanation generated"
                    )

                    st.info(
                        explanation
                    )

            st.divider()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Workforce Optimization Platform • "
    "Streamlit + FastAPI + OR-Tools + Gemini"
)