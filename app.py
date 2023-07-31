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


def create_message_dict(
    role="user", content="What is a good salad company", function_call=""
):
    message_dict = {
        "consumer_id": "random_other",
        "role": role,
        "content": content,
        "function_call": function_call,
    }
    return message_dict


app = Flask(__name__)
# CORS(app)
CORS(
    app,
    resources={
        r"/api/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}
    },
)
app.config["ENV"] = "development"


@app.route("/")
def hello_world():
    # future = producer.send(TOPIC_NAME, b"Hello Upstash!")

    future = producer.send(TOPIC_NAME, value=create_message_dict())
    record_metadata = future.get(timeout=10)
    # print(record_metadata)
    return "Hello, World"


def generate_event_data():
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=UPSTASH_KAFKA_USERNAME,
        sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    consumer.subscribe([TOPIC_NAME])

    for message in consumer:
        print("new message", message.value)
        # respond to web listner
        yield f"data: {message.value}\n\n"


# /events endpoint that publishes messages to a react endpoint
@app.route("/api/events")
def events():
    response = Response(generate_event_data(), content_type="text/event-stream")
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# api/submit_events endpoint that publishes messages to a kafka producer
@app.route("/api/submit_events", methods=["POST"])
def submit_events():
    print("submit_events")
    data = request.json
    future = producer.send(
        TOPIC_NAME, value=create_message_dict(content=data["content"])
    )
    # Return response to client
    return Response(
        json.dumps({"success": True, "message": "Message sent successfully"}),
        status=200,
        mimetype="application/json",
    )


# catch all route
@app.route("/<path:path>")
def catch_all(path):
    return "You want path: %s" % path


def run_app():
    app.run(debug=False, threaded=True)


if __name__ == "__main__":
    handle_health_checks()
    # send_openai_messages([{"role": "user", "content": "say one short sentance"}])
    # setup_openai()
    # try_openai()

    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=run_generic_bot)
    third_thread = threading.Thread(target=run_obstacle_bot)
    first_thread.start()
    second_thread.start()
    time.sleep(3)
    third_thread.start()
