from .config import TIP_MODEL
from .gemini_client import ask


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """One short nutrition or recovery tip for the user's goal, from the fast model."""
    prompt = (
        f"Give one clear, practical nutrition or recovery tip for someone whose goal is '{goal}'. "
        "Friendly, plain text, two sentences at most."
    )
    return ask(prompt, TIP_MODEL)
