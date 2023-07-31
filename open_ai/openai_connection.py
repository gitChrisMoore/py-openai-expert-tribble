# For the OpenAI
import os
from dotenv import load_dotenv
import openai


try:
    load_dotenv()
    openai.api_key = os.environ.get("VITE_SOME_KEY")
    print("OpenAI Key Set")
except Exception as ex:
    print("OpenAI Key Not Set")
    print(ex)


def handle_opeai_response_messages(response):
    """Function that handles the response from OpenAI"""
    try:
        message = response["choices"][0]["message"]
        return message
    except Exception as error:
        print("Error in handle_opeai_response_messages")
        print(error)


def send_openai_messages(messages):
    """Function that sends a message to OpenAI and returns the response"""
    # openai_conn = open_ai_connection()
    print("messages", messages)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(handle_opeai_response_messages(response))
    try:
        # messages.append(handle_opeai_response_messages(response))
        return handle_opeai_response_messages(response)
    except Exception as error:
        print("Error in send_openai_messages")
        print(error)
