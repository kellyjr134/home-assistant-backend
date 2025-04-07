from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import requests
from urllib.parse import urlencode

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use environment variables from Render
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://your-backend-url.onrender.com/callback"

buttons = []

class Button(BaseModel):
    x: float
    y: float
    label: str

@app.get("/")
def read_root():
    return {"status": "Backend is live"}

@app.get("/auth")
def auth():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar.readonly",
        "access_type": "offline",
        "prompt": "consent"
    }
    return Response(status_code=302, headers={"Location": "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)})

@app.get("/callback")
def callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed")
    token = r.json()
    access_token = token.get("access_token")
    content = f"""
    <script>
      localStorage.setItem('access_token', '{access_token}');
      window.location.href = '/';
    </script>
    """
    return Response(content=content, media_type="text/html")

@app.get("/calendar")
def get_calendar(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = auth.split(" ")[1]
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch calendar events")
    items = r.json().get("items", [])
    events = [{"summary": e.get("summary"), "time": e.get("start", {}).get("dateTime", "N/A")} for e in items]
    return {"events": events}

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
