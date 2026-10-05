# FitBuddy

FastAPI + Gemini workout planner with SQLite storage.

## Run (Windows)
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env      (then paste your key into .env)
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000 (API docs at /docs, admin at /view-all-users).
Get a key at https://aistudio.google.com/apikey

If a model name is rejected, change PLAN_MODEL / TIP_MODEL in .env.
