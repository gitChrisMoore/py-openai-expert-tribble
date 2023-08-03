from py_backend.bots.base_bot_function import BaseBotFunction
from open_ai.openai_connection import send_openai_messages
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

    if "content" not in payload:
        logging.warning("Payload is missing a content: %s", payload)
        return False

    return True


def parse_openai_res(openai_response, consumer_id):
    openai_response["consumer_id"] = consumer_id
    print("handle_response_custom: ", openai_response)
    return [openai_response]


def get_openai_response(new_messages):
    print("CEO ADvisor: send_message: ", new_messages)
    messages = [
        {
            "role": "system",
            "content": "Imagine you are a Advisor for the USER who is a CEO.  Your job is to try and help the CEO refine the market trends that they are talking about.  No part of your response should use the quotes charecter.",
        },
    ]
    messages.extend(new_messages)
    return send_openai_messages(messages)


def run_ceo_advisor_ai():
    bot_name = "CEO Advisor AI"

    print("Starting AI: ", bot_name)
    bot = BaseBotFunction(
        consumer_id="generic_bot",
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-general",
        get_openai_response=get_openai_response,
        parse_openai_res=parse_openai_res,
        is_valid_kafka_message=is_valid_kafka_message,
    )
    bot.run()
    print("Running AI: ", bot_name)
