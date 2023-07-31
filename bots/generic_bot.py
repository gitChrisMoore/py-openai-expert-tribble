from bots.base_bot import BaseBot
from open_ai.openai_connection import send_openai_messages


def send_message(new_messages):
    messages = [
        {
            "role": "system",
            "content": "Imagine you are a Advisor for the USER who is a CEO.  Respond with two sentances max.",
        },
    ]
    messages.extend(new_messages)
    return send_openai_messages(messages)


def run_generic_bot():
    bot = BaseBot(
        consumer_id="generic_bot",
        sub_topic_name="prod-strategy-market_size",
        pub_topic_name="prod-strategy-market_size",
        send_message=send_message,
    )
    bot.run()
