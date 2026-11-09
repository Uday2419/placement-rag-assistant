
def rewrite_query(question):

    question = question.strip()
    lower_question = question.lower()

    # Handle short CGPA questions
    if "cgpa" in lower_question:

        if "company x" in lower_question:
            return "What is the minimum CGPA required for Company X?"

        elif "company y" in lower_question:
            return "What is the minimum CGPA required for Company Y?"

    # Handle backlog questions
    if "backlog" in lower_question:

        if "company x" in lower_question:
            return "Does Company X allow students with active backlogs?"

        elif "company y" in lower_question:
            return "Does Company Y allow students with active backlogs?"

    return question
