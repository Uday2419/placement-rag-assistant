
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class TestPlacementAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(api.app)

    @patch("api.generate_answer")
    @patch("api.retrieve_chunks")
    def test_company_workshop_followup(
        self,
        mock_retrieve,
        mock_generate
    ):
        # Mock the first retrieval: Company X information.
        company_chunks = [
            {
                "text": "Company X requires a CGPA above 7.5.",
                "metadata": {"source": "company_x.txt"},
                "distance": 0.5
            }
        ]

        # Mock the second retrieval: General workshop information.
        workshop_chunks = [
            {
                "text": "The college placement cell conducts resume workshops.",
                "metadata": {"source": "placement_policy.txt"},
                "distance": 0.6
            }
        ]

        mock_retrieve.side_effect = [
            company_chunks,
            workshop_chunks
        ]

        mock_generate.return_value = (
            "The college placement cell conducts resume workshops. "
            "The context does not mention Company X conducting its own workshops."
        )

        # Send a follow-up question with chat history.
        response = self.client.post(
            "/ask",
            json={
                "question": "What about its workshops?",
                "chat_history": [
                    {
                        "role": "user",
                        "content": "Tell me about Company X."
                    },
                    {
                        "role": "assistant",
                        "content": "Company X has placement requirements."
                    }
                ]
            }
        )

        data = response.json()

        # Check API response.
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            data["contextualized_question"],
            "What about Company X's workshops?"
        )

        self.assertEqual(data["answer_method"], "RAG")

        # Check that both retrieval queries were executed.
        self.assertEqual(mock_retrieve.call_count, 2)

        # Check that generation received the expanded question.
        generation_question = mock_generate.call_args[0][0]

        self.assertIn("placement cell", generation_question.lower())
        self.assertIn("Company X", generation_question)

        # Check that generation received both retrieved chunks.
        generation_context = mock_generate.call_args[0][1]

        self.assertIn("Company X requires", generation_context)
        self.assertIn("resume workshops", generation_context)

        # Check source tracking.
        self.assertIn("company_x.txt", data["sources"])
        self.assertIn("placement_policy.txt", data["sources"])


if __name__ == "__main__":
    unittest.main()
