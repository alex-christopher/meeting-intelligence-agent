from pydantic import BaseModel, Field
from tavily import TavilyClient

from app.config import get_settings
from app.llm_client import get_chat_model
from app.company_details import extract_company_details


def direct_llm_call(meeting_title, attendees):

    llm = get_chat_model(temperature=0.8)
    prompt = f"""
                You need to provide a brief summary with the help pf the details that are provided from Meeting title and attendees : {meeting_title, attendees}
    """
    
    llm_out = llm.invoke(prompt)
    return llm_out

class SearchSource(BaseModel):
    title: str
    url: str
    content: str

class ResearchBrief(BaseModel):
    company_summary: str = Field(description="Plain-language company summary")
    recent_activity: list[str] = Field(description="Recent news, funding, product launches, or announcements")
    tech_signals: list[str] = Field(description="Technology, stack, infrastructure, hiring, or open-source signals")
    pain_points: list[str] = Field(description="Inferred business or operational pain points")
    talking_points: list[str] = Field(description="Suggested talking points for the meeting")
    sources: list[str] = Field(description="Source URLs used")



def run_company_research(
        company_name: str,
        company_domain: str | None = None,
        meeting_title: str | None = None,
        attendees: list[str] | None = None
) -> ResearchBrief:
    
    settings = get_settings()

    if not settings.tavily_api_key:
        raise ValueError("TAVILY API KEY is missing")
    
    tavily = TavilyClient(api_key=settings.tavily_api_key)

    queries = build_research_queries(
        company_name=company_name,
        company_domain=company_domain
    )

    sources = search_sources(tavily, queries)

    llm = get_chat_model(temperature=0.2)
    structured_llm = llm.with_structured_output(ResearchBrief)

    prompt = f"""
        You are a meeting intelligence research agent.

        Create a concise pre-meeting intelligence brief for an upcoming external call.

        Company:
        {company_name}

        Company domain:
        {company_domain or "Unknown"}

        Meeting title:
        {meeting_title or "Unknown"}

        Attendees:
        {attendees or []}

        Research sources:
        {[source.model_dump() for source in sources]}

        Instructions:
        - Use the sources to synthesize, not copy.
        - Write in plain language.
        - Include recent activity only if supported by sources.
        - Infer pain points from company stage, market, product, hiring, or public activity.
        - Include practical talking points a salesperson/account manager could use.
        - Do not invent specific funding/news dates unless source evidence supports them.
        - If evidence is weak, say so honestly.
        - Return source URLs in the sources field.
        """
    
    brief = structured_llm.invoke(prompt)

    source_urls = []

    for source in sources:
        if source.url not in source_urls:
            source_urls.append(source.url)
    
    brief.sources = source_urls[:6]

    return brief

def build_research_queries(company_name: str,
                           company_domain: str | None = None,
                           ) -> list[str]:
    
    queries = [
        f'{company_name} company what it do',
        f'{company_name} recent news funding product launch',
        f'{company_name} jobs engineering tech stack'
    ]

    if company_domain:
        queries.append(f"site:{company_domain} about company product")
        queries.append(f"{company_domain} technology stack engineering")

    return queries

def search_sources(tavily: TavilyClient,
                   queries: list[str],
                   ) -> list[SearchSource]:
    

    collected: list[SearchSource] = []
    seen_urls: set[str] = set()

    for query in queries:
        response = tavily.search(
            query=query,
            search_depth="advanced",
            max_results=3,
            include_answer=False
        )

        for result in response.get("results", []):
            url = result.get("url")

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)

            collected.append(
                SearchSource(
                    title=result.get("title", ""),
                    url=url,
                    content=result.get("content", "")
                )
            )

    return collected[:8]