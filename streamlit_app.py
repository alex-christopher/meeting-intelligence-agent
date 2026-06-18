import streamlit as st

from app.config import get_settings


st.set_page_config(
    page_title="Meeting Intelligence Agent",
    page_icon="📅",
    layout="wide",
)

st.title("Meeting Intelligence Agent")
st.caption("Prototype dashboard for upcoming meeting briefs.")

settings = get_settings()

st.subheader("Configuration check")

st.write(
    {
        "openai_model": settings.openai_model,
        "google_credentials_file": settings.google_credentials_file,
        "google_token_file": settings.google_token_file,
        "database_path": settings.database_path,
        "calendar_days_ahead": settings.calendar_days_ahead,
        "openai_key_loaded": bool(settings.openai_api_key),
        "tavily_key_loaded": bool(settings.tavily_api_key),
    }
)