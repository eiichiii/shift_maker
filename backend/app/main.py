"""FastAPI application entry point."""
from fastapi import FastAPI
from .routers import schedules, members, availabilities, shift_generation

app = FastAPI()
app.include_router(schedules.router)
app.include_router(members.router)
app.include_router(availabilities.router)
app.include_router(shift_generation.router)


@app.get("/")
def read_root():
    return {"message": "Shift maker API"}

