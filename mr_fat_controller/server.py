"""The core MR Fat Controller server."""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from mr_fat_controller import api

app = FastAPI()
app.include_router(api.router)
app.mount("/app", StaticFiles(packages=[("mr_fat_controller", "frontend/dist")], html=True), name="app")


@app.get("/", response_class=RedirectResponse)
def root() -> str:
    """Redirect to the frontend application."""
    return "/app"
