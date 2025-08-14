"""FastAPI application entry point."""
from fastapi import FastAPI
from .routers import schedules

app = FastAPI()
app.include_router(schedules.router)


@app.get("/")
def read_root():
    return {"message": "Shift maker API"}

