import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from flask import Response, request
from py_backend.rails_conversational import bp

BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
RAILS_CONVERSATIONAL_TOPIC_NAME_PUB = "strategy-market_obsticle-general"
RAILS_CONVERSATIONAL_TOPIC_NAME_SUB = "strategy-market_obsticle-general"
ROUTES_ID = "rails_conversational"


@bp.route("/", methods=["POST"])
def submit_conversation_message():
    """Submit a message to the Kafka topic"""
    data = request.json
    message = {
        "consumer_id": "front_end",
        "role": "user",
        "content": data["content"],
    }
    load_dotenv()
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
        sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    producer.send(RAILS_CONVERSATIONAL_TOPIC_NAME_PUB, value=message)
    print(f"{ROUTES_ID}: {RAILS_CONVERSATIONAL_TOPIC_NAME_PUB} - published message")
    return Response(
        json.dumps({"success": True, "message": "Message sent successfully"}),
        status=200,
        mimetype="application/json",
    )


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
    # add try catch block
    try:
        print("subscribing to topic", topic_name)
        consumer.subscribe([topic_name])
        for message in consumer:
            print(f"{ROUTES_ID}: {topic_name} - received message")
            # respond to web listner
            yield f"data: {message.value}\n\n"
    except Exception as e:
        print("error", e)
    finally:
        consumer.close()


@bp.route("/subscribe")
def subscribe_events_market_obsticle():
    """subscribe to kafka topic and send data to web listner"""
    response = Response(
        parse_event_data(RAILS_CONVERSATIONAL_TOPIC_NAME_SUB),
        content_type="text/event-stream",
    )
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response
