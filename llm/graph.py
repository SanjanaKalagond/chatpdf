from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END

from .chains import build_rag_chain, postprocess_answer
from .prompts import REFUSAL_TEXT
from .tokens import count_tokens
from .grounding import enforce_grounding


class QAState(TypedDict):
    question: str
    context: str
    citations: List[dict]
    answer: Optional[str]
    error: Optional[str]
    tokens_used: Optional[int]


def build_qa_graph(llm):
    graph = StateGraph(QAState)

    def validate_input(state: QAState):
        if not state["question"].strip():
            return {
                **state,
                "error": "Empty question",
                "tokens_used": None,
                "citations": [],
            }
        return state

    def generate_answer(state: QAState):
        if state.get("error"):
            return state

        chain = build_rag_chain(llm)
        raw = chain.invoke(
            {
                "question": state["question"],
                "context": state["context"],
            }
        )

        # Postprocess + grounding enforcement
        answer = enforce_grounding(
            answer=postprocess_answer(raw, state["context"]),
            citations=state["citations"],
        )

        tokens = count_tokens(
            state["question"] + state["context"] + answer
        )

        return {
            **state,
            "answer": answer,
            "tokens_used": tokens,
            # IMPORTANT: citations pass through unchanged
            "citations": state["citations"],
        }

    def handle_error(state: QAState):
        return {
            **state,
            "answer": REFUSAL_TEXT,
            "tokens_used": None,
            # IMPORTANT: refusal wipes citations
            "citations": [],
        }

    graph.add_node("validate", validate_input)
    graph.add_node("generate", generate_answer)
    graph.add_node("handle_error", handle_error)

    graph.set_entry_point("validate")

    graph.add_conditional_edges(
        "validate",
        lambda s: "handle_error" if s.get("error") else "generate",
    )

    graph.add_edge("generate", END)
    graph.add_edge("handle_error", END)

    return graph.compile()
