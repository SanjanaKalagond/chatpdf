from typing import List
from .prompts import REFUSAL_TEXT

def enforce_grounding(
    *,
    answer: str,
    citations: List[dict],
) -> str:
    if not citations:
        return REFUSAL_TEXT

    if not answer or not answer.strip():
        return REFUSAL_TEXT

    return answer
