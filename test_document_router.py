
from document_router import detect_source

questions = [
    "What is Company X eligibility?",
    "What is Company Y CGPA requirement?",
    "When are resume workshops conducted?",
    "How should I prepare for interviews?",
    "Tell me about college facilities."
]

for question in questions:

    source = detect_source(question)

    print("\nQuestion:", question)
    print("Detected source:", source)
