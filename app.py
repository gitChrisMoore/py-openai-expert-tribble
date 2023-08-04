import time
import threading
from flask import Flask
from jsonschema import validate
from py_backend.bots.ceo_advisor_ai import run_ceo_advisor_ai
from py_backend.bots.ceo_trend_ai import run_trend_ai
from py_backend.bots.persona_ai import run_persona_ai, validate_json_config_file
from py_backend.health_checks.env_health_check import handle_health_checks
from py_backend.rails_conversational import bp as rails_conversational_bp
from py_backend.rails_functional import bp as rails_functional_bp
from py_backend.crud_problem_solvers import bp as crud_problem_solvers_bp
from py_backend.storage.db import (
    create_database,
    create_problem_solver_config_table,
    get_problem_solver_config,
    get_problem_solver_configs,
    init_problem_solver_config_table,
    load_database,
    remove_table,
    save_problem_solver_config,
)


def run_app():
    app = Flask(__name__)
    app.register_blueprint(
        rails_conversational_bp, url_prefix="/api/rails_conversational"
    )
    app.register_blueprint(rails_functional_bp, url_prefix="/api/rails_functional")
    app.register_blueprint(
        crud_problem_solvers_bp, url_prefix="/api/crud_problem_solvers"
    )
    app.run(debug=False, threaded=True)


# if __name__ == "__main__":
#     json_config = "py_backend/problem_solvers/problem_solver_config.json"
#     handle_health_checks()
#     first_thread = threading.Thread(target=run_app)
#     second_thread = threading.Thread(target=run_ceo_advisor_ai)
#     third_thread = threading.Thread(target=run_trend_ai)
#     fourth_thread = threading.Thread(target=run_persona_ai(json_config))
#     first_thread.start()
#     second_thread.start()
#     time.sleep(1)
#     third_thread.start()
#     fourth_thread.start()
#     print("All threads started")

# import json
# from py_backend.problem_solvers.problem_solver_base import _message


if __name__ == "__main__":
    # res = init_problem_solver_config_table()
    # print(res)
    run_app()
