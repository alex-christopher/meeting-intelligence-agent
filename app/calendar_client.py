from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import os
import json

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import get_settings

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_service_account_info() -> dict[str, Any] | None:
    try:
        import streamlit as st

        if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
            return dict(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
        
    except Exception:
        pass

    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw_json:
        return json.loads(raw_json)
    
    return None

def get_calendar():
    settings = get_settings()

    service_account_info = get_service_account_info()

    if service_account_info:
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
        return build("calendar", "v3", credentials=creds)

    credentials_path = Path(settings.google_credentials_file)
    token_path = Path(settings.google_token_file)

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                SCOPES
            )

            creds = flow.run_local_server(
                host="localhost",
                port=8080,
                authorization_prompt_message="Please visit this URL : {url}",
                success_message="Authentication complete. You can close the window",
                open_browser=True
            )

        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("calendar", "v3", credentials=creds)



def fetch_events(days_ahead: int | None = None) -> list[dict[str, Any]]:
    settings = get_settings()
    service = get_calendar()

    days = days_ahead or settings.calendar_days_ahead

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)

    events = (
        service.events().list(
            calendarId = settings.google_calendar_id,
            timeMin = now.isoformat(),
            timeMax = end.isoformat(),
            singleEvents = True,
            orderBy = "startTime"
        ).execute()
    )

    return events.get("items", [])

def normalize_events(event: dict[str, Any]) -> dict[str, Any]:
    attendees = [
        attendee.get("email", "")
        for attendee in event.get("attendees", [])
        if attendee.get("email")
    ]

    start = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
    end = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")

    return {
        "calendar_event_id": event["id"],
        "title": event.get("summary", "Untitled meeting"),
        "start": start,
        "end": end,
        "description": event.get("description", ""),
        "attendees": attendees
    }

if __name__ == "__main__":
    events = fetch_events()
    for event in events:
        print(normalize_events(event))