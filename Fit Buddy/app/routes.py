from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from .config import TEMPLATE_DIR
from .database import (delete_user, get_all_users, get_plan, get_user,
                       save_plan, save_user, update_plan)
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini, parse_plan
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)


def show_form(request, form=None, error=None, status=200):
    return templates.TemplateResponse(request, "index.html", {"form": form or {}, "error": error}, status_code=status)


def show_result(request, user_id, message=None, error=None):
    user, plan = get_user(user_id), get_plan(user_id)
    if not user or not plan:
        return show_form(request, error="No plan found for that user ID. Create one first.", status=404)
    current = plan.updated_plan or plan.original_plan
    return templates.TemplateResponse(request, "result.html", {
        "user": user,
        "tip": plan.nutrition_tip,
        "plan": parse_plan(current),
        "raw": current,
        "has_update": bool(plan.updated_plan),
        "original": parse_plan(plan.original_plan),
        "original_raw": plan.original_plan,
        "message": message,
        "error": error,
    })


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return show_form(request)


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(request: Request, username: str = Form(...), user_id: str = Form(...),
                     age: str = Form(...), weight: str = Form(...), goal: str = Form(...),
                     intensity: str = Form(...)):
    form = {"username": username, "user_id": user_id, "age": age, "weight": weight,
            "goal": goal, "intensity": intensity}
    try:
        data = UserInput(username=username.strip(), user_id=user_id, age=age, weight=weight,
                         goal=goal.strip(), intensity=intensity.lower())
    except ValidationError as err:
        fields = ", ".join(dict.fromkeys(str(e["loc"][0]) for e in err.errors()))
        return show_form(request, form, f"Check these fields: {fields}.", status=422)
    try:
        plan = generate_workout_gemini({"age": data.age, "weight": data.weight,
                                        "goal": data.goal, "intensity": data.intensity})
        tip = generate_nutrition_tip_with_flash(data.goal)
    except Exception as exc:
        return show_form(request, form, str(exc), status=502)
    save_user(data.user_id, data.username, data.age, data.weight, data.goal, data.intensity)
    save_plan(data.user_id, plan, tip)
    return show_result(request, data.user_id)


@router.get("/plan/{user_id}", response_class=HTMLResponse)
def view_plan(request: Request, user_id: int):
    return show_result(request, user_id)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: int = Form(...), feedback: str = Form(...)):
    user, plan = get_user(user_id), get_plan(user_id)
    if not user or not plan:
        return show_result(request, user_id)
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback.strip())
    except ValidationError:
        return show_result(request, user_id, error="Write a few words about what to change (3 to 500 characters).")
    try:
        revised = update_workout_plan(plan.updated_plan or plan.original_plan, data.feedback)
        tip = generate_nutrition_tip_with_flash(user.goal)
    except Exception as exc:
        return show_result(request, user_id, error=str(exc))
    update_plan(user_id, revised, tip)
    return show_result(request, user_id, message="Your plan has been updated based on your feedback.")


@router.get("/nutrition-tip")
def nutrition_tip(goal: str):
    return {"goal": goal, "nutrition_tip": generate_nutrition_tip_with_flash(goal)}


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    rows = []
    for user in get_all_users():
        plan = user.plan
        rows.append({
            "user": user,
            "original": parse_plan(plan.original_plan) if plan else None,
            "original_raw": plan.original_plan if plan else "",
            "updated": parse_plan(plan.updated_plan) if plan and plan.updated_plan else None,
            "updated_raw": plan.updated_plan if plan else "",
            "has_update": bool(plan and plan.updated_plan),
        })
    return templates.TemplateResponse(request, "all_users.html", {"rows": rows})


@router.post("/delete-user/{user_id}")
def remove_user(user_id: int):
    delete_user(user_id)
    return RedirectResponse("/view-all-users", status_code=303)
