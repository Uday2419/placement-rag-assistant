
import re


def contextualize_question(question, chat_history):

    question = question.strip()

    if not chat_history:
        return question

    # Find the most recently mentioned company
    # by searching backwards through conversation history.
    company = None

    for message in reversed(chat_history):

        content = message.get("content", "")

        match = re.search(
            r"\bcompany\s+([xy])\b",
            content,
            re.IGNORECASE
        )

        if match:
            company = f"Company {match.group(1).upper()}"
            break

    if company is None:
        return question

    # Replace complete pronouns only.
    question = re.sub(
        r"\bits\b",
        f"{company}'s",
        question,
        flags=re.IGNORECASE
    )

    question = re.sub(
        r"\bit\b",
        company,
        question,
        flags=re.IGNORECASE
    )

    return question
