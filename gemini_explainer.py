import os
import time

from dotenv import load_dotenv
from google import genai
from gemini_explainer import explain_assignment


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# MODELS
# ============================================================

MODELS = [
    "gemini-3.5-flash-lite",
]


# ============================================================
# EXPLAIN ASSIGNMENT
# ============================================================

def explain_assignment(assignment):

    employee_name = assignment.get(
        "employee_name",
        "Unknown employee"
    )

    employee_id = assignment.get(
        "employee_id",
        "Unknown ID"
    )

    shift_name = assignment.get(
        "shift_name",
        "Unknown shift"
    )

    shift_id = assignment.get(
        "shift_id",
        "Unknown shift ID"
    )

    duration_hours = assignment.get(
        "duration_hours",
        0
    )

    cost = assignment.get(
        "cost",
        0
    )

    preferred_shift = assignment.get(
        "preferred_shift",
        "Not specified"
    )

    skills = assignment.get(
        "skills",
        []
    )

    department = assignment.get(
        "department",
        "Not specified"
    )

    role = assignment.get(
        "role",
        "Not specified"
    )


    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    if isinstance(skills, list):

        skills_text = ", ".join(
            str(skill)
            for skill in skills
        )

    else:

        skills_text = str(skills)


    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are an explainable workforce scheduling assistant.

OR-Tools has already made the scheduling decision.

Your job is ONLY to explain that decision.

Do NOT make a new scheduling decision.

Do NOT invent information.

Use ONLY the information supplied below.

Employee ID: {employee_id}
Employee Name: {employee_name}

Department: {department}

Role: {role}

Skills: {skills_text}

Assigned Shift: {shift_name}

Shift ID: {shift_id}

Duration: {duration_hours} hours

Cost: ₹{cost}

Preferred Shift: {preferred_shift}

Explain why this assignment is reasonable.

Consider only the available information:
- shift preference
- skills
- role
- department
- duration
- cost

Do not claim availability, leave status,
rest periods, or other constraints unless
they are explicitly provided.

Write 2-4 professional sentences.
"""


    # --------------------------------------------------------
    # Try models
    # --------------------------------------------------------

    for model_name in MODELS:

        print(
            f"\nTrying Gemini model: {model_name}"
        )


        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )


                if response.text:

                    return response.text.strip()


            except Exception as error:

                error_text = str(error)

                print(
                    f"Attempt {attempt + 1} failed."
                )

                print(
                    error_text
                )


                # Retry temporary 503 errors

                if "503" in error_text:

                    time.sleep(3)

                    continue


                # Move to next model

                break


    return (
        "Gemini is temporarily unavailable. "
        "The OR-Tools optimization result is still valid."
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_assignment = {

        "employee_id": "E001",

        "employee_name": "Rahul",

        "department": "AI",

        "role": "AI Engineer",

        "skills": [
            "Python",
            "Machine Learning"
        ],

        "shift_id": "S001",

        "shift_name": "Morning",

        "duration_hours": 8,

        "cost": 2400,

        "preferred_shift": "Morning"
    }


    print()
    print("=" * 60)
    print("          GEMINI EXPLANATION TEST")
    print("=" * 60)


    try:

        explanation = explain_assignment(
            test_assignment
        )


        print()
        print("Employee : Rahul")
        print("Shift    : Morning")
        print()
        print("AI Explanation:")
        print(explanation)
        print()


    except Exception as error:

        print()
        print("❌ Gemini request failed.")
        print()
        print(error)


    print("=" * 60)