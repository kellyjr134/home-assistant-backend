from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

buttons = []

class Button(BaseModel):
    x: float
    y: float
    label: str

@app.get("/buttons")
def get_buttons():
    return buttons

@app.post("/buttons")
def save_buttons(new_buttons: List[Button]):
    global buttons
    buttons = new_buttons
    return {"status": "saved"}

@app.post("/toggle")
def toggle_device(label: str):
    print(f"Toggling device: {label}")
    return {"status": f"Toggled {label}"}

@app.get("/calendar")
def get_calendar():
    return {
        "events": [
            {"summary": "Dentist Appointment", "time": "10:00 AM"},
            {"summary": "Team Meeting", "time": "2:00 PM"}
        ]
    }
