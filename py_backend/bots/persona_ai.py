import json
import logging
from jsonschema import validate
from py_backend.bots.AIBaseClass import AIBaseClassFunctions
from py_backend.problem_solvers.conversational_message import conversational_message

logging.basicConfig(level=logging.WARNING)


class InvalidInitialContextException(Exception):
    """
    An exception to represent an invalid initial context.
    """

    def __init__(self, message):
        super().__init__(message)


class MissingJSONConfigFileException(Exception):
    """
    An exception to represent a missing json config file.
    """

    def __init__(self, message):
        super().__init__(message)


def is_valid_initial_context(messages):
    """Check if the inbound source_id is valid"""
    for message in messages:
        try:
            validate(instance=message, schema=conversational_message)
        except Exception as error:
            print(f"is_valid_messages: {error} - {message}")
            raise InvalidInitialContextException from error  # type: ignore
    return True


def validate_json_config_file(data):
    """Validate the json config file"""
    try:
        is_valid_initial_context(data["initial_context"])

        if "name" not in data:
            raise MissingJSONConfigFileException(
                "name is missing from the json config file"
            )

        if "sub_topic_name" not in data:
            raise MissingJSONConfigFileException(
                "sub_topic_name is missing from the json config file"
            )

        if "pub_topic_name" not in data:
            raise MissingJSONConfigFileException(
                "pub_topic_name is missing from the json config file"
            )

        if "functions" not in data:
            raise MissingJSONConfigFileException(
                "functions is missing from the json config file"
            )

        if "initial_context" not in data:
            raise MissingJSONConfigFileException(
                "initial_context is missing from the json config file"
            )

        print(f"validate_json_config_file: success, {data['name']}")
        return data
    except Exception as error:
        print(f"validate_json_config_file: {error}")
        raise error


def start_ai(problem_solver_json):
    """Run the persona ai"""
    problem_solver = validate_json_config_file(problem_solver_json)

    print("Starting AI: ", problem_solver["name"])
    bot = AIBaseClassFunctions(
        source_id=problem_solver["name"],
        sub_topic_name=problem_solver["sub_topic_name"],
        pub_topic_name=problem_solver["pub_topic_name"],
        inital_openai_messages=problem_solver["initial_context"],
        functions=problem_solver["functions"],
        function_name=problem_solver["functions"][0]["name"],
        valid_schema=problem_solver["functions"][0]["parameters"],
    )
    bot.run()
    print("Shutting Down AI: ", problem_solver["name"])


def run_persona_ai(json_file_path):
    """Run the persona ai"""
    with open(json_file_path, "r") as file:
        problem_solver_json = json.load(file)

    start_ai(problem_solver_json)
