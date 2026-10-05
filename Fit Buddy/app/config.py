import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(ROOT_DIR, ".env"))

API_KEY = os.getenv("GOOGLE_API_KEY", "")
PLAN_MODEL = os.getenv("PLAN_MODEL", "gemini-3.1-pro-preview")
TIP_MODEL = os.getenv("TIP_MODEL", "gemini-3.6-flash")

DB_PATH = os.path.join(ROOT_DIR, "fitbuddy.db")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Tried in order when the main model is busy or rejects the request.
FALLBACK_MODELS = [m.strip() for m in os.getenv("FALLBACK_MODELS", "gemini-3.5-flash,gemini-3.1-flash-lite").split(",") if m.strip()]