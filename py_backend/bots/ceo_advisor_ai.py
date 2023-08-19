from py_backend.bots.AIBaseClass import AIBaseClass


def run_ceo_advisor_ai():
    bot_name = "CEO Advisor AI"

    default_messages = [
        {
            "role": "system",
            "content": "Imagine you are a Advisor for the USER who is a CEO.  Your job is to try and help the CEO refine the market trends that they are talking about.  No part of your response should use the quotes charecter.",
        },
    ]

    print("Starting AI: ", bot_name)
    bot = AIBaseClass(
        source_id="generic_botaaa",
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-general",
        inital_openai_messages=default_messages,
        ignored_roles=["system"],
        source_type="conversational",
        ignored_source_types=["functional"],
    )
    bot.run()
    print("Shutting Down AI: ", bot_name)
