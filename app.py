import json
import time
import threading
from kafka import KafkaProducer, KafkaConsumer
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from health_checks.env_health_check import handle_health_checks
from bots.obstacle_bot import run_obstacle_bot
from bots.generic_bot import run_generic_bot


# For the Upstash
BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
UPSTASH_KAFKA_USERNAME = (
    "dXAtb3NwcmV5LTYyMzAkV7cVY7Mr0DNHEu63FYKy6PM4oFFHUhEhy9WDO_FOYmc"
)

UPSTASH_KAFKA_PASSWORD = "72784a0f2d7647e58185136ceb50a30b"
TOPIC_NAME = "prod-strategy-market_size"


producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_ENDPOINT,
    sasl_mechanism="SCRAM-SHA-512",
    security_protocol="SASL_SSL",
    sasl_plain_username=UPSTASH_KAFKA_USERNAME,
    sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


app = Flask(__name__)
# CORS(app)
CORS(
    app,
    resources={
        r"/api/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}
    },
)
app.config["ENV"] = "development"


def get_event_data(topic_name):
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=UPSTASH_KAFKA_USERNAME,
        sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    # add try catch block
    try:
        print("subscribing to topic", topic_name)
        consumer.subscribe([topic_name])
        for message in consumer:
            print("new message recieved")
            # respond to web listner
            yield f"data: {message.value}\n\n"
    except Exception as e:
        print("error", e)
    finally:
        consumer.close()


@app.route("/api/events/strategy/market_obsticle-general", methods=["POST"])
def submit_events_market_obsticle():
    data = request.json
    message = {
        "consumer_id": "front_end",
        "role": "user",
        "content": data["content"],
    }
    producer.send("strategy-market_obsticle-general", value=message)
    # Return response to client
    return Response(
        json.dumps({"success": True, "message": "Message sent successfully"}),
        status=200,
        mimetype="application/json",
    )


@app.route("/api/events/strategy/market_obsticle-general/subscribe")
def subscribe_events_market_obsticle():
    response = Response(
        get_event_data("strategy-market_obsticle-general"),
        content_type="text/event-stream",
    )
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def run_app():
    app.run(debug=False, threaded=True)


if __name__ == "__main__":
    handle_health_checks()
    # send_openai_messages([{"role": "user", "content": "say one short sentance"}])
    # setup_openai()
    # try_openai()

    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=run_generic_bot)
    # third_thread = threading.Thread(target=run_obstacle_bot)
    first_thread.start()
    second_thread.start()
    time.sleep(3)
    # third_thread.start()
