
import unittest

from contextualizer import contextualize_question


class TestContextualizer(unittest.TestCase):

    def test_company_x_reference(self):
        history = [
            {"role": "user", "content": "Tell me about Company X."},
            {"role": "assistant", "content": "Company X has placement requirements."},
            {"role": "user", "content": "Does it allow active backlogs?"}
        ]

        result = contextualize_question(
            "What about its workshops?", history
        )

        self.assertEqual(
            result, "What about Company X's workshops?"
        )

    def test_company_y_reference(self):
        history = [
            {"role": "user", "content": "Tell me about Company Y."}
        ]

        result = contextualize_question(
            "Does it allow active backlogs?", history
        )

        self.assertEqual(
            result, "Does Company Y allow active backlogs?"
        )

    def test_empty_history(self):
        result = contextualize_question(
            "What about its workshops?", []
        )

        self.assertEqual(result, "What about its workshops?")

    def test_no_company_mentioned(self):
        history = [
            {"role": "user", "content": "Tell me about placements."}
        ]

        result = contextualize_question(
            "What about its workshops?", history
        )

        self.assertEqual(result, "What about its workshops?")

    def test_unrelated_words_remain_unchanged(self):
        history = [
            {"role": "user", "content": "Tell me about Company X."}
        ]

        result = contextualize_question(
            "Does it offer internships?", history
        )

        self.assertEqual(
            result, "Does Company X offer internships?"
        )


if __name__ == "__main__":
    unittest.main()
