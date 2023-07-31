"""Kafka consumer and producer configuration

This module contains the configuration for the Kafka consumer and producer
that is used by external files.

This file can also be imported as a module and contains the following
dicts:
    * BOOTSTRAP_ENDPOINT - the endpoint for the Kafka cluster
    * UPSTASH_KAFKA_USERNAME - the username for the Kafka cluster
    * UPSTASH_KAFKA_PASSWORD - the password for the Kafka cluster
    * TOPIC_NAME - the topic name for the Kafka cluster
    
"""


import json
from kafka import KafkaProducer, KafkaConsumer

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

consumer = KafkaConsumer(
    bootstrap_servers=BOOTSTRAP_ENDPOINT,
    sasl_mechanism="SCRAM-SHA-512",
    security_protocol="SASL_SSL",
    sasl_plain_username=UPSTASH_KAFKA_USERNAME,
    sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
)
