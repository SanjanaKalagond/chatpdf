from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from documents.models import Document
from documents.services import answer_document_question
from llm.embeddings import DummyEmbeddingProvider
from documents.tests import DummyLLM
from llm.prompts import REFUSAL_TEXT
User = get_user_model()

class EndToEndQATest(TestCase):
    def test_full_pipeline_runs(self):
        user = User.objects.create_user("alice", password="pass")
        doc = Document.objects.create(
            owner=user,
            filename="doc.txt",
        )
<<<<<<< HEAD

=======
>>>>>>> bc46b94 (Committing)
        doc.pdf_file.save(
            "doc.txt",
            ContentFile("LangChain is a framework for LLMs."),
        )
        log = answer_document_question(
            user=user,
            document=doc,
            question="What is LangChain?",
            embedding_provider=DummyEmbeddingProvider(),
            llm=DummyLLM(),
        )        
        self.assertEqual(log.answer, REFUSAL_TEXT)
        self.assertGreater(len(log.citations), 0)
        self.assertIn("LangChain", log.citations[0]['chunk_text'])
<<<<<<< HEAD
        self.assertIsNotNone(log.latency_ms)
=======
        self.assertIsNotNone(log.latency_ms)
>>>>>>> bc46b94 (Committing)
