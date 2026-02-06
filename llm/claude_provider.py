import os
from langchain_anthropic import ChatAnthropic

def get_haiku_llm():
    return ChatAnthropic(
        model="claude-3-5-haiku-20241022",
        temperature=0,  
        max_tokens=1024,
    )