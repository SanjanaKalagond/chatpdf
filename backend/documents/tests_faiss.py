from django.test import TestCase
from llm.retrieval import retrieve_context
from llm.vectorstore import FAISSVectorStore
from llm.embeddings import DummyEmbeddingProvider

class FAISSRetrievalTests(TestCase):
    def test_faiss_returns_relevant_context(self):
        embedding_provider = DummyEmbeddingProvider()
        vector_store = FAISSVectorStore(dim=5)

        document_text = (
            "Python is a programming language.\n\n"
            "LangChain helps build LLM applications.\n\n"
            "Databricks is used for large-scale data processing."
        )
        context, citations = retrieve_context(
            document_text=document_text,
            question="What is LangChain?",
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            k=2,
        )
        self.assertIn("LangChain", context)
        self.assertGreater(len(citations), 0)
