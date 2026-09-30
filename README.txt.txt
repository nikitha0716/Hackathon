📊 Workforce Optimization Platform
Intelligent Multi-Constraint Workforce Scheduling with Explainable AI

An AI-powered workforce scheduling platform that automatically assigns employees to shifts while considering multiple constraints such as working hours, shift requirements, employee preferences, skills, roles, and assignment cost.

The platform combines Google OR-Tools for deterministic schedule optimization with Google Gemini to provide human-readable explanations for why an employee was assigned to a particular shift.

🚀 Overview

Workforce scheduling becomes challenging when organizations need to balance:

Employee availability
Maximum working hours
Shift requirements
Employee preferences
Skills and roles
Department requirements
Workforce cost
Assignment feasibility

This project automates the scheduling process using a constraint optimization engine and presents the results through an interactive Streamlit interface.

✨ Key Features
👥 Employee Management
Add and edit employee information
Employee ID and name
Department and role
Skills
Hourly rate
Maximum working hours
Preferred shift
🗓️ Intelligent Scheduling
Automatic employee-to-shift assignment
Multi-constraint optimization
Shift staffing requirements
Maximum working-hour constraints
Cost-aware scheduling
Feasible schedule generation
🧠 Explainable AI

After the optimization engine generates a schedule, Gemini explains the assignment in natural language.

For example:

Rahul was assigned to the Morning shift because it matches his preferred shift, aligns with his AI Engineer role and department, and remains within his maximum working-hour limit.

This makes the scheduling decision easier for managers and users to understand.

📊 Interactive Dashboard

The Streamlit interface provides:

Employee workspace
Editable employee table
Schedule optimization
Assignment results
Total scheduling cost
AI-generated assignment explanations
Optimization status
🏗️ System Architecture
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    │  Employee Dashboard  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI API      │
                    │ Validation & Routing  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    OR-Tools Solver   │
                    │ Constraint Optimizer │
                    └──────────┬───────────┘
                               │
                    Optimized Schedule
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Gemini API       │
                    │ Explain Assignments  │
                    └──────────┬───────────┘
                               │
                               ▼
                    Human-readable Reason
⚙️ Optimization Logic

The scheduling engine separates constraints into different categories.

Hard Constraints

These must be satisfied:

Required number of employees per shift
Maximum working hours
Valid employee assignments
Shift duration requirements
Schedule feasibility
Scheduling Preferences

The system can consider:

Preferred shift
Employee role
Department
Relevant skills
Workforce utilization
Objective

The optimization engine searches for a feasible schedule while minimizing assignment cost and respecting the defined workforce constraints.

🧠 Why OR-Tools?

Google OR-Tools is used because workforce scheduling is fundamentally a constraint optimization problem.

Instead of manually deciding:

Rahul → Morning
Priya → Evening
Arjun → Morning

the solver evaluates the available employees and constraints to determine a feasible optimized assignment.

This approach makes the scheduling logic:

Deterministic
Constraint-aware
Scalable
Reproducible
Easier to extend
🤖 Why Gemini?

OR-Tools determines what the schedule should be.

Gemini explains why the assignment makes sense.

This creates a clear separation:

OR-Tools
    ↓
Optimization decision
    ↓
Gemini
    ↓
Natural-language explanation

Gemini is therefore used as an explanation layer, rather than allowing a generative model to directly make the scheduling decision.

This helps preserve the deterministic behavior of the optimization engine.

🛠️ Technology Stack
Technology	Purpose
Python	Core development
Streamlit	Frontend / dashboard
FastAPI	Backend API
Pydantic	Request validation
Google OR-Tools	Workforce optimization
Google Gemini API	AI explanations
Pandas	Employee data handling
Uvicorn	FastAPI server
Git & GitHub	Version control
📁 Project Structure
Hackathon/
│
├── app.py
│
├── backend/
│   ├── main.py
│   │
│   ├── api/
│   │   └── scheduling.py
│   │
│   └── scheduler/
│       ├── solver.py
│       └── test_solver.py
│
├── gemini_explainer.py
├── nova_test.py
│
├── requirements.txt
├── .gitignore
└── README.md
💻 Installation
1. Clone the repository
git clone https://github.com/nikitha0716/Hackathon.git

Navigate into the project:

cd Hackathon
2. Create a virtual environment

Windows:

python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1

If PowerShell blocks script execution, you can run the project using the virtual environment's Python directly:

.\venv\Scripts\python.exe app.py
3. Install dependencies
pip install -r requirements.txt
🔑 Environment Variables

Create a .env file in the project root.

GEMINI_API_KEY=your_gemini_api_key

⚠️ Never commit your real API key to GitHub.

The .env file should remain ignored by Git.

For other developers, create a .env.example:

GEMINI_API_KEY=your_api_key_here
▶️ Running the Application
Start the FastAPI backend

From the project root:

.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload

The backend will be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Start the Streamlit application

Open another terminal in the project folder:

.\venv\Scripts\python.exe -m streamlit run app.py

Streamlit will provide a local URL similar to:

http://localhost:8501
🔄 Application Workflow
1. Add employee data
        ↓
2. Define shifts
        ↓
3. Submit scheduling request
        ↓
4. FastAPI validates the data
        ↓
5. OR-Tools generates optimized schedule
        ↓
6. Schedule returned to Streamlit
        ↓
7. Gemini analyzes assignment context
        ↓
8. Explanation displayed to user
📌 Example
Employee
Employee ID: E001
Name: Rahul
Role: AI Engineer
Department: AI
Skills: Python, Machine Learning
Hourly Rate: ₹300
Maximum Hours: 40
Preferred Shift: Morning
Assignment
Rahul → Morning
Duration: 8 hours
Cost: ₹2400
Status: OPTIMAL
Explanation

The AI explanation can identify that:

Rahul's preferred shift is Morning
His department is AI
His role is AI Engineer
His skills include Python and Machine Learning
The 8-hour assignment is within his 40-hour limit
The cost is calculated using his hourly rate
🎯 Advantages
For Managers
Reduces manual scheduling effort
Provides transparent assignment reasoning
Helps control workforce cost
Makes schedule generation faster
For Employees
Takes shift preferences into consideration
Helps avoid excessive working hours
Provides more structured scheduling
For Organizations
Constraint-based workforce allocation
Reduced scheduling conflicts
Better workforce utilization
Extensible optimization architecture
🔮 Future Scope

The current prototype can be extended with:

Employee availability calendars
Leave management
Overtime detection
Project-specific staffing
Multi-project scheduling
Database persistence
Authentication and role-based access
Schedule history
Analytics dashboard
Workforce demand forecasting
Skill-gap analysis
Automated hiring recommendations
Cloud deployment
🔐 Design Philosophy

The system follows a deterministic optimization + generative explanation architecture.

                  ┌─────────────────┐
                  │   Workforce     │
                  │      Data       │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │    OR-Tools     │
                  │   Optimization  │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Optimized       │
                  │ Schedule        │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │     Gemini      │
                  │   Explanation   │
                  └────────┬────────┘
                           ↓
                  ┌─────────────────┐
                  │ Transparent     │
                  │ Decision        │
                  └─────────────────┘

This architecture ensures that the AI explanation layer does not replace the underlying scheduling optimization.

👩‍💻 Team
Workforce Optimization Platform

Built as a collaborative hackathon project using:

Python • Streamlit • FastAPI • OR-Tools • Gemini

📄 License

This project was developed as a hackathon prototype for demonstrating intelligent workforce scheduling and explainable optimization.