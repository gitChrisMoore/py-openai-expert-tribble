import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
import logging

load_dotenv()
logging.basicConfig(level=logging.WARNING)

BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
TOPIC_NAME = "prod-strategy-market_size"


def producer_value_serializer(v):
    print("producer_value_serializer: ", v)
    print("producer_value_serializer: ", json.dumps(v).encode("utf-8"))
    return json.dumps(v).encode("utf-8")


class BaseBotFunction:
    """Base Bot Function Class"""

    def __init__(
        self,
        consumer_id,
        sub_topic_name,
        pub_topic_name,
        get_openai_response,
        parse_openai_res,
        is_valid_kafka_message,
        message_threshold=5,
    ):
        self.consumer = KafkaConsumer(
            bootstrap_servers=BOOTSTRAP_ENDPOINT,
            sasl_mechanism="SCRAM-SHA-512",
            security_protocol="SASL_SSL",
            sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
            sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_ENDPOINT,
            sasl_mechanism="SCRAM-SHA-512",
            security_protocol="SASL_SSL",
            sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
            sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
            value_serializer=producer_value_serializer,
        )
        self.sub_topic_name = sub_topic_name
        self.pub_topic_name = pub_topic_name
        self.consumer_id = consumer_id
        self.get_openai_response = get_openai_response
        self.message_counter = 0
        self.message_threshold = message_threshold
        self.parse_openai_res = parse_openai_res
        self.is_valid_kafka_message = is_valid_kafka_message

    def send_messages_outbound(self, messages):
        """Send messages to the Kafka topic"""
        for message in messages:
            self.producer.send(self.pub_topic_name, value=message)
            logging.info(
                "Sent message to topic: %s, message: %s", self.pub_topic_name, message
            )

    def incresement_message_counter(self):
        # unsubscribe if the counter is greater than the threshold, else increment the counter
        self.message_counter += 1
        print("Message counter: %s", self.message_counter)

    def get_openai_query(self, inbound_message):
        try:
            res = [
                {
                    "role": inbound_message["role"],
                    "content": inbound_message["content"],
                }
            ]
            logging.info("get_openai_query: success")
            return res
        except Exception as error:
            logging.error("get_openai_query: error - %s", error)

    def run(self):
        """Creates a consumer and subscribes to the specified topic name.

        The consumer will listen for messages on the topic name and send the
        message to the OpenAI API. The response from the OpenAI API will be
        sent back to the Kafka topic.

        Flow:
            1. Create a consumer and subscribe to the specified topic name.
            2. Listen for messages on the topic name.
            3. Send the message to the OpenAI API.
            4. Send the response from the OpenAI API to the Kafka topic.
            5. Unsubscribe from the topic name if the message counter is greater
                than the threshold.

        """
        try:
            self.consumer.subscribe([self.sub_topic_name])
            logging.info(
                "Consumer ID: %s is listening for messages on topic: %s",
                self.consumer_id,
                self.sub_topic_name,
            )

            for inbound_message in self.consumer:
                # Check to maker sure message is valid
                if (
                    self.is_valid_kafka_message(inbound_message.value, self.consumer_id)
                    is False
                ):
                    continue

                # Get the OpenAI response
                openai_query = self.get_openai_query(inbound_message.value)
                openai_res = self.get_openai_response(openai_query)

                if openai_res is None:
                    logging.warning("openai_res is None")
                    continue

                # Send messages outbound to Kafka
                outbound_messages = self.parse_openai_res(openai_res, self.consumer_id)
                self.send_messages_outbound(outbound_messages)

                # Increment message sent
                self.incresement_message_counter()
                if self.message_counter > self.message_threshold:
                    print("Unsubscribing from topic: %s", self.sub_topic_name)
                    self.consumer.unsubscribe()
                    break

        except KeyboardInterrupt:
            logging.info("Consumer stopped.")
            self.consumer.close()
        except Exception as error:
            logging.error("Error in AI_Bot run: %s", error)
