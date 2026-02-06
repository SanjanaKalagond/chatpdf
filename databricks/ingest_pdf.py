import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
import argparse
import pdfplumber
from llm.chunking import chunk_text
from llm.embeddings import DummyEmbeddingProvider
from llm.vectorstore import FAISSVectorStore

MAX_DOC_SIZE_CHARS = 500_000        
MAX_CHUNKS_PER_DOC = 200
FAISS_DIM = 5                       
INDEX_DIR = Path("vector_index")

def ingest_txt_file(
    *,
    file_path: Path,
    embedding_provider,
    vector_store,
    dry_run: bool,
):
    print(f"\n[INFO] Processing TXT: {file_path.name}")

    text = file_path.read_text(encoding="utf-8")

    if len(text) > MAX_DOC_SIZE_CHARS:
        print(f"[WARN] Skipping {file_path.name} (too large)")
        return

    chunks = chunk_text(text)[:MAX_CHUNKS_PER_DOC]

    if not chunks:
        print("[WARN] No chunks produced")
        return

    texts = [c["chunk_text"] for c in chunks]
    embeddings = embedding_provider.embed(texts)

    if dry_run:
        print(f"[DRY-RUN] Would index {len(chunks)} TXT chunks")
        return

    vector_store.add(
        embeddings=embeddings,
        metadatas=chunks,
    )

def extract_text_from_pdf(file_path: Path) -> str:
    text_parts = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        print(f"[WARN] Failed to read PDF {file_path.name}: {e}")
        return ""

    return "\n".join(text_parts)


def ingest_pdf_file(
    *,
    file_path: Path,
    embedding_provider,
    vector_store,
    dry_run: bool,
):
    print(f"\n[INFO] Processing PDF: {file_path.name}")

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        print("[WARN] No text extracted from PDF")
        return

    if len(text) > MAX_DOC_SIZE_CHARS:
        print(f"[WARN] Skipping {file_path.name} (too large)")
        return

    chunks = chunk_text(text)[:MAX_CHUNKS_PER_DOC]

    if not chunks:
        print("[WARN] No chunks produced from PDF")
        return

    texts = [c["chunk_text"] for c in chunks]
    embeddings = embedding_provider.embed(texts)

    if dry_run:
        print(f"[DRY-RUN] Would index {len(chunks)} PDF chunks")
        return

    vector_store.add(
        embeddings=embeddings,
        metadatas=chunks,
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing FAISS index",
    )

    args = parser.parse_args()

    embedding_provider = DummyEmbeddingProvider()
    vector_store = FAISSVectorStore(dim=FAISS_DIM)

    txt_dir = Path("data/txt")
    txt_files = list(txt_dir.glob("*.txt")) if txt_dir.exists() else []

    if txt_files:
        print(f"[INFO] Found {len(txt_files)} TXT files")

    for file_path in txt_files:
        ingest_txt_file(
            file_path=file_path,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            dry_run=args.dry_run,
        )

    pdf_dir = Path("data/pdf")
    pdf_files = list(pdf_dir.glob("*.pdf")) if pdf_dir.exists() else []

    if pdf_files:
        print(f"\n[INFO] Found {len(pdf_files)} PDF files")

    for file_path in pdf_files:
        ingest_pdf_file(
            file_path=file_path,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            dry_run=args.dry_run,
        )

    if args.dry_run:
        print("\n[DRY-RUN] Ingestion complete — no data written")
        return

    INDEX_DIR.mkdir(exist_ok=True)

    vector_store.save(
        index_path=INDEX_DIR / "index.faiss",
        metadata_path=INDEX_DIR / "metadata.json",
    )

    print("\n[INFO] FAISS index written to disk")


if __name__ == "__main__":
    main()
