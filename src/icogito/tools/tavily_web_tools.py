from tavily import AsyncTavilyClient
from pydantic_ai import ModelRetry, RunContext
from icogito.models import ResearchState
from dotenv import load_dotenv
from loguru import logger
from typing import Any, Literal
import os

load_dotenv()


def get_tavily_client() -> AsyncTavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("TAVILY_API_KEY is missing!")
        raise ValueError("TAVILY_API_KEY is missing! Check your .env file.")
    return AsyncTavilyClient(api_key=api_key)


BLOCKED_MESSAGE = (
    "This URL is blocked by a paywall or anti-bot system. DO NOT retry "
    "fetching this URL. Proceed with the draft using only the available "
    "search context."
)

async def web_search(
        search: str,
        topic: Literal['general', 'news', 'finance'] = "news",
        days: int = 7
) -> dict:
    """Performs a web search specifically for recent news using Tavily"""
    logger.info(f"Web search looking for {search}")
    tavily_client = get_tavily_client()
    search_response = await tavily_client.search(
        query=search,
        topic=topic,
        days=days,
        max_results=20
    )
    if search_response is None:
        logger.warning("Tavily found nothing or got blocked")
        raise ModelRetry(BLOCKED_MESSAGE)
    return search_response

async def web_fetch(ctx: RunContext[ResearchState], urls: str | list[str]) -> dict[str, Any]:
    """Performs a web fetch using Tavily"""
    for url in urls:
        if url in ctx.deps.visited_urls:
            return {"error": "URL already processed. Stop fetching this URL and synthesize."}
        ctx.deps.visited_urls.add(url)
    logger.info(f"Extracting from {urls}")
    tavily_client = get_tavily_client()
    response = await tavily_client.extract(
        urls=urls,
        extract_depth="advanced",
        format="markdown"
    )
    if not response or "cloudflare" in str(response).lower():
        logger.warning("Tavily found nothing or got blocked")
        raise ModelRetry(BLOCKED_MESSAGE)
    return response


async def web_crawl(url: str, instructions: str) -> dict[str, Any]:
    """Performs a smart web crawling using Tavily"""
    logger.info(f"Crawling: {url}")
    tavily_client = get_tavily_client()
    response = await tavily_client.crawl(url, instructions=instructions)
    if not response:
        logger.warning("Tavily found nothing or got blocked")
        raise ModelRetry(BLOCKED_MESSAGE)
    return response
