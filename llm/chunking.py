from typing import List, Dict

def chunk_text(
    text: str,
    *,
    max_chars: int = 2500,
    overlap: int = 400,
) -> List[Dict]:

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