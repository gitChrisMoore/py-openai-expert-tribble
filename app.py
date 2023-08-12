import json
import os
import time
import threading
from flask import Flask
from jsonschema import validate
from py_backend.bots.ceo_advisor_ai import run_ceo_advisor_ai
from py_backend.bots.ceo_trend_ai import run_trend_ai
from py_backend.bots.persona_ai import run_persona_ai, validate_json_config_file
from py_backend.bots.persona_ai_two import run_persona_ai_two
from py_backend.health_checks.env_health_check import handle_health_checks
from py_backend.open_ai.openai_connection import send_openai_functions_two
from py_backend.rails_conversational import bp as rails_conversational_bp
from py_backend.rails_functional import bp as rails_functional_bp
from py_backend.crud_problem_solvers import bp as crud_problem_solvers_bp
from py_backend.funcs import bp as funcs_bp
from py_backend.admin import bp as admin_bp
from py_backend.storage.db import get_problem_solver_configs, load_database
from py_backend.storage.db_setup import initialize_database
from py_backend.storage.tbl_func import get_func_configs, init_func_config_table
from py_backend.blueprints import bp as blueprints_bp


def run_app():
    app = Flask(__name__)
    app.register_blueprint(
        rails_conversational_bp, url_prefix="/api/rails_conversational"
    )
    app.register_blueprint(rails_functional_bp, url_prefix="/api/rails_functional")
    app.register_blueprint(
        crud_problem_solvers_bp, url_prefix="/api/crud_problem_solvers"
    )
    app.register_blueprint(funcs_bp, url_prefix="/api/funcs")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(blueprints_bp, url_prefix="/api/blueprints")
    app.run(debug=False, threaded=True)


if __name__ == "__main__":
    json_config = "py_backend/problem_solvers/problem_solver_config.json"
    handle_health_checks()
    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=run_ceo_advisor_ai)
    third_thread = threading.Thread(target=run_trend_ai)
    # fourth_thread = threading.Thread(target=run_persona_ai(json_config))
    fourth_thread = threading.Thread(target=run_persona_ai_two)
    # fourth_thread = threading.Thread(target=run_persona_ai(json_config))
    first_thread.start()
    second_thread.start()
    time.sleep(1)
    third_thread.start()
    fourth_thread.start()
    print("All threads started")

# import json
# from py_backend.problem_solvers.problem_solver_base import _message

# run_app(


def check_json_schema():
    conn = load_database(os.environ.get("DB_FILEPATH"))

    objectives = get_func_configs(conn)
    blueprints = get_problem_solver_configs(conn)

    for obj in objectives:
        print(obj["name"])

        openai_request = {
            "messages": json.loads(blueprints[1]["initial_context"]),
            "functions": obj["parameters"],
            "function_name": obj["name"],
        }
        tmp_func = {
            "type": "object",
            "name": obj["name"],
            "parameters": json.loads(obj["parameters"]),
        }
        openai_res = send_openai_functions_two(
            openai_request["messages"],
            [tmp_func],
            # openai_request["functions"],
            openai_request["function_name"],
        )
        print(openai_res)


# if __name__ == "__main__":
#     run_app()
#     # initialize_database()
