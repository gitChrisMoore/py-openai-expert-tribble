from py_backend.bots.AIBaseClass import AIFlatten
from py_backend.bots.trend.trend_schema import trend_schema
import logging

logging.basicConfig(level=logging.WARNING)


def run_trend_ai():
    bot_name = "Trend AI"

    default_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that helps consultants generate market trends. "
            + "When a consultant submits a topic, you will generate a market trend based on the industry or market. "
            + "Your response should be concise and unique. "
            + "The title should be a short, punchy description of the overall trend. "
            + "The implication should be two sentances, and describe examples."
            + "You should not repeat. No part of your response should use the quotes charecter.",
        },
        {
            "role": "user",
            "content": "Software Quality Engineering",
        },
        {
            "role": "assistant",
            "content": "Title: DevQualOps. Implication: The recent focus on fast, iterative releases has led to increased tech debt, agile burnout, and scalability issues. DevQualOps emerges as a solution which places more emphasis on integrating quality management and stakeholder expectations into the development process.",
        },
    ]

    functions = [
        {
            "name": "save_market_trend",
            "description": "Save information related to a given market trend",
            "parameters": {
                "type": "object",
                "properties": {
                    "trends": {
                        "type": "array",
                        "description": "Array of market trends",
                        "items": {
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
                        },
                    }
                },
            },
            "required": ["title", "implication"],
        },
    ]

    print("Starting AI: ", bot_name)
    bot = AIFlatten(
        source_id="trend_bot",
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-typed",
        inital_openai_messages=default_messages,
        functions=functions,
        function_name="save_market_trend",
        valid_schema=trend_schema,
    )
    bot.run()
    print("Shutting Down AI: ", bot_name)
