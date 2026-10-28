
from generation import generate_answer

question = "What is the CGPA requirement for Company X?"

context = """
Company X requires a CGPA above 7.5.
Students must have no active backlogs for Company X.
"""

answer = generate_answer(question, context)

if answer is None:
    print("Answer generation failed.")
else:
    print("Generated answer:", answer)
