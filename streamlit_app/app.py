import os
import sys
<<<<<<< Updated upstream
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

=======
import requests
from urllib.parse import urljoin
from pathlib import Path

import streamlit as st
import pandas as pd
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm.prompts import REFUSAL_TEXT

DJANGO_BASE = "https://zany-cod-9774rx9q96qr297v5-8000.app.github.dev/"
API_KEY = "dev-streamlit-key"

def django_post(path, *, files=None, json=None):
    url = urljoin(DJANGO_BASE, path.lstrip("/"))
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.post(url, files=files, json=json, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
st.set_page_config(page_title="ChatPDF", layout="wide")
=======
def extract_llm_text(response):
    if hasattr(response, "content"):
        if isinstance(response.content, list):
            return response.content[0].get("text", "")
        return response.content
    return str(response)

st.set_page_config(page_title="ChatPDF", layout="wide")
st.title("ChatPDF")

for key, default in {
    "chat_history": [],
    "csv_df": None,
    "document_id": None,
    "last_uploaded_name": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default
>>>>>>> Stashed changes

st.title("ChatPDF")
with st.sidebar:
<<<<<<< Updated upstream
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
=======
    api_key = (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or st.text_input("Google / Gemini API Key", type="password")
    )

uploaded_file = st.file_uploader(
    "Upload a document",
    type=["txt", "pdf", "csv"],
)

if uploaded_file:
    if st.session_state.last_uploaded_name != uploaded_file.name:
        st.session_state.last_uploaded_name = uploaded_file.name
        st.session_state.chat_history = []
        st.session_state.csv_df = None
        st.session_state.document_id = None

if uploaded_file and uploaded_file.name.lower().endswith(".csv"):
    if st.session_state.csv_df is None:
        st.session_state.csv_df = pd.read_csv(uploaded_file)

    df = st.session_state.csv_df

    st.dataframe(df.head())
    st.write(df.shape)
    st.write(df.dtypes)
    st.write(df.isnull().sum())
    st.dataframe(df.describe())

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        st.bar_chart(df[numeric_cols].mean())

    for turn in st.session_state.chat_history:
        st.markdown(f"**You:** {turn['question']}")
        st.markdown(f"**ChatPDF:** {turn['answer']}")
        st.markdown("---")

    with st.form("csv_chat_form", clear_on_submit=True):
        question = st.text_area("", height=80)
        submitted = st.form_submit_button("Send")

    if submitted and question and api_key:
        llm = get_gemini_llm(api_key)
        prompt = f"""
Columns: {list(df.columns)}
Shape: {df.shape}

Summary:
{df.describe().to_string()}

Question:
{question}
"""
        response = llm.invoke(prompt)
        answer = extract_llm_text(response)
        st.session_state.chat_history.append(
            {"question": question, "answer": answer}
        )
        st.success(answer)

elif uploaded_file:
    if st.session_state.document_id is None:
        result = django_post(
            "/api/documents/upload/",
            files={"file": (uploaded_file.name, uploaded_file.getvalue())},
        )
        st.session_state.document_id = result["document_id"]
        st.success(f"Uploaded document {st.session_state.document_id}")

    for turn in st.session_state.chat_history:
        st.markdown(f"**You:** {turn['question']}")
        if turn["answer"] == REFUSAL_TEXT:
            st.warning(turn["answer"])
>>>>>>> Stashed changes
        else:
            st.warning("Enter your Gemini API key to continue")

uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])
question = st.text_input("Ask Gemini a question about the content")

<<<<<<< Updated upstream
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
=======
    if submitted and question:
        result = django_post(
            f"/api/documents/{st.session_state.document_id}/query/",
            json={"question": question},
        )
        answer = result["answer"]
        st.session_state.chat_history.append(
            {"question": question, "answer": answer}
        )
        if answer == REFUSAL_TEXT:
            st.warning(answer)
        else:
            st.success(answer)
>>>>>>> Stashed changes
