
from retrieval import retrieve_chunks
from generation import generate_answer

import re


# --------------------------------------------------
# 1. Identify company mentioned in the question
# --------------------------------------------------

def detect_company(question):

    question_lower = question.lower()

    has_x = re.search(r"\bcompany\s+x\b", question_lower)
    has_y = re.search(r"\bcompany\s+y\b", question_lower)

    if has_x and not has_y:
        return "Company X"

    if has_y and not has_x:
        return "Company Y"

    return None


# --------------------------------------------------
# 2. Answer strict eligibility questions with rules
# --------------------------------------------------

def answer_eligibility_question(question):

    question_lower = question.lower()
    company = detect_company(question)

    if company is None:
        return None

    keywords = [
        "cgpa", "backlog", "backlogs",
        "eligible", "eligibility",
        "qualify", "qualification",
        "apply", "requirement", "requirements"
    ]

    if not any(word in question_lower for word in keywords):
        return None

    if company == "Company X":
        required_cgpa = 7.5
        max_backlogs = 0
    else:
        required_cgpa = 8.0
        max_backlogs = 1

    asks_overall_eligibility = any(
        word in question_lower
        for word in ["eligible", "eligibility", "apply", "qualify"]
    )

    # Handle simple CGPA requirement questions.
    if "cgpa" in question_lower and not asks_overall_eligibility:
        return (
            f"{company} requires a CGPA above "
            f"{required_cgpa:.1f}."
        )

    # Extract explicitly stated CGPA.
    cgpa = None

    explicit_cgpa = re.search(
        r"cgpa\s*(?:of|is|=|:)?\s*(\d{1,2}(?:\.\d+)?)"
        r"|(\d{1,2}(?:\.\d+)?)\s*cgpa",
        question_lower
    )

    if explicit_cgpa:
        cgpa = float(
            explicit_cgpa.group(1) or explicit_cgpa.group(2)
        )

    # Extract explicitly stated active backlog count.
    backlog_count = None

    if re.search(r"\b(no|zero|0) active backlogs?\b", question_lower):
        backlog_count = 0
    elif re.search(r"\b(one|1) active backlogs?\b", question_lower):
        backlog_count = 1
    elif re.search(r"\b(two|2) active backlogs?\b", question_lower):
        backlog_count = 2

    # Overall eligibility questions.
    if asks_overall_eligibility:

        if cgpa is not None and cgpa <= required_cgpa:
            return (
                f"No. {company} requires a CGPA above "
                f"{required_cgpa:.1f}; a CGPA of {cgpa:g} "
                "does not meet that requirement."
            )

        if backlog_count is not None and backlog_count > max_backlogs:
            if max_backlogs == 0:
                return (
                    f"No. {company} requires students "
                    "to have no active backlogs."
                )

            return (
                f"No. {company} allows at most "
                f"{max_backlogs} active backlog(s)."
            )

        if cgpa is not None and backlog_count is not None:
            return (
                f"Yes. The stated CGPA and backlog count "
                f"meet {company}'s listed requirements."
            )

        if cgpa is not None:
            return (
                f"The CGPA meets {company}'s requirement, "
                f"but the student must also have no more "
                f"than {max_backlogs} active backlog(s). "
                "The complete eligibility cannot be "
                "confirmed without the backlog count."
            )

        if backlog_count is not None:
            return (
                f"The backlog count meets {company}'s rule, "
                f"but the student must also have a CGPA "
                f"above {required_cgpa:.1f}."
            )

        return (
            f"Please provide your CGPA and active backlog "
            f"count to check eligibility for {company}."
        )

    # Handle general backlog policy questions.
    asks_backlog_policy = "backlog" in question_lower

    is_policy_question = any(
        phrase in question_lower
        for phrase in [
            "allow", "allows", "allowed",
            "requirement", "requirements",
            "can students", "must have",
            "active backlog"
        ]
    )

    if asks_backlog_policy and is_policy_question:

        if max_backlogs == 0:
            return (
                f"{company} requires students "
                "to have no active backlogs."
            )

        return (
            f"{company} allows up to one active backlog. "
            f"Students must also have a CGPA above "
            f"{required_cgpa:.1f}."
        )

    return None


# --------------------------------------------------
# 3. Main RAG application
# --------------------------------------------------

def main():

    while True:

        question = input(
            "\nAsk a placement question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            print("Exiting RAG application.")
            break

        if not question:
            continue

        # Step 1: Try deterministic eligibility rules.
        rule_answer = answer_eligibility_question(question)

        if rule_answer is not None:

            print("\nRAG answer:")
            print(rule_answer)
            print("Answer method: Eligibility rules")

            continue

        # Step 2: Identify company.
        company = detect_company(question)

        # Step 3: Retrieve relevant chunks.
        retrieved_chunks = retrieve_chunks(
            question,
            company=company
        )

        if not retrieved_chunks:

            print("\nRAG answer:")
            print("I don't have enough information to answer that.")

            continue

        # Step 4: Prepare context and sources.
        context_parts = []
        sources = set()

        for chunk in retrieved_chunks:

            chunk_text = chunk["text"]

            source = chunk["metadata"].get(
                "source", "Unknown"
            )

            context_parts.append(
                f"Source: {source}\nInformation: {chunk_text}"
            )

            sources.add(source)

        context = "\n\n".join(context_parts)

        # Step 5: Generate answer using Ollama.
        answer = generate_answer(question, context)

        if answer is None:

            print("\nCould not generate an answer.")

            continue

        # Step 6: Display answer.
        print("\nRAG Answer:")
        print(answer)

        print("\nSources:")

        for source in sorted(sources):
            print("-", source)


# --------------------------------------------------
# 4. Application entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()
