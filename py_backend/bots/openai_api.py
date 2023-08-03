import os
from dotenv import load_dotenv
import openai


try:
    load_dotenv()
    openai.api_key = os.environ.get("VITE_SOME_KEY")
    print("set_openai_key: success")
except Exception as error:
    print("set_openai_key: error")
    print(error)


def parse_openai_response(openai_response):
    """Parse the OpenAI response"""
    try:
        response = openai_response["choices"][0]["message"]
        print("send_openai_functions: success")
        return response
    except Exception as e:
        print("send_openai_functions: error")
        print(e)
        return None


def send_openai_functions(messages, functions, function_name):
    """Function that sends a message to OpenAI and returns the response"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=functions,
            function_call={"name": function_name},
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        print("send_openai_functions: success")
        return response
    except Exception as e:
        print("send_openai_functions: error")
        print(e)
        return None


def handle_openai_query(messages, functions, function_name):
    raw_openai_response = send_openai_functions(messages, functions, function_name)
    openai_response = parse_openai_response(raw_openai_response)
    return openai_response
