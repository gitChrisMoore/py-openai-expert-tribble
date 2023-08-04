conversational_message = {
    "type": "object",
    "properties": {
        "role": {
            "type": "string",
            "description": "role of the message",
        },
        "content": {
            "type": "string",
            "description": "content of the message",
        },
    },
    "required": ["role", "content"],
}
