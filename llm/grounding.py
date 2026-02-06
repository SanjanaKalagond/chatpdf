from typing import List
from .prompts import REFUSAL_TEXT


STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "to", "of", "in", "on",
    "for", "with", "this", "that", "it", "as", "are", "was",
}


def is_answer_grounded(
    *,
    answer: str,
    citations: List[dict],
    min_overlap: int = 1,
) -> bool:
    """
    Grounding heuristic:
    Answer must share at least `min_overlap` non-stopword tokens
    with at least one cited chunk.
    """

    answer_tokens = {
        word
        for word in answer.lower().split()
        if word not in STOPWORDS
    }

    if not answer_tokens:
        return False

    for chunk in citations:
        chunk_tokens = {
            word
            for word in chunk["chunk_text"].lower().split()
            if word not in STOPWORDS
        }

        overlap = answer_tokens.intersection(chunk_tokens)

        if len(overlap) >= min_overlap:
            return True

    return False


def enforce_grounding(
    *,
    answer: str,
    citations: List[dict],
) -> str:
    if not citations:
        return REFUSAL_TEXT

    if not is_answer_grounded(answer=answer, citations=citations):
        return REFUSAL_TEXT

    return answer
