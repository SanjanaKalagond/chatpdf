from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Document
from .services import get_user_document

from llm.graph import build_qa_graph
from llm.prompts import REFUSAL_TEXT

User = get_user_model()


# ---------------------------
# Day 2: Ownership Enforcement
# ---------------------------

class DocumentOwnershipTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="alice", password="password123"
        )
        self.user2 = User.objects.create_user(
            username="bob", password="password123"
        )

        self.doc1 = Document.objects.create(
            owner=self.user1,
            filename="alice_doc.pdf",
            pdf_file="pdfs/alice.pdf",
        )

    def test_owner_can_access_document(self):
        document = get_user_document(self.user1, self.doc1.id)
        self.assertEqual(document.id, self.doc1.id)

    def test_non_owner_cannot_access_document(self):
        with self.assertRaises(Exception):
            get_user_document(self.user2, self.doc1.id)


# ---------------------------
# Day 3: LLM Control & Refusal
# ---------------------------

class DummyLLM:
    """
    Dummy LLM that always hallucinates.
    """
    def invoke(self, *_args, **_kwargs):
        return "This is a hallucinated answer."


class LLMRefusalTests(TestCase):
    def test_refuses_when_context_is_empty(self):
        graph = build_qa_graph(DummyLLM())

        result = graph.invoke(
            {
                "question": "What is this document about?",
                "context": "",
                "answer": None,
                "error": None,
            }
        )

        self.assertEqual(result["answer"], REFUSAL_TEXT)

