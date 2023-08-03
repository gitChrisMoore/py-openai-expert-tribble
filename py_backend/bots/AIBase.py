import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from open_ai.openai_connection import send_openai_messages
import logging


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


class AIMessageBaseClass:
    """AI Parent Base Class

    * Recieve messages from a Kafka topic
    * Send messages to a OpenAI API
    * Recieve messages from a OpenAI API
    * Send messages to a Kafka topic

    """

    def __init__(
        self,
        consumer_id,
        sub_topic_name,
        pub_topic_name,
        inital_openai_messages,
        message_counter=0,
        message_threshold=5,
    ):
        self.consumer = KafkaConsumer(
            bootstrap_servers=BOOTSTRAP_ENDPOINT,
            sasl_mechanism="SCRAM-SHA-512",
            security_protocol="SASL_SSL",
            sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
            sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
            value_deserializer=custom_value_deserializer,
        )
        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_ENDPOINT,
            sasl_mechanism="SCRAM-SHA-512",
            security_protocol="SASL_SSL",
            sasl_plain_username=os.environ.get("UPSTASH_KAFKA_USERNAME"),
            sasl_plain_password=os.environ.get("UPSTASH_KAFKA_PASSWORD"),
            value_serializer=custom_value_serializer,
        )
        self.sub_topic_name = sub_topic_name
        self.pub_topic_name = pub_topic_name
        self.consumer_id = consumer_id
        self.inital_openai_messages = inital_openai_messages
        self.message_counter = message_counter
        self.message_threshold = message_threshold

    def is_valid_inbound_consumer_id(self, payload):
        """Check if the inbound consumer_id is valid"""
        if "consumer_id" not in payload:
            logging.warning("Message does not have a consumer_id: %s", payload)
            return False

        if payload["consumer_id"] == self.consumer_id:
            logging.warning(
                "Message is from the same consumer_id, ignoring: %s", payload
            )
            return False

        return True

    def is_valid_inbound_role(self, payload):
        """Check if the inbound role is valid"""
        if "role" not in payload:
            logging.warning("Payload is missing a role: %s", payload)
            return False

        if payload["role"] == "system":
            logging.info("Payload is a system, ignorring: %s", payload)
            return False

        return True

    # def is_valid_inbound_role(self, payload):
    #     """Check if the inbound role is valid"""
    #     if "role" not in payload:
    #         logging.warning("Payload is missing a role: %s", payload)
    #         return False

    #     if payload["role"] == "user":
    #         logging.info("Payload is a user, ignorring: %s", payload)
    #         return False

    #     if payload["role"] == "system":
    #         logging.info("Payload is a system, ignorring: %s", payload)
    #         return False

    def get_openai_response(self, inbound_message):
        """Get the OpenAI response"""
        _messages = []
        _messages.extend(self.inital_openai_messages)
        new_messages = [
            {
                "role": inbound_message["role"],
                "content": inbound_message["content"],
            }
        ]
        _messages.extend(new_messages)
        try:
            res = send_openai_messages(_messages)
            print(f"{self.consumer_id}: get_openai_response - success")
            return res
        except Exception as error:
            print(f"{self.consumer_id}: get_openai_response - error")
            print(error)
            return None

    def parse_openai_res(self, openai_res):
        """Parse the OpenAI response"""
        openai_res["consumer_id"] = self.consumer_id
        return [openai_res]

    def send_messages_outbound(self, messages):
        """Send messages to the Kafka topic"""
        for message in messages:
            try:
                self.producer.send(self.pub_topic_name, value=message)
                print(f"{self.consumer_id}: send_messages_outbound - success")
            except Exception as error:
                print(f"{self.consumer_id}: send_messages_outbound - error")
                print(error)
                continue

    def incresement_message_counter(self):
        """Incresement the message counter"""
        self.message_counter += 1
        print("Message counter: %s", self.message_counter)

    def run(self):
        """Run the AI"""
        try:
            self.consumer.subscribe([self.sub_topic_name])
            logging.info(
                "Consumer ID: %s is listening for messages on topic: %s",
                self.consumer_id,
                self.sub_topic_name,
            )

            for message in self.consumer:
                if (self.is_valid_inbound_consumer_id(message.value)) is False:
                    continue
                if (self.is_valid_inbound_role(message.value)) is False:
                    continue

                openai_res = self.get_openai_response(message.value)

                outbound_messages = self.parse_openai_res(openai_res)
                self.send_messages_outbound(outbound_messages)

                self.incresement_message_counter()
                if self.message_counter > self.message_threshold:
                    print("Unsubscribing from topic: %s", self.sub_topic_name)
                    self.consumer.unsubscribe()
                    break

        except Exception as error:
            logging.error("Error subscribing to topic: %s", self.sub_topic_name)
            logging.error(error)
            self.consumer.unsubscribe()