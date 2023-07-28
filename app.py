from flask import Flask
from kafka import KafkaProducer, KafkaConsumer
import threading
import socket

BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
UPSTASH_KAFKA_USERNAME = (
    "dXAtb3NwcmV5LTYyMzAkV7cVY7Mr0DNHEu63FYKy6PM4oFFHUhEhy9WDO_FOYmc"
)

UPSTASH_KAFKA_PASSWORD = "72784a0f2d7647e58185136ceb50a30b"
TOPIC_NAME = "prod-strategy-market_size"


# producer = KafkaProducer(
#     bootstrap_servers=BOOTSTRAP_ENDPOINT,
#     sasl_mechanism="SCRAM-SHA-512",
#     security_protocol="SASL_SSL",
#     sasl_plain_username=UPSTASH_KAFKA_USERNAME,
#     sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
# )


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        # print conntect with host and port successfully
        print(f"Connected to {host}:{port}")
        return True
    except socket.error as ex:
        print("Socket Error")
        print(ex)
        return False


app = Flask(__name__)


#


@app.route("/")
def hello_world():
    # future = producer.send(TOPIC_NAME, b"Hello Upstash!")
    # record_metadata = future.get(timeout=10)
    # print(record_metadata)
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
    internet()
    internet(host="up-osprey-6230-us1-kafka.upstash.io", port=9092)
    first_thread = threading.Thread(target=run_app)
    second_thread = threading.Thread(target=consume_messages)
    first_thread.start()
    second_thread.start()
