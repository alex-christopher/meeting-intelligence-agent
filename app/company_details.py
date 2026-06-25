from pydantic import BaseModel, Field

from app.config import Settings
from app.llm_client import get_chat_model

settings = Settings()

PERSONAL_EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "outlook.com",
]

class CompanyDetails(BaseModel):
    company_name: str | None = Field(description="Inferred company name, or null")
    company_domain: str | None = Field(description="Inferred company domain, or null")
    primary_contact_name: str | None = Field(description="Likely external contact name")
    external_attendees: list[str] = Field(description="Non-personal attendee emails")
    should_research: bool = Field(description="Whether enough company signal exists to research")
    confidence: float = Field(description="Confidence from 0 to 1")
    reason: str = Field(description="Short explanation")

def is_external_email(email: str) -> bool:
    if "@" not in email:
        return False

    domain = email.split("@", 1)[1].strip().lower()

    return domain not in PERSONAL_EMAIL_DOMAINS

def extract_company_details(
        title: str,
        attendees: list[str],
        description: str | None = None
) -> CompanyDetails:
    
    llm = get_chat_model(temperature=0)
    structured_llm = llm.with_structured_output(CompanyDetails)

    prompt = f"""
        You are a calendar intelligence extraction agent.

        Your job:
        Infer the external company, company domain, primary contact, and whether this meeting should be researched.

        Rules:
        - Use the meeting title, description, and attendee emails.
        - Treat these as personal email domains: {PERSONAL_EMAIL_DOMAINS}
        - If only personal email domains are present and the company is not clear from the title/description, set should_research=false.
        - Do not invent a company.
        - If an external business email domain exists, use it as strong evidence.
        - Return conservative confidence from 0 to 1.

        Meeting title:
        {title}

        Meeting description:
        {description or ""}

        Attendees:
        {attendees}
    """

    details = structured_llm.invoke(prompt)

    # details.external_attendees = [
    #     email
    #     for email in attendees
    #     if is_external_email(email)
    # ]

    return details

