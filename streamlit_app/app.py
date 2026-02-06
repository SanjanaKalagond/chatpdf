import os
import sys
import django
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatpdf_backend.settings")
django.setup()


import streamlit as st
from pypdf import PdfReader 
from langchain_google_genai import ChatGoogleGenerativeAI # pip install langchain-google-genai
from llm.embeddings import DummyEmbeddingProvider
from llm.vectorstore import InMemoryVectorStore
from llm.retrieval import retrieve_context
from llm.graph import build_qa_graph
from llm.prompts import REFUSAL_TEXT

def extract_text(file):
    """Handles both PDF and TXT extraction."""
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    else:
        return file.read().decode("utf-8", errors="ignore")

def get_gemini_llm(api_key):
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview", 
        google_api_key=api_key,
        temperature=0,
    )

st.set_page_config(page_title="ChatPDF", layout="wide")

st.title("ChatPDF")
with st.sidebar:
    st.header("Settings")
    env_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if env_key:
        api_key = env_key
        st.success("Key loaded from environment")
    else:
        api_key = st.text_input("Google/Gemini API Key", type="password")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            st.success("Key loaded manually")
        else:
            st.warning("Enter your Gemini API key to continue")

uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])
question = st.text_input("Ask Gemini a question about the content")

if uploaded_file and question and api_key:
    with st.spinner("Gemini is reading your document..."):
        document_text = extract_text(uploaded_file)

        if not document_text.strip():
            st.error("No text found. PDF might be image-only.")
            st.stop()

        context, citations = retrieve_context(
            document_text=document_text,
            question=question,
            embedding_provider=DummyEmbeddingProvider(),
            vector_store=InMemoryVectorStore(),
        )

        llm = get_gemini_llm(api_key)
        graph = build_qa_graph(llm)

        result = graph.invoke({
            "question": question,
            "context": context,
            "citations": citations,
            "answer": None,
            "error": None,
            "tokens_used": None,
        })

    st.divider()
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Answer")
        if result["answer"] == REFUSAL_TEXT:
            st.warning(result["answer"])
        else:
            st.success("Grounded Answer Generated")
            st.write(result["answer"])

    with col2:
        st.subheader("Source References")
        if citations:
            for idx, cite in enumerate(citations):
                with st.expander(f"Reference {idx + 1}"):
                    st.write(cite.get("chunk_text", "No preview available"))
        else:
            st.info("No sources returned")

    with st.expander("Raw Retrieved Context (Debug)"):
        st.text(context)