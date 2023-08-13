import os
import json
import logging
from dotenv import load_dotenv
from kafka import KafkaConsumer
from flask import Response
from py_backend.rails_functional import bp


logging.getLogger("rails_functional").setLevel(logging.WARNING)
log = logging.getLogger("rails_functional")

BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
RAILS_FUNCTIONAL_TOPIC_NAME_SUB = "strategy-market_obsticle-typed"
ROUTES_ID = "rails_functional"


def parse_event_data(topic_name):
    """parse kafka topic data to send to web listner"""
    load_dotenv()
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
        sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    try:
        print("subscribing to topic", topic_name)
        consumer.subscribe([topic_name])
        for message in consumer:
            # print(f"{ROUTES_ID}: {topic_name} - message recieved")
            log.info(f"{ROUTES_ID}: {topic_name} - message recieved")
            # respond to web listner
            yield f"data: {message.value}\n\n"
    except Exception as e:
        print("error", e)
    finally:
        consumer.close()


@bp.route("/subscribe")
def subscribe_events_rails_functional():
    """subscribe to kafka topic and send data to web listner"""
    res_data = parse_event_data(RAILS_FUNCTIONAL_TOPIC_NAME_SUB)
    response = Response(
        res_data,
        content_type="text/event-stream",
    )

    return response
