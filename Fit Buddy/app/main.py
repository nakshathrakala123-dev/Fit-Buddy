from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR
from .database import init_db
from .routes import router

init_db()

app = FastAPI(title="FitBuddy")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)
