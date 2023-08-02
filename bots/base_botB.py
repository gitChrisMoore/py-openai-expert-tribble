import json
import logging
from kafka import KafkaProducer, KafkaConsumer

logging.basicConfig(level=logging.WARNING)


# For the Upstash
BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]
UPSTASH_KAFKA_USERNAME = (
    "dXAtb3NwcmV5LTYyMzAkV7cVY7Mr0DNHEu63FYKy6PM4oFFHUhEhy9WDO_FOYmc"
)
UPSTASH_KAFKA_PASSWORD = "72784a0f2d7647e58185136ceb50a30b"
TOPIC_NAME = "prod-strategy-market_size"


class BaseBotB:
    """Base Bot Class

    This class consumes messages from a Kafka topic, sends the message to the
    OpenAI API, and then sends the response back to the Kafka topic.

    This Class should only send messages to OpenAI if the consumer_id exists
    and the consumer_id is not the same as the current consumer_id.


    Attributes:
        topic_name: The topic name to subscribe to.
        consumer_id: The consumer_id of the current consumer.
        send_message: The function that sends messages to OpenAI.

    """

    def __init__(
        self,
        consumer_id,
        sub_topic_name,
        pub_topic_name,
        send_message,
        message_threshold=5,
    ):
        self.consumer = KafkaConsumer(
            bootstrap_servers=BOOTSTRAP_ENDPOINT,
            sasl_mechanism="SCRAM-SHA-512",
            security_protocol="SASL_SSL",
            sasl_plain_username=UPSTASH_KAFKA_USERNAME,
            sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
        )
        self.producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_ENDPOINT,
            sasl_mechanism="SCRAM-SHA-512",
            security_protocol="SASL_SSL",
            sasl_plain_username=UPSTASH_KAFKA_USERNAME,
            sasl_plain_password=UPSTASH_KAFKA_PASSWORD,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.sub_topic_name = sub_topic_name
        self.pub_topic_name = pub_topic_name
        self.consumer_id = consumer_id
        self.send_message = send_message
        self.message_counter = 0
        self.message_threshold = message_threshold

    def parse_payload(self, payload):
        """Parse the JSON payload"""
        try:
            res = json.loads(payload)
            logging.info("Parsed JSON payload: %s", res)
            return res
        except ValueError as error:
            logging.error("Error parsing JSON payload: %s, payload: %s", error, payload)
            return None

    def parse_openai_res(self, openia_res):
        """Parse the OpenAI response"""
        messages = []
        for i in openia_res:
            messages.append(
                {
                    "role": "assistant",
                    "title": i["title"],
                    "implication": i["implication"],
                }
            )
        return messages

    def send_messages(self, messages):
        """Send messages to the Kafka topic"""
        for message in messages:
            self.producer.send(self.pub_topic_name, message)
            logging.info(
                "Sent message to topic: %s, message: %s", self.pub_topic_name, message
            )

    def is_valid_payload(self, payload):
        """Check if the payload is valid"""

        if "consumer_id" not in payload:
            logging.warning("Message does not have a consumer_id: %s", payload)
            return False

        if payload["consumer_id"] == self.consumer_id:
            logging.warning(
                "Message is from the same consumer_id, ignoring: %s", payload
            )
            return False

        if "role" not in payload:
            logging.warning("Payload is missing a role: %s", payload)
            return False

        if payload["role"] == "user":
            logging.info("Payload is a user, ignorring: %s", payload)
            return False

        if payload["role"] == "system":
            logging.info("Payload is a system, ignorring: %s", payload)
            return False

        if "content" not in payload:
            logging.warning("Payload is missing a content: %s", payload)
            return False

        return True

    def run(self):
        """Creates a consumer and subscribes to the specified topic name.
        When messages are received, they are parsed a dictionary and printed.
        """
        try:
            self.consumer.subscribe([self.sub_topic_name])
            # log consumer_id is listening for messages on sub_topic_name
            logging.info(
                "Consumer ID: %s is listening for messages on topic: %s",
                self.consumer_id,
                self.sub_topic_name,
            )

            # use a generator instead of a list to store the messages in the Kafka topic
            for message in self.consumer:
                # parse kafka message into dict
                kafka_message = self.parse_payload(message.value.decode("utf-8"))

                if self.is_valid_payload(kafka_message) is False:
                    continue

                openai_res = self.send_message(
                    [
                        {
                            "role": kafka_message["role"],
                            "content": kafka_message["content"],
                        }
                    ]
                )

                if openai_res is None:
                    logging.warning("openai_res is None")
                    continue

                producer_messages = self.parse_openai_res(openai_res)

                self.send_messages(producer_messages)

                # unsubscribe if the counter is greater than the threshold, else increment the counter
                if self.message_counter > self.message_threshold:
                    print("Unsubscribing from topic: %s", self.sub_topic_name)
                    self.consumer.unsubscribe()
                    break
                else:
                    print("Message counter: %s", self.message_counter)
                    self.message_counter += 1

        except KeyboardInterrupt:
            logging.info("Consumer stopped.")
            self.consumer.close()
        except Exception as error:
            logging.error("Error in AI_Bot run: %s", error)