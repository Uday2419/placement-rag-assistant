chat_history = []

# First conversation
user_message = "What is the minimum CGPA required for Company X?"
assistant_message = "Company X requires a minimum CGPA of 7.5."

# Store messages in history
chat_history.append({
    "role": "user",
    "content": user_message
})

chat_history.append({
    "role": "assistant",
    "content": assistant_message
})

# Second conversation
user_message = "Does it allow active backlogs?"

chat_history.append({
    "role": "user",
    "content": user_message
})

# Display complete conversation history
for message in chat_history:
    print(message["role"], ":", message["content"])