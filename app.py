"""This module runs the Flask app and the bots."""
import time
import threading
import os
from flask import Flask
from py_backend.bots.ceo_advisor_ai import run_ceo_advisor_ai
from py_backend.bots.ceo_trend_ai import run_trend_ai
from py_backend.bots.persona_ai_two import run_persona_ai_two
from py_backend.health_checks.env_health_check import handle_health_checks
from py_backend.rails_conversational import bp as rails_conversational_bp
from py_backend.rails_functional import bp as rails_functional_bp
from py_backend.admin import bp as admin_bp
from py_backend.blueprints import bp as blueprints_bp
from py_backend.objectives import bp as objectives_bp

import logging

logging.getLogger("py_backend.bots.ceo_advisor_ai").setLevel(logging.WARNING)
logging.getLogger("py_backend.bots.ceo_trend_ai").setLevel(logging.WARNING)
logging.getLogger("py_backend.bots.persona_ai_two").setLevel(logging.WARNING)


# TODO:
# = [ ] Add functionality to read from config file
app = Flask(__name__)


@app.route("/")
def index():
    return """This module runs the Flask app and the bots."""


def run_app():
    """Runs the Flask app."""

    app.register_blueprint(
        rails_conversational_bp, url_prefix="/api/rails_conversational"
    )
    app.register_blueprint(rails_functional_bp, url_prefix="/api/rails_functional")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(blueprints_bp, url_prefix="/api/blueprints")
    app.register_blueprint(objectives_bp, url_prefix="/api/objectives")
    # host = os.environ.get("FLASK_HOST", "0.0.0.0")  # Default to '0.0.0.0' if not set
    host = os.environ.get("HOST", "0.0.0.0")  # Default to '0.0.0.0' if not set
    port = int(os.environ.get("PORT", "5000"))  # Default to 5000 if not set
    # app.run(host=host, port=port, debug=False, threaded=True)
    app.run(debug=False, host=host, port=port, threaded=True)  # type: ignore
    # app.run(debug=False, threaded=True)


if __name__ == "__main__":
    # JSON_CONFIG = "py_backend/problem_solvers/problem_solver_config.json"
    handle_health_checks()
    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=run_ceo_advisor_ai)
    third_thread = threading.Thread(target=run_trend_ai)
    # # fourth_thread = threading.Thread(target=run_persona_ai(JSON_CONFIG))
    fourth_thread = threading.Thread(target=run_persona_ai_two)
    # # fourth_thread = threading.Thread(target=run_persona_ai(JSON_CONFIG))

    first_thread.start()
    second_thread.start()
    time.sleep(1)
    third_thread.start()
    fourth_thread.start()
    print("All threads started")
