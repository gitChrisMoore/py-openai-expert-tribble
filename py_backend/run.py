import time
import threading
from flask import Flask
from .health_checks.env_health_check import handle_health_checks


def run_app():
    app = Flask(__name__)
    app.register_blueprint(market_obsticle_bp, url_prefix="/api/events/strategy")
    app.run(debug=False, threaded=True)


if __name__ == "__main__":
    handle_health_checks()
    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=run_generic_bot)
    third_thread = threading.Thread(target=run_trend_bot)
    first_thread.start()
    second_thread.start()
    time.sleep(2)
    third_thread.start()
    print("All threads started")
