persona_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "frieldy name of the persona",
        },
        "age": {
            "type": "number",
            "description": "age of the persona",
        },
        "occupation": {
            "type": "string",
            "description": "occupation of the persona",
        },
        "education": {
            "type": "string",
            "description": "education of the persona",
        },
        "personality_traits": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "personality traits of the persona",
            },
        },
        "interests": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "interests traits of the persona",
            },
        },
        "pain_points": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "pain_points traits of the persona",
            },
        },
        "goals": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "goals traits of the persona",
            },
        },
    },
    "required": [
        "name",
        "age",
        "occupation",
        "personality_traits",
        "education",
        "interests",
        "pain_points",
        "goals",
    ],
}
