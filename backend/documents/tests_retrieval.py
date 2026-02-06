from django.test import TestCase

from llm.retrieval import retrieve_context
from llm.embeddings import DummyEmbeddingProvider
from llm.vectorstore import InMemoryVectorStore


class RetrievalPipelineTests(TestCase):

    def setUp(self):
        self.embedding_provider = DummyEmbeddingProvider()
        self.vector_store = InMemoryVectorStore()

    def test_empty_document_returns_empty_context(self):
        context = retrieve_context(
            document_text="",
            question="What is this about?",
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )
        self.assertEqual(context, "")

    def test_retrieves_relevant_chunks(self):
        document_text = (
            "Django is a web framework.\n\n"
            "LangChain is a library for LLMs.\n\n"
            "Databricks is used for big data processing."
        )

        context = retrieve_context(
            document_text=document_text,
            question="What is LangChain?",
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            k=2,
        )

        # Because DummyEmbeddingProvider is length-based,
        # the chunk mentioning LangChain must appear
        self.assertIn("LangChain", context)

    def test_deterministic_output(self):
        document_text = "A" * 3000

        context1 = retrieve_context(
            document_text=document_text,
            question="Test?",
            embedding_provider=self.embedding_provider,
            vector_store=InMemoryVectorStore(),
        )

        context2 = retrieve_context(
            document_text=document_text,
            question="Test?",
            embedding_provider=self.embedding_provider,
            vector_store=InMemoryVectorStore(),
        )

        self.assertEqual(context1, context2)
