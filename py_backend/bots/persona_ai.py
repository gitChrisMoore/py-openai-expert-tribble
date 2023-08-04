from py_backend.bots.AIBaseClass import AIBaseClass
import json
import logging

from py_backend.bots.persona.persona_schema import persona_schema

logging.basicConfig(level=logging.WARNING)


def run_persona_ai():
    json_file_path = "py_backend/problem_solvers/problem_solver_config.json"
    with open(json_file_path, "r") as file:
        problem_solver = json.load(file)

    print("Starting AI: ", problem_solver["name"])
    bot = AIBaseClass(
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
