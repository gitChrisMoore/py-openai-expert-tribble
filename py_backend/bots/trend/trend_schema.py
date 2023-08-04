trend_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "frieldy name of the market trend",
        },
        "implication": {
            "type": "string",
            "description": "Inference of what the market trend means to the industry",
        },
    },
}

# trends_schema = {
#     "type": "object",
#     "properties": {
#         "trends": {
#             "type": "array",
#             "description": "Array of market trends",
#             "items": trend_schema,
#         }
#     },
# }
trends_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "implication": {"type": "string"},
        },
        "required": ["name", "description"],
    },
}
