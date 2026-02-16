from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def build_rag_chain(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a senior automotive systems engineer.\n"
                    "Generate a complete, formal, well-structured Technical Requirement Specification document.\n"
                    "You must extract and include every single requirement explicitly present in the provided context.\n"
                    "Do not omit any hazard ID, safety goal ID, or system requirement ID.\n"
                    "Preserve all identifiers such as H-xx, SG-xx, SYS-xxx exactly as written.\n"
                    "Structure the document into numbered sections and subsections.\n"
                    "Group requirements logically (Safety, Performance, Diagnostics, Interface, Environmental, Cybersecurity, Calibration, Software, Power, Mechanical, etc.).\n"
                    "Use clear numbering, professional language, and well-paragraphed formatting.\n"
                    "Do not invent requirements that are not present in the context.\n"
                    "If context is empty, respond with: \"I don't know based on the provided documents.\""
                ),
            ),
            (
                "human",
                "Context:\n{context}\n\nTask:\n{question}",
            ),
        ]
    )

    return prompt | llm | StrOutputParser()