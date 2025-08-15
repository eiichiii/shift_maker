"""FastAPI application entry point."""
from fastapi import FastAPI
from .routers import schedules, members

app = FastAPI()
app.include_router(schedules.router)
app.include_router(members.router)


@app.get("/")
def read_root():
    return {"message": "Shift maker API"}

