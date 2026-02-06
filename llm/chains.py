# NEW (Correct for 2026)
from langchain_core.prompts import ChatPromptTemplate
# NEW (Correct for 2026)
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from .prompts import SYSTEM_PROMPT, REFUSAL_TEXT


def build_rag_chain(llm):
    """
    Build a RAG chain that works with:
    - Real LangChain LLMs
    - Dummy/test LLMs
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
        ]
    )

    # ---- ADAPTER LAYER (CRITICAL FIX) ----
    if hasattr(llm, "invoke"):
        # Wrap non-LangChain LLMs into a Runnable
        llm_runnable = RunnableLambda(
            lambda x: llm.invoke(x)
        )
    else:
        llm_runnable = llm

    chain = (
        prompt
        | llm_runnable
        | StrOutputParser()
    )

    return chain


def postprocess_answer(answer: str, context: str) -> str:
    if not context.strip():
        return REFUSAL_TEXT
    return answer
