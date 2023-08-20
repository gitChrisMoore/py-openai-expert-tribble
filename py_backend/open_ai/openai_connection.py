# For the OpenAI
import os
from dotenv import load_dotenv
import openai
import logging

logging.getLogger("openai_connection").setLevel(logging.WARNING)
log = logging.getLogger("openai_connection")

try:
    load_dotenv()
    openai.api_key = os.environ.get("VITE_SOME_KEY")
    print("OpenAI Key Set")
except Exception as ex:
    print("OpenAI Key Not Set")
    print(ex)

FILE_ID = "openai_connection.py"


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
    # print("messages", messages)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # print(handle_opeai_response_messages(response))
    try:
        # messages.append(handle_opeai_response_messages(response))
        return handle_opeai_response_messages(response)
    except Exception as error:
        print("Error in send_openai_messages")
        print(error)


def send_openai_functions(messages, functions, function_name, prase_response):
    """Function that sends a message to OpenAI and returns the response"""
    # openai_conn = open_ai_connection()
    # print("messages", messages)
    print("send_openai_functions: ", functions)
    print(type(functions))  # Output: <class 'int'>

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
    # print(handle_opeai_response_messages(response))
    try:
        # messages.append(handle_opeai_response_messages(response))
        return prase_response(response)
    except Exception as error:
        print("Error in send_openai_messages")
        print(error)


def send_openai_functions_two(messages, functions, function_name):
    """Function that sends a message to OpenAI and returns the response"""
    print("send_openai_functions_two: messages: ", messages)
    print("send_openai_functions_two: functions: ", functions)
    print("send_openai_functions_two: ", function_name)
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
        # print("res res re", response)
        log.info(
            "%s: send_openai_functions_two - response - %s",
            FILE_ID,
            response,
        )
        return response
    except Exception as err:
        log.error(
            "%s: send_openai_functions_two - error - %s",
            FILE_ID,
            err,
        )


def send_openai_functions_three(messages):
    """Function that sends a message to OpenAI and returns the response"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        log.info(
            "%s: send_openai_functions_three - response - %s",
            FILE_ID,
            response,
        )
        return response
    except Exception as err:
        log.error(
            "%s: send_openai_functions_three - error - %s",
            FILE_ID,
            err,
        )


{
    "name": "build_persona",
    "description": "Generates a persona, defining key demographics, behaviors, and goals to guide product development.",
    "parameters": {
        "type": '{"type": "object", "properties": {"name": {"type": "string", "description": "frieldy name of the persona"}, "age": {"type": "number", "description": "age of the persona"}, "occupation": {"type": "string", "description": "occupation of the persona"}, "education": {"type": "string", "description": "education of the persona"}, "personality_traits": {"type": "array", "items": {"type": "string", "description": "personality traits of the persona"}}, "interests": {"type": "array", "items": {"type": "string", "description": "interests traits of the persona"}}, "pain_points": {"type": "array", "items": {"type": "string", "description": "pain_points traits of the persona"}}, "goals": {"type": "array", "items": {"type": "string", "description": "goals traits of the persona"}}}, "required": ["name", "age", "occupation", "personality_traits", "education", "interests", "pain_points", "goals"]}',
        "properties": {},
        "required": [],
    },
}


{
    "type": '{"type": "object", "properties": {"name": {"type": "string", "description": "frieldy name of the persona"}, "age": {"type": "number", "description": "age of the persona"}, "occupation": {"type": "string", "description": "occupation of the persona"}, "education": {"type": "string", "description": "education of the persona"}, "personality_traits": {"type": "array", "items": {"type": "string", "description": "personality traits of the persona"}}, "interests": {"type": "array", "items": {"type": "string", "description": "interests traits of the persona"}}, "pain_points": {"type": "array", "items": {"type": "string", "description": "pain_points traits of the persona"}}, "goals": {"type": "array", "items": {"type": "string", "description": "goals traits of the persona"}}}, "required": ["name", "age", "occupation", "personality_traits", "education", "interests", "pain_points", "goals"]}',
    "properties": {},
    "required": [],
}
