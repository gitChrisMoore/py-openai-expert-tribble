import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from flask import Response, request
from app.market_obsticle import bp

BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
TOPIC_NAME = "prod-strategy-market_size"


print("Kafka username: ", os.environ.get("UPSTASH_KAFKA_USERNAME"))
print("Kafka password: ", os.environ.get("UPSTASH_KAFKA_PASSWORD"))


def get_event_data(topic_name):
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
            print("new message recieved")
            # respond to web listner
            yield f"data: {message.value}\n\n"
    except Exception as e:
        print("error", e)
    finally:
        consumer.close()


def get_event_function_data(topic_name):
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
            print("new message recieved", topic_name)
            # respond to web listner
            yield f"data: {message.value}\n\n"
    except Exception as e:
        print("error", e)
    finally:
        consumer.close()


@bp.route("/")
def base_res():
    return "hello"


@bp.route("/market_obsticle-general", methods=["POST"])
def submit_events_market_obsticle():
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

    producer.send("strategy-market_obsticle-general", value=message)
    # Return response to client
    return Response(
        json.dumps({"success": True, "message": "Message sent successfully"}),
        status=200,
        mimetype="application/json",
    )


@bp.route("/market_obsticle-general/subscribe")
def subscribe_events_market_obsticle():
    response = Response(
        get_event_data("strategy-market_obsticle-general"),
        content_type="text/event-stream",
    )
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@bp.route("/market_obsticle-typed/subscribe")
def subscribe_events_market_obsticle_typed():
    res_data = get_event_function_data("strategy-market_obsticle-typed")

    response = Response(
        res_data,
        content_type="text/event-stream",
    )
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response
