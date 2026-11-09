
def detect_source(question):

    question = question.lower()

    if "company x" in question:
        return "company_x.txt"

    elif "company y" in question:
        return "company_y.txt"

    elif "resume" in question or "placement cell" in question:
        return "placement_policy.txt"

    elif "interview" in question:
        return "interview_guidelines.txt"

    else:
        return None
