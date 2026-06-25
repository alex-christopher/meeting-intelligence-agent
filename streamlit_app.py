import streamlit as st
from streamlit_autorefresh import st_autorefresh

from app.config import get_settings
from app.calendar_client import fetch_events, normalize_events
from app.company_details import extract_company_details
from app.research_agent import run_company_research, direct_llm_call



st.set_page_config(
    page_title="Meeting Intelligence Agent",
    page_icon="calendar",
    layout="wide",
)

live_monitoring = st.sidebar.checkbox("Live Monitoring", value=False)

if live_monitoring:
    refresh_tick = st_autorefresh(interval=60_000, key="calendar_refresh")
else:
    refresh_tick = 0

st.title("Meeting Intelligence Agent")
st.caption("Prototype dashboard for upcoming meeting briefs.")

settings = get_settings()


@st.cache_data(show_spinner=False)
def load_meetings(refresh_tick: int):
    raw_events = fetch_events()
    return [normalize_events(event) for event in raw_events]


@st.cache_data(show_spinner=False)
def extract_details_cached(title: str, attendees: tuple[str, ...], description: str | None):
    return extract_company_details(
        title=title,
        attendees=list(attendees),
        description=description,
    )


with st.sidebar:
    st.header("Status")
    st.write(
        {
            "calendar_id": settings.google_calendar_id,
            "days_ahead": settings.calendar_days_ahead,
            "openai_key_loaded": bool(settings.openai_api_key),
            "tavily_key_loaded": bool(settings.tavily_api_key)
        }
    )

    refresh_clicked = st.button("Refresh now", use_container_width=True)
    if refresh_clicked:
        load_meetings.clear()

st.subheader("upcoming meetings")

try:
    meetings = load_meetings(refresh_tick)

    if not meetings:
        st.info("No upcoming meetings found for the calendar")

    for meeting in meetings:
        with st.container(border=True):
            st.markdown(f"### {meeting['title']}")
            st.write(f"**Start:** {meeting['start']}")
            st.write(f"**End:** {meeting['end']}")
            st.write("**Attendees:**")
            if meeting["attendees"]:
                for attendee in meeting["attendees"]:
                    st.write(f"- {attendee}")
            else:
                st.write("No attendees found.")

            if meeting["description"]:
                with st.expander("Description"):
                    st.write(meeting["description"])

            with st.spinner("Agent extracting company details..."):
                details = extract_details_cached(
                    title=meeting["title"],
                    attendees=tuple(meeting["attendees"]),
                    description=meeting["description"],
                )

            st.divider()

            if details.should_research:
                st.write(f"**Company:** {details.company_name}")
                st.write(f"**Domain:** {details.company_domain}")
                st.write(f"**Primary contact:** {details.primary_contact_name}")
                st.write(f"**External attendees:** {', '.join(details.external_attendees)}")
                st.write(f"**Confidence:** {details.confidence}")
                st.caption(details.reason)
                if st.button(
                    "Generate research brief",
                    key=f"research-{meeting['calendar_event_id']}",
                ):
                    with st.spinner("Research agent gathering live web signals..."):
                        # brief = run_company_research(
                        #     company_name=details.company_name,
                        #     company_domain=details.company_domain,
                        #     meeting_title=meeting["title"],
                        #     attendees=meeting["attendees"],
                        # )

                        brief = direct_llm_call(meeting_title=meeting["title"],
                                                attendees=meeting["attendees"])
                        st.write(brief)

                    # st.markdown("#### Company brief")
                    # st.write(brief.company_summary)

                    # st.markdown("#### Recent activity")
                    # for item in brief.recent_activity:
                    #     st.write(f"- {item}")

                    # st.markdown("#### Tech signals")
                    # for item in brief.tech_signals:
                    #     st.write(f"- {item}")

                    # st.markdown("#### Inferred pain points")
                    # for item in brief.pain_points:
                    #     st.write(f"- {item}")

                    # st.markdown("#### Talking points")
                    # for item in brief.talking_points:
                    #     st.write(f"- {item}")

                    # with st.expander("Sources"):
                    #     for source in brief.sources:
                    #         st.write(source)
            else:
                st.warning("Company could not be identified for this meeting.")
                st.caption(details.reason)

except Exception as exc:
    st.error("Could not fetch calendar events.")
    st.exception(exc)

# st.subheader("Configuration check")

# st.write(
#     {
#         "openai_model": settings.openai_model,
#         "google_credentials_file": settings.google_credentials_file,
#         "google_token_file": settings.google_token_file,
#         "database_path": settings.database_path,
#         "calendar_days_ahead": settings.calendar_days_ahead,
#         "openai_key_loaded": bool(settings.openai_api_key),
#         "tavily_key_loaded": bool(settings.tavily_api_key),
#     }
# )
