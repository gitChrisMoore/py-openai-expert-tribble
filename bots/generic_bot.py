from bots.base_bot import BaseBot
from open_ai.openai_connection import send_openai_messages


def send_message(new_messages):
    messages = [
        {
            "role": "system",
            "content": "Imagine you are a Advisor for the USER who is a CEO.  Your job is to try and help the CEO refine the market trends that they are talking about.  No part of your response should use the quotes charecter.",
        },
    ]
    messages.extend(new_messages)
    return send_openai_messages(messages)


def run_generic_bot():
    bot = BaseBot(
        consumer_id="generic_bot",
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-general",
        send_message=send_message,
    )
    bot.run()
