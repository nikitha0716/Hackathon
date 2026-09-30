import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Workforce Optimizer",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Workforce Optimization Platform")

st.markdown(
    """
    ### Intelligent Multi-Constraint Workforce Scheduling

    Manage employees, shifts, availability, leave, projects,
    constraints and optimized schedules from one platform.
    """
)

st.divider()


# ============================================================
# KPI CARDS
# ============================================================

# Demo employee data for now
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

employee_df = pd.DataFrame(employee_data)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Employees",
        value=len(employee_df)
    )

with col2:
    st.metric(
        label="📅 Shifts",
        value="0"
    )

with col3:
    st.metric(
        label="⚠️ Conflicts",
        value="0"
    )

with col4:
    st.metric(
        label="📋 Projects",
        value="0"
    )


st.divider()


# ============================================================
# EMPLOYEE WORKSPACE
# ============================================================

st.subheader("👥 Employee Workspace")

st.caption(
    "Edit employee information directly in the spreadsheet below."
)


# ============================================================
# EMPLOYEE EDITOR
# ============================================================

edited_employee_df = st.data_editor(
    employee_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Employee ID": st.column_config.TextColumn(
            "Employee ID",
            help="Unique employee identifier"
        ),

        "Name": st.column_config.TextColumn(
            "Name",
            help="Employee full name"
        ),

        "Department": st.column_config.SelectboxColumn(
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

        "Role": st.column_config.TextColumn(
            "Role"
        ),

        "Skills": st.column_config.TextColumn(
            "Skills",
            help="Separate multiple skills using commas"
        ),

        "Rate/hr": st.column_config.NumberColumn(
            "Rate/hr",
            min_value=0,
            step=50,
            format="₹%d"
        ),

        "Max Hours": st.column_config.NumberColumn(
            "Max Hours",
            min_value=1,
            max_value=168,
            step=1
        ),

        "Preferred Shift": st.column_config.SelectboxColumn(
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


st.divider()


# ============================================================
# SAVE BUTTON
# ============================================================

col_save, col_reset = st.columns(2)

with col_save:

    if st.button(
        "💾 Save Employee Changes",
        type="primary",
        use_container_width=True
    ):

        st.session_state["employees"] = edited_employee_df

        st.success(
            "Employee information updated successfully."
        )


with col_reset:

    if st.button(
        "↩️ Reset Demo Data",
        use_container_width=True
    ):

        st.session_state["employees"] = pd.DataFrame(
            employee_data
        )

        st.rerun()


# ============================================================
# CURRENT DATA PREVIEW
# ============================================================

st.subheader("📋 Current Employee Data")

if "employees" in st.session_state:

    st.dataframe(
        st.session_state["employees"],
        use_container_width=True,
        hide_index=True
    )

else:

    st.dataframe(
        edited_employee_df,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ============================================================
# SCHEDULING SECTION
# ============================================================

st.subheader("🚀 Schedule Optimization")

if st.button(
    "Generate Optimized Schedule",
    type="primary",
    use_container_width=True
):

    st.warning(
        "Optimization engine is not connected yet. "
        "We will build the OR-Tools scheduling engine next."
    )


st.divider()


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Workforce Optimization Platform • "
    "Streamlit + FastAPI + OR-Tools"
)