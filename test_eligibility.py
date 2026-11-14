
import unittest

from main import answer_eligibility_question


class TestEligibility(unittest.TestCase):

    def test_company_x_eligible(self):
        question = (
            "Is a student with 8.5 CGPA and 0 active backlogs "
            "eligible for Company X?"
        )
        answer = answer_eligibility_question(question)
        self.assertTrue(answer.startswith("Yes."))

    def test_company_x_cgpa_boundary(self):
        question = (
            "Is a student with 7.5 CGPA and 0 active backlogs "
            "eligible for Company X?"
        )
        answer = answer_eligibility_question(question)
        self.assertTrue(answer.startswith("No."))
        self.assertIn("above 7.5", answer)

    def test_company_x_active_backlog(self):
        question = (
            "Is a student with 8.5 CGPA and 1 active backlog "
            "eligible for Company X?"
        )
        answer = answer_eligibility_question(question)
        self.assertTrue(answer.startswith("No."))
        self.assertIn("no active backlogs", answer)

    def test_company_y_eligible(self):
        question = (
            "Is a student with 8.5 CGPA and 1 active backlog "
            "eligible for Company Y?"
        )
        answer = answer_eligibility_question(question)
        self.assertTrue(answer.startswith("Yes."))

    def test_company_y_cgpa_boundary(self):
        question = (
            "Is a student with 8.0 CGPA and 0 active backlogs "
            "eligible for Company Y?"
        )
        answer = answer_eligibility_question(question)
        self.assertTrue(answer.startswith("No."))
        self.assertIn("above 8.0", answer)

    def test_company_y_active_backlog_limit(self):
        question = (
            "Is a student with 8.5 CGPA and 2 active backlogs "
            "eligible for Company Y?"
        )
        answer = answer_eligibility_question(question)
        self.assertTrue(answer.startswith("No."))
        self.assertIn("at most 1", answer)


if __name__ == "__main__":
    unittest.main()
