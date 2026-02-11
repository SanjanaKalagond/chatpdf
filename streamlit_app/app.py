import os
import sys
import django
import requests
import pandas as pd
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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


DJANGO_BASE_URL = "http://127.0.0.1:8000"
API_TOKEN = os.environ.get("STREAMLIT_API_KEY", "dev-streamlit-key")

st.set_page_config(page_title="ChatPDF + CSV", layout="wide")
st.title("ChatPDF")


for key, default in {
    "chat_history": [],
    "document_id": None,
    "csv_df": None,
    "last_file_name": None,
    "api_key": None,
    "provider": "gemini",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


with st.sidebar:
    st.header("Settings")

    provider = st.selectbox(
        "LLM Provider",
        ["gemini", "openai"],
        index=0 if st.session_state.provider == "gemini" else 1,
    )
    st.session_state.provider = provider

    api_key_input = st.text_input(
        f"{provider.upper()} API Key",
        type="password",
        value=st.session_state.api_key or "",
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success(f"{provider.upper()} API key loaded")

    if API_TOKEN:
        st.success("Connected to Django backend")
    else:
        st.warning("STREAMLIT_API_KEY not set")


def django_post(path, *, files=None, json=None):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "X-LLM-PROVIDER": st.session_state.provider,
        "X-LLM-API-KEY": st.session_state.api_key or "",
    }

    url = f"{DJANGO_BASE_URL}{path}"
    r = requests.post(url, headers=headers, files=files, json=json, timeout=60)

    if r.status_code not in (200, 201):
        try:
            error = r.json()
            st.error(error.get("error", "Unknown backend error"))
        except Exception:
            st.error(f"Backend error: {r.status_code}")
        st.stop()

    return r.json()


uploaded_file = st.file_uploader("Upload a document", type=["csv", "txt", "pdf"])

if uploaded_file:

    if uploaded_file.name != st.session_state.last_file_name:
        st.session_state.last_file_name = uploaded_file.name
        st.session_state.chat_history = []
        st.session_state.document_id = None
        st.session_state.csv_df = None

    if uploaded_file.name.lower().endswith(".csv"):

        if st.session_state.csv_df is None:
            st.session_state.csv_df = pd.read_csv(uploaded_file)

        df = st.session_state.csv_df

        st.subheader("CSV Preview")
        st.dataframe(df.head())

        col1, col2 = st.columns(2)
        with col1:
            st.write("Shape:", df.shape)
            st.write("Columns:", df.columns.tolist())
        with col2:
            st.dataframe(df.describe())

        for turn in st.session_state.chat_history:
            st.markdown(f"**You:** {turn['question']}")
            st.markdown(f"**ChatCSV:** {turn['answer']}")
            st.markdown("---")

        with st.form("csv_chat", clear_on_submit=True):
            question = st.text_area("Ask about the CSV", height=80)
            submitted = st.form_submit_button("Send")

        if submitted:
            question = question.strip()
            if not question:
                st.stop()

            if not st.session_state.api_key:
                st.error("Please enter an API key in the sidebar.")
                st.stop()

            # Provider-aware LLM (CSV stays frontend-only)
            if st.session_state.provider == "gemini":
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash-lite",
                    google_api_key=st.session_state.api_key,
                    temperature=0,
                )
            else:
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=st.session_state.api_key,
                    temperature=0,
                )

            prompt = f"""
Columns: {list(df.columns)}
Shape: {df.shape}
Summary:
{df.describe().to_string()}

Question: {question}
"""

            response = llm.invoke(prompt)
            answer = response.content

            st.session_state.chat_history.append(
                {"question": question, "answer": answer}
            )

            st.rerun()

    else:

        if st.session_state.document_id is None:
            with st.spinner("Uploading to Django..."):
                result = django_post(
                    "/api/documents/upload/",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                )
                st.session_state.document_id = result["document_id"]
                st.success(f"Uploaded document (ID {st.session_state.document_id})")

        for turn in st.session_state.chat_history:
            st.markdown(f"**You:** {turn['question']}")
            st.markdown(f"**ChatPDF:** {turn['answer']}")
            st.markdown("---")

        with st.form("doc_chat", clear_on_submit=True):
            question = st.text_area("Ask about the document", height=80)
            submitted = st.form_submit_button("Send")

        if submitted:
            question = question.strip()

            if not question:
                st.stop()

            if not st.session_state.api_key:
                st.error("Please enter an API key in the sidebar.")
                st.stop()

            result = django_post(
                f"/api/documents/{st.session_state.document_id}/query/",
                json={"question": question},
            )

            answer = result["answer"]

            st.session_state.chat_history.append(
                {"question": question, "answer": answer}
            )

            st.rerun()
