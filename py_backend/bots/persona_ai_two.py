from py_backend.bots.AIBaseClass import AIBaseClassFunctions
from py_backend.bots.persona.persona_schema import persona_schema


def run_persona_ai_two():
    bot_name = "persona_ai"

    default_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant, and responsable for coming up with personas.  "
            + "Each persona should be unique."
            + "Your job is to provide a concise and unique response. ",
        },
    ]

    functions = [
        {
            "name": "save_persona",
            "description": "Save information related to a given persona",
            "parameters": persona_schema,
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
        },
    ]

    print("Starting AI: ", bot_name)
    bot = AIBaseClassFunctions(
        source_id=bot_name,
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-typed",
        inital_openai_messages=default_messages,
        functions=functions,
        function_name=functions[0]["name"],
        valid_schema=persona_schema,
        ignored_roles=["system"],
        source_type="functional",
        ignored_source_types=["functional"],
    )
    bot.run()
    print("Shutting Down AI: ", bot_name)
