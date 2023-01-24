"""The core MR Fat Controller server."""
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class StatusModel(BaseModel):
    """Model for the status response."""

    ready: bool
    """Whether the server is ready."""


@app.get('/status', response_model=StatusModel)
def status() -> dict:
    """Return the current server status."""
    return {'ready': True}
