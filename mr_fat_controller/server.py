"""The core MR Fat Controller server."""
from fastapi import FastAPI

from . import api


app = FastAPI()
app.include_router(api.router)
