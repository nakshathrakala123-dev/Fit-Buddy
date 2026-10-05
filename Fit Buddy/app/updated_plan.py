from .config import PLAN_MODEL, TIP_MODEL
from .gemini_client import ask
from .gemini_generator import PLAN_FORMAT


def update_workout_plan(current_plan: str, user_feedback: str) -> str:
    """Revise a plan using the user's feedback. Untouched days stay as they were."""
    prompt = f"""You are a professional fitness trainer assistant.

Current 7-day plan (JSON):
{current_plan}

User feedback:
"{user_feedback}"

Revise the parts of the plan the feedback affects. Keep every other day unchanged.

{PLAN_FORMAT}"""
    return ask(prompt, PLAN_MODEL, fallback=TIP_MODEL, json_mode=True)
