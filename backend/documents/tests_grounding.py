from django.test import TestCase

from llm.grounding import enforce_grounding
from llm.prompts import REFUSAL_TEXT


class GroundingTests(TestCase):
    def test_refuses_when_no_citations(self):
        answer = "LangChain is great."
        result = enforce_grounding(answer=answer, citations=[])
        self.assertEqual(result, REFUSAL_TEXT)

    def test_refuses_when_answer_not_grounded(self):
        citations = [
            {"chunk_text": "Django is a web framework."}
        ]
        answer = "LangChain is great."
        result = enforce_grounding(answer=answer, citations=citations)
        self.assertEqual(result, REFUSAL_TEXT)

    def test_accepts_grounded_answer(self):
        citations = [
            {"chunk_text": "LangChain helps build LLM applications."}
        ]
        answer = "LangChain helps build applications."
        result = enforce_grounding(answer=answer, citations=citations)
        self.assertNotEqual(result, REFUSAL_TEXT)
