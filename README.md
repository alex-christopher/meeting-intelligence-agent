# Meeting Intelligence Agent

A Streamlit prototype that reads upcoming Google Calendar meetings, uses an LLM extraction agent to identify the external company/contact, and generates live meeting intelligence briefs using Tavily search plus OpenAI/LangChain structured output.

## What It Does

- Fetches upcoming meetings from Google Calendar.
- Extracts company name, company domain, primary contact, and external attendees from calendar event context.
- Uses Tavily live web search to gather public company signals.
- Uses OpenAI through LangChain to synthesize structured briefs:
  - company summary
  - recent activity
  - tech signals
  - inferred pain points
  - suggested talking points
  - source URLs
- Displays everything in a Streamlit dashboard.

## Tech Stack

- Python
- Streamlit
- Google Calendar API
- OpenAI
- LangChain
- Tavily
- Pydantic

## Setup

### 1. Clone and Install

```powershell
git clone https://github.com/alex-christopher/meeting-intelligence-agent.git
cd meeting-intelligence-agent

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Required API Keys

You need:

- OpenAI API key
- Tavily API key
- Google Calendar access through either:
  - recommended: Google service account
  - optional local fallback: Google OAuth desktop credentials

## Recommended Calendar Setup: Google Service Account

This is the recommended setup for both local testing and Streamlit Cloud deployment.

### 1. Enable Google Calendar API

1. Open Google Cloud Console.
2. Create or select a project.
3. Go to **APIs & Services > Library**.
4. Enable **Google Calendar API**.

### 2. Create a Service Account

1. Go to **IAM & Admin > Service Accounts**.
2. Click **Create service account**.
3. Give it a name such as `meeting-intelligence-agent`.
4. Finish creation.

### 3. Create a JSON Key

1. Open the service account.
2. Go to **Keys**.
3. Click **Add key > Create new key**.
4. Choose **JSON**.
5. Download the file.

Do not commit this JSON file to GitHub.

### 4. Share Your Calendar With the Service Account

Open the downloaded JSON and copy `client_email`.

Then in Google Calendar:

1. Open calendar settings.
2. Select the calendar you want the app to read.
3. Go to **Share with specific people or groups**.
4. Add the service account `client_email`.
5. Give permission: **See all event details**.

### 5. Get the Calendar ID

In Google Calendar:

1. Open calendar settings.
2. Go to **Integrate calendar**.
3. Copy **Calendar ID**.

For a personal main calendar, this may look like:

```text
your-email@gmail.com
```

For a separate calendar, it may look like:

```text
abc123@group.calendar.google.com
```

Use this value as `GOOGLE_CALENDAR_ID`.

## Local Secrets

Create this file locally:

```text
.streamlit/secrets.toml
```

Paste:

```toml
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "gpt-4o-mini"

TAVILY_API_KEY = "your-tavily-api-key"

GOOGLE_CALENDAR_ID = "your-calendar-id"
CALENDAR_DAYS_AHEAD = "7"
DATABASE_PATH = "meeting_intelligence.db"

[GOOGLE_SERVICE_ACCOUNT]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
your-private-key-lines
-----END PRIVATE KEY-----
"""
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-cert-url"
universe_domain = "googleapis.com"
```

The service account fields come from the downloaded JSON key. Convert JSON to TOML manually or paste the values one by one.

Important private key conversion:

JSON:

```json
"private_key": "-----BEGIN PRIVATE KEY-----\nABC\nDEF\n-----END PRIVATE KEY-----\n"
```

TOML:

```toml
private_key = """-----BEGIN PRIVATE KEY-----
ABC
DEF
-----END PRIVATE KEY-----
"""
```

## Optional Local OAuth Fallback

The app also supports local OAuth fallback if no service account is found.

Use this only for local development.

### 1. Create OAuth Client

1. Go to Google Cloud Console.
2. Enable Google Calendar API.
3. Go to **APIs & Services > OAuth consent screen**.
4. Add your Google account as a test user.
5. Go to **Credentials > Create Credentials > OAuth client ID**.
6. Choose **Desktop app**.
7. Download the JSON.
8. Rename it:

```text
credentials.json
```

9. Put it in the project root.

### 2. Create `.env`

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

TAVILY_API_KEY=your-tavily-api-key

GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_CALENDAR_ID=primary

DATABASE_PATH=meeting_intelligence.db
CALENDAR_DAYS_AHEAD=7
```

On first run, the app opens a browser for Google login and creates `token.json`.

Do not commit `.env`, `credentials.json`, or `token.json`.

## Run Locally

```powershell
streamlit run streamlit_app.py
```

The dashboard should show:

- sidebar status
- upcoming Google Calendar meetings
- extracted company details
- a button to generate research briefs

## Deploy on Streamlit Cloud

1. Push the repo to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repo.
4. Set main file path:

```text
streamlit_app.py
```

5. In **Advanced settings > Secrets**, paste the same TOML used in `.streamlit/secrets.toml`.
6. Deploy.

Do not upload or commit credential files. Streamlit Cloud should receive secrets only through its Secrets UI.

## Expected Demo Flow

Create calendar events such as:

```text
Demo call with Linear
Attendee: john@linear.app
```

```text
Intro call with Priya
Attendee: priya@growthsignal.io
```

Then open the dashboard:

1. The app fetches upcoming calendar events.
2. The extraction agent identifies the company/contact.
3. Click **Generate research brief**.
4. The research agent searches live web sources and synthesizes the meeting brief.

## Environment Variables

| Name | Required | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | OpenAI API key for extraction and synthesis |
| `OPENAI_MODEL` | Yes | Model name, usually `gpt-4o-mini` |
| `TAVILY_API_KEY` | Yes | Tavily API key for live web research |
| `GOOGLE_CALENDAR_ID` | Yes | Calendar ID to fetch events from |
| `CALENDAR_DAYS_AHEAD` | No | Number of future days to fetch, default `7` |
| `DATABASE_PATH` | No | Reserved for future SQLite persistence |
| `GOOGLE_CREDENTIALS_FILE` | OAuth only | Local OAuth credentials file |
| `GOOGLE_TOKEN_FILE` | OAuth only | Local OAuth token cache |
| `GOOGLE_SERVICE_ACCOUNT` | Service account | TOML section containing service account fields |

## Security Notes

Never commit:

```text
.env
.streamlit/secrets.toml
credentials.json
token.json
service-account.json
cerd.json
```

If any key or service account JSON is committed or pasted publicly, revoke it and create a new key.

