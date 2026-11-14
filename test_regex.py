import re

questions = [
    "My CGPA is 8.5",
    "CGPA: 7.5",
    "I have 9 CGPA",
    "My CGPA of 8.25"
]

pattern = (
    r"cgpa\s*(?:of|is|=|:)?\s*(\d{1,2}(?:\.\d+)?)"
    r"|(\d{1,2}(?:\.\d+)?)\s*cgpa"
)

for question in questions:

    match = re.search(pattern, question.lower())

    if match:
        cgpa = float(match.group(1) or match.group(2))
        print(question, "->", cgpa)