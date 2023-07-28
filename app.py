from flask import Flask
from kafka import KafkaProducer, KafkaConsumer
import threading

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
)

app = Flask(__name__)


#


@app.route("/")
def hello_world():
    future = producer.send(TOPIC_NAME, b"Hello Upstash!")
    record_metadata = future.get(timeout=10)
    print(record_metadata)
    return "Hello, World"


def consume_messages():
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=UPSTASH_KAFKA_USERNAME,
        sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
    )
    consumer.subscribe([TOPIC_NAME])

    print(f"Listening for messages on topic: {TOPIC_NAME}")

    try:
        for message in consumer:
            print(f"Received message: {message.value.decode('utf-8')}")
    except KeyboardInterrupt:
        print("Consumer stopped.")


def run_app():
    app.run(debug=False, threaded=True)


if __name__ == "__main__":
    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=consume_messages)
    first_thread.start()
    second_thread.start()
