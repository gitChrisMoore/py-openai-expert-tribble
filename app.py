"""This module runs the Flask app and the bots."""
import uuid
import threading
import os
from flask import Flask
from flask_cors import CORS
from py_backend.bots.AIThreadManager import thread_manager
from py_backend.bots.droid_assembly_basic import run_droid_basic
from py_backend.health_checks.env_health_check import handle_health_checks
from py_backend.rails_conversational import bp as rails_conversational_bp
from py_backend.rails_functional import bp as rails_functional_bp
from py_backend.admin import bp as admin_bp
from py_backend.blueprints import bp as blueprints_bp
from py_backend.objectives import bp as objectives_bp

app = Flask(__name__)
CORS(app)

INSTANCE_UUID = str(uuid.uuid4())
app.config["INSTANCE_UUID"] = INSTANCE_UUID


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
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=False, host=host, port=port, threaded=True)


if __name__ == "__main__":
    handle_health_checks()
    threading.Thread(name="Flask App", target=run_app).start()
    thread_manager.add_threads(
        [
            (
                "CEO Advisor AI",
                run_droid_basic,
                ("c720aaae-06ea-479b-b7f6-2397e7174fcc",),
            ),
            (
                "Market Trends",
                run_droid_basic,
                (
                    "c720aaae-06ea-479b-b7f6-2397e7174f6b",
                    "c720aaae-06ea-479b-b7f6-2397e7174f6o",
                ),
            ),
            (
                "Persona Bot",
                run_droid_basic,
                (
                    "e7602ac8-80f7-4584-aec4-053ce3590291",
                    "31db3025-00c3-4258-a717-718e9a11388b",
                ),
            ),
        ]
    )
    thread_manager.start_threads()
    print("All threads started")
