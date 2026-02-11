from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def build_rag_chain(llm):
    """
    Builds a simple RAG chain:
    Prompt -> LLM -> String output

    The chain expects:
        {
            "question": str,
            "context": str
        }
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a question-answering assistant.\n"
                    "Answer ONLY using the provided context.\n"
                    "If the answer is not in the context, say:\n"
                    "\"I don't know based on the provided documents.\""
                ),
            ),
            (
                "human",
                "Context:\n{context}\n\nQuestion:\n{question}",
            ),
        ]
    )

    return prompt | llm | StrOutputParser()
