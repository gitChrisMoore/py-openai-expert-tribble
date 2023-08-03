import json
from py_backend.bots.base_bot_function import BaseBotFunction
from open_ai.openai_connection import send_openai_functions
import logging

logging.basicConfig(level=logging.WARNING)


def is_valid_kafka_message(payload, own_consumer_id):
    """Check if the payload is valid"""

    if "consumer_id" not in payload:
        logging.warning("Message does not have a consumer_id: %s", payload)
        return False

    if payload["consumer_id"] == own_consumer_id:
        logging.warning("Message is from the same consumer_id, ignoring: %s", payload)
        return False

    if "role" not in payload:
        logging.warning("Payload is missing a role: %s", payload)
        return False

    if payload["role"] == "user":
        logging.info("Payload is a user, ignorring: %s", payload)
        return False

    if payload["role"] == "system":
        logging.info("Payload is a system, ignorring: %s", payload)
        return False

    if "content" not in payload:
        logging.warning("Payload is missing a content: %s", payload)
        return False

    return True


def handle_response_custom(openai_response):
    """Function that handles the response from OpenAI"""
    try:
        arguments_raw = openai_response["choices"][0]["message"]["function_call"][
            "arguments"
        ]
        arguments = json.loads(arguments_raw)
        print("handle_response_custom: success - parsed openai_response")
        res = arguments["trends"]
        print("handle_response_custom: success - parsed records: ", str(len(res)))
        return res
    except Exception as error:
        print("handle_response_custom: error in parsing response")
        print(error)
        print("handle_response_custom: ", openai_response)


def parse_openai_res(openia_res, consumer_id):
    """Parse the OpenAI response"""
    messages = []
    for i in openia_res:
        messages.append(
            {
                "role": "assistant",
                "title": i["title"],
                "implication": i["implication"],
            }
        )
    return messages


def get_openai_response(new_messages):
    messages = [
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
    messages.extend(new_messages)

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

    return send_openai_functions(
        messages=messages,
        functions=functions,
        function_name="save_market_trend",
        prase_response=handle_response_custom,
    )


def run_trend_bot():
    bot_name = "Trend AI"

    print("Starting AI: ", bot_name)
    bot = BaseBotFunction(
        consumer_id="trend_bot",
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-typed",
        get_openai_response=get_openai_response,
        parse_openai_res=parse_openai_res,
        is_valid_kafka_message=is_valid_kafka_message,
    )
    bot.run()
    print("Running AI: ", bot_name)
