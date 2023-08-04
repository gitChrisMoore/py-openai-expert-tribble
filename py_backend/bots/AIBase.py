import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from py_backend.bots.persona.persona_schema import persona_schema
from py_backend.open_ai.openai_connection import (
    send_openai_functions_two,
    send_openai_messages,
    send_openai_functions,
)
import logging
from jsonschema import validate
from py_backend.utils.kafka_conn import create_kafka_consumer, create_kafka_producer


load_dotenv()
BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]


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
        self.consumer = create_kafka_consumer()
        self.producer = create_kafka_producer()
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
            logging.info("Message is from the same consumer_id, ignoring: %s", payload)
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

    def get_openai_response(self, openai_query):
        """Get the OpenAI response"""
        try:
            res = send_openai_messages(openai_query)
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

                openai_query = self.set_openai_query(message.value)
                openai_res = self.get_openai_response(openai_query)

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


class AIFunctionsClass(AIMessageBaseClass):
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
        functions,
        function_name,
        custom_openai_res_parser,
    ):
        super().__init__(
            consumer_id, sub_topic_name, pub_topic_name, inital_openai_messages
        )
        self.functions = functions
        self.function_name = function_name
        self.custom_openai_res_parser = custom_openai_res_parser

    def is_valid_inbound_role(self, payload):
        """Check if the inbound role is valid"""
        if "role" not in payload:
            logging.warning("Payload is missing a role: %s", payload)
            return False

        if payload["role"] == "user":
            logging.info("Payload is a user, ignorring: %s", payload)
            return False

        if payload["role"] == "system":
            logging.info("Payload is a system, ignorring: %s", payload)
            return False

    def handle_openai_response_custom(self, openai_response):
        """Function that handles the response from OpenAI"""
        try:
            arguments_raw = openai_response["choices"][0]["message"]["function_call"][
                "arguments"
            ]
            arguments = json.loads(arguments_raw)
            print("handle_response_custom: success - parsed openai_response")
            res = arguments["trends"]
            print("handle_response_custom: success - parsed records: ", str(len(res)))
            return res
        except Exception as error:
            print("handle_response_custom: error in parsing response")
            print(error)
            print("handle_response_custom: ", openai_response)

    def get_openai_response(self, openai_query):
        """Get the OpenAI response"""
        try:
            res = send_openai_functions(
                messages=openai_query,
                functions=self.functions,
                function_name=self.function_name,
                prase_response=self.handle_openai_response_custom,
            )
            print(f"{self.consumer_id}: get_openai_response - success")
            return res
        except Exception as error:
            print(f"{self.consumer_id}: get_openai_response - error")
            print(f"{self.consumer_id}: get_openai_response - {error}")
            print(
                f"{self.consumer_id}: get_openai_response - openai_query - {openai_query} "
            )
            return None

    def parse_openai_res(self, openai_res):
        """Parse the OpenAI response"""
        res = self.custom_openai_res_parser(openai_res, self.consumer_id)
        return res


class AIFunctionsClassTwo(AIMessageBaseClass):
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
        functions,
        function_name,
        custom_openai_res_parser,
    ):
        super().__init__(
            consumer_id, sub_topic_name, pub_topic_name, inital_openai_messages
        )
        self.functions = functions
        self.function_name = function_name
        self.custom_openai_res_parser = custom_openai_res_parser

    def is_valid_inbound_role(self, payload):
        """Check if the inbound role is valid"""
        if "role" not in payload:
            logging.warning("Payload is missing a role: %s", payload)
            return False

        if payload["role"] == "user":
            logging.info("Payload is a user, ignorring: %s", payload)
            return False

        if payload["role"] == "system":
            logging.info("Payload is a system, ignorring: %s", payload)
            return False

    def handle_openai_response_custom(self, openai_response):
        """Function that handles the response from OpenAI"""
        try:
            arguments_raw = openai_response["choices"][0]["message"]["function_call"][
                "arguments"
            ]
            arguments = json.loads(arguments_raw)
            print(f"{self.consumer_id}: handle_openai_response_custom - success")
            print(f"{self.consumer_id}: handle_openai_response_custom - {arguments}")
        except Exception as error:
            print("handle_response_custom: error in parsing response")
            print(error)
            print("handle_response_custom: ", openai_response)

        try:
            validate(instance=arguments, schema=persona_schema)

            print(f"{self.consumer_id}: handle_openai_response_custom - success")
        except Exception as error:
            print(f"{self.consumer_id}: handle_openai_response_custom - error")
            print(f"{self.consumer_id}: handle_openai_response_custom - {error}")

    def get_openai_response(self, openai_query):
        """Get the OpenAI response"""
        try:
            res = send_openai_functions_two(
                messages=openai_query,
                functions=self.functions,
                function_name=self.function_name,
            )
            print(f"{self.consumer_id}: get_openai_response - success")
            return res
        except Exception as error:
            print(f"{self.consumer_id}: get_openai_response - {error}")
            return None

    def parse_openai_res(self, openai_res):
        """Parse the OpenAI response"""
        res = self.custom_openai_res_parser(openai_res, self.consumer_id)
        return res
