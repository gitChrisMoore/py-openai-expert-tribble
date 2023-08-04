import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer

load_dotenv()
BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]


def custom_value_deserializer(v):
    # print("custom_value_deserializer: ", v)
    # print("custom_value_deserializer: ", json.loads(v.decode("utf-8")))
    return json.loads(v.decode("utf-8"))


def custom_value_serializer(v):
    # print("custom_value_serializer: ", v)
    # print("custom_value_serializer: ", json.dumps(v).encode("utf-8"))
    return json.dumps(v).encode("utf-8")


def create_kafka_consumer():
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
        sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
        value_deserializer=custom_value_deserializer,
    )
    return consumer


def create_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_ENDPOINT,
        sasl_mechanism="SCRAM-SHA-512",
        security_protocol="SASL_SSL",
        sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
        sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
        value_serializer=custom_value_serializer,
    )
    return producer
