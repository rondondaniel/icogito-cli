from pydantic import BaseModel, Field

class Findings(BaseModel):
    title: str = Field(
        ...,
        min_length=10,
        max_length=150,
        description=(
            "The headline of the news item found via web search. "
            "Must be concise, factual, and specific enough to identify the story independently."
        ),
        examples=["Google releases Gemini 1.5 Pro with 1M token context window"]
    )
    summary: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description=(
            "A factual, self-contained summary of the news item's key points. "
            "Must contain enough detail for a downstream agent to draft a complete article "
            "without re-fetching the original source."
        ),
        examples=[
            "Google has introduced Gemini 1.5 Pro, featuring a novel Mixture-of-Experts (MoE) architecture "
            "and an unprecedented context window of up to 1 million tokens, enabling the model to process "
            "vast amounts of text, video, and audio simultaneously."
        ]
    )
    url: str = Field(
        ...,
        description=(
            "Source URL of the news item. "
            "Must be kept as-is to allow downstream rewriting agents to cite it as a verified reference."
        ),
        pattern=r"^https?://",
        examples=["https://blog.google/technology/ai/google-gemini-next-generation-model-update/"]
    )

class TopicNewsBatch(BaseModel):
    news: list[Findings] = Field(
        ...,
        min_length=1,
        max_length=15,
        description=(
            "A curated list of 5 to 15 news items discovered during the web search phase about the requested topic. "
            "Each item must contain a clear title, a detailed summary, and a valid source URL."
        )
    )