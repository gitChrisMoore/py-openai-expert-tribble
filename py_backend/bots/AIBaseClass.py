import json
import logging
import re
from jsonschema import validate
from dotenv import load_dotenv
from py_backend.open_ai.openai_connection import (
    send_openai_functions_two,
)
from py_backend.utils.kafka_conn import create_kafka_consumer, create_kafka_producer


load_dotenv()
BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]


def extract_json_objects(json_string):
    """Extract JSON objects from a string"""
    # Regular expression pattern for identifying JSON objects
    pattern = r"\{[^{}]*\}"
    json_objects = []

    # Find all matches of the pattern
    for match in re.findall(pattern, json_string):
        # Try to parse the JSON string, add it to the list if successful
        try:
            json_object = json.loads(match)
            json_objects.append(json_object)
        except json.JSONDecodeError:
            continue  # Ignore JSON decoding errors

    return json_objects


class AIBaseClass:
    """AI Parent Base Class

    * Recieve messages from a Kafka topic
    * Send messages to a OpenAI API
    * Recieve messages from a OpenAI API
    * Send messages to a Kafka topic

    """

    def __init__(
        self,
        source_id,
        sub_topic_name,
        pub_topic_name,
        inital_openai_messages,
        functions,
        function_name,
        valid_schema,
        message_counter=0,
        message_threshold=5,
    ):
        self.consumer = create_kafka_consumer()
        self.producer = create_kafka_producer()
        self.sub_topic_name = sub_topic_name
        self.pub_topic_name = pub_topic_name
        self.source_id = source_id
        self.inital_openai_messages = inital_openai_messages
        self.functions = functions
        self.function_name = function_name
        self.valid_schema = valid_schema
        self.message_counter = message_counter
        self.message_threshold = message_threshold

    def subscribe_to_topic(self):
        """Subscribe to a Kafka topic"""
        try:
            self.consumer.subscribe([self.sub_topic_name])
            print(
                f"{self.source_id}: subscribe_to_topic - success - {self.sub_topic_name}"
            )
        except Exception as error:
            print(
                f"{self.source_id}: subscribe_to_topic - error - {self.sub_topic_name}"
            )
            logging.error(error)

    def is_valid_inbound_source_id(self, payload):
        """Check if the inbound source_id is valid"""
        if "consumer_id" not in payload:
            logging.warning("Message does not have a source_id: %s", payload)
            return False

        if payload["consumer_id"] == self.source_id:
            logging.info("Message is from the same source_id, ignoring: %s", payload)
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

    def set_openai_query(self, inbound_message):
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
        return _messages

    def fetch_data(self, openai_query):
        """Get the OpenAI response"""
        try:
            res = send_openai_functions_two(
                messages=openai_query,
                functions=self.functions,
                function_name=self.function_name,
            )
            arguments_raw = res["choices"][0]["message"]["function_call"]["arguments"]
            arguments = json.loads(arguments_raw)
            print(f"{self.source_id}: fetch_data - success")
            return arguments
        except Exception as error:
            print(f"{self.source_id}: fetch_data - {error}")
            print(f"{self.source_id}: fetch_data - {arguments_raw}")
            return None

    def format_outbound_messages(self, data):
        """Prepare the outbound messages"""
        try:
            validate(instance=data, schema=self.valid_schema)
            res = [{"source_id": self.source_id, "role": "ai_bot", "payload": data}]
            return res
        except Exception as error:
            print(f"{self.source_id}: format_outbound_messages - {error}")

    def send_messages_outbound(self, msgs):
        """Send messages to the Kafka topic"""
        print(f"{self.source_id}: send_messages_outbound - {msgs}")
        try:
            for msg in msgs:
                self.producer.send(self.pub_topic_name, value=msg)
        except Exception as error:
            print(f"{self.source_id}: send_messages_outbound - {error}")

    def run(self):
        """Run the AI"""

        self.subscribe_to_topic()

        for message in self.consumer:
            # handle_inbound_message
            if (self.is_valid_inbound_source_id(message.value)) is False:
                continue
            if (self.is_valid_inbound_role(message.value)) is False:
                continue
            openai_query = self.set_openai_query(message.value)

            response = self.fetch_data(openai_query)

            outbound_messages = self.format_outbound_messages(response)

            self.send_messages_outbound(outbound_messages)

            # Self Counter
            self.message_counter += 1
            if self.message_counter > self.message_threshold:
                print("Unsubscribing from topic: %s", self.sub_topic_name)
                self.consumer.unsubscribe()
                break


class AIFlatten(AIBaseClass):
    """AI Parent Base Class

    * Recieve messages from a Kafka topic
    * Send messages to a OpenAI API
    * Recieve messages from a OpenAI API
    * Send messages to a Kafka topic

    """

    def __init__(
        self,
        source_id,
        sub_topic_name,
        pub_topic_name,
        inital_openai_messages,
        functions,
        function_name,
        valid_schema,
    ):
        super().__init__(
            source_id,
            sub_topic_name,
            pub_topic_name,
            inital_openai_messages,
            functions,
            function_name,
            valid_schema,
        )

    def fetch_data(self, openai_query):
        """Get the OpenAI response"""
        try:
            res = send_openai_functions_two(
                messages=openai_query,
                functions=self.functions,
                function_name=self.function_name,
            )
            function_call_raw = res["choices"][0].to_dict()["message"]["function_call"]
            arguments = extract_json_objects(function_call_raw["arguments"])

            return arguments
        except Exception as error:
            print(f"{self.source_id}: fetch_data - error {error}")
            print(f"{self.source_id}: fetch_data - openai_query - {openai_query}")
            return None

    def format_outbound_messages(self, data):
        """Prepare the outbound messages"""
        try:
            res = []
            for msg in data:
                print(f"{self.source_id}: format_outbound_messages - {msg}")
                validate(instance=msg, schema=self.valid_schema)
                res.append(
                    {
                        "source_id": self.source_id,
                        "role": "ai_bot",
                        "payload": msg,
                    }
                )
            return res
        except Exception as error:
            print(f"{self.source_id}: format_outbound_messages - {error}")
