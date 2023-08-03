import time
import threading
from flask import Flask
from py_backend.bots.ceo_advisor_ai import run_ceo_advisor_ai
from py_backend.bots.ceo_trend_ai import run_trend_ai
from py_backend.health_checks.env_health_check import handle_health_checks
from py_backend.rails_conversational import bp as rails_conversational_bp
from py_backend.rails_functional import bp as rails_functional_bp


def run_app():
    app = Flask(__name__)
    app.register_blueprint(
        rails_conversational_bp, url_prefix="/api/rails_conversational"
    )
    app.register_blueprint(rails_functional_bp, url_prefix="/api/rails_functional")
    app.run(debug=False, threaded=True)


if __name__ == "__main__":
    handle_health_checks()
    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=run_ceo_advisor_ai)
    third_thread = threading.Thread(target=run_trend_ai)
    first_thread.start()
    second_thread.start()
    time.sleep(1)
    third_thread.start()
    print("All threads started")
