from typing import List, Dict


def chunk_text(
    text: str,
    *,
    max_chars: int = 1200,
    overlap: int = 200,
) -> List[Dict]:
    """
    Deterministic text chunking with overlap.

    Returns a list of dicts:
    {
        "chunk_text": str,
        "chunk_index": int,
    }
    """
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]

        chunks.append(
            {
                "chunk_text": chunk,
                "chunk_index": index,
            }
        )

        index += 1
        start = end - overlap

    return chunks
