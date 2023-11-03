"""The core MR Fat Controller server."""
from fastapi import FastAPI

from mr_fat_controller import api

app = FastAPI()
app.include_router(api.router)
