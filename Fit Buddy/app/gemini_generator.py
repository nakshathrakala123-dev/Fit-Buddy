import json

from .config import PLAN_MODEL, TIP_MODEL
from .gemini_client import ask

PLAN_FORMAT = """Reply with JSON only, in exactly this shape:
{"title": "short plan title",
 "summary": "two sentences on how the week is built",
 "days": [{"day": 1, "focus": "e.g. Upper body push",
           "type": "strength, cardio, mobility or rest",
           "warmup": "5-10 minute warm-up (empty on rest days)",
           "exercises": [{"name": "Goblet squat", "detail": "3 x 10-12, rest 60s"}],
           "cooldown": "cooldown or recovery tip"}],
 "notes": ["2-4 short safety and progression notes"]}
Exactly 7 days, numbered 1 to 7. Rest days use type "rest" with light recovery work as exercises."""


def parse_plan(text):
    """Turn stored plan text into a dict, or None if it is not valid plan JSON."""
    if not text:
        return None
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(cleaned)
    except ValueError:
        return None
    return data if isinstance(data, dict) and isinstance(data.get("days"), list) else None


def generate_workout_gemini(user_input):
    prompt = f"""You are a professional fitness trainer.
Create a personalized, structured 7-day workout plan for a {user_input['age']}-year-old weighing {user_input['weight']} kg.
Goal: {user_input['goal']}. Preferred intensity: {user_input['intensity']}.
Each training day needs a warm-up, a main workout with sets and reps, and a cooldown or recovery tip.

{PLAN_FORMAT}"""
    return ask(prompt, PLAN_MODEL, fallback=TIP_MODEL, json_mode=True)
