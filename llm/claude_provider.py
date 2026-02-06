import os
from langchain_anthropic import ChatAnthropic

def get_haiku_llm():
    """
    Returns Claude 3.5 Haiku.
    The cheapest and fastest model in the Claude family.
    """
    # Ensure your ANTHROPIC_API_KEY is set in your environment
    return ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,  # Best for RAG to keep answers factual
        max_tokens=1024,
    )