import json
from bots.base_botB import BaseBotB
from open_ai.openai_connection import send_openai_functions


def handle_response_custom(response):
    """Function that handles the response from OpenAI"""

    print("TTTTTTTTTTT TTTTT TTTT TTT ")
    message = response["choices"][0]["message"]
    try:
        message_json_dumps = json.dumps(message)
        function_call = json.loads(message_json_dumps)
        arguments = function_call["function_call"]["arguments"]
        arguments_json = json.loads(arguments)
        events = arguments_json["trends"]
        print("handle_response_custom: success, trend_bot")
        return events
    except Exception as error:
        print("Error in handle_response_custom")
        print(error)

    # print("handle_response_custom           : ", json.loads(message))
    return message


def send_message(new_messages):
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
    print("Running trend bot")
    bot = BaseBotB(
        consumer_id="trend_bot",
        sub_topic_name="strategy-market_obsticle-general",
        pub_topic_name="strategy-market_obsticle-typed",
        send_message=send_message,
    )
    bot.run()
