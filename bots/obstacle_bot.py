from bots.base_bot import BaseBot
from open_ai.openai_connection import send_openai_messages


def send_message(new_messages):
    messages = [
        {
            "role": "system",
            "content": "Imagine you are a Advisor for the USER who is a CEO.  "
            + "Lookup 10 obstacle's from what the USER says."
            + "The CEO wants to understand what obstacles or challenges that will make it difficult to adapt to trends in the industry. "
            + "Your job is to provide a concise and unique response.  Respond with two sentances max.",
        },
    ]
    messages.extend(new_messages)
    return send_openai_messages(messages)


def run_obstacle_bot():
    bot = BaseBot(
        consumer_id="obstacle_bot",
        sub_topic_name="prod-strategy-market_size",
        pub_topic_name="prod-strategy-market_size",
        send_message=send_message,
    )
    bot.run()
