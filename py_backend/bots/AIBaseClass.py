import json
import logging
import re
from jsonschema import validate
from dotenv import load_dotenv
from py_backend.open_ai.openai_connection import (
    send_openai_functions_two,
    send_openai_functions_three,
)
from py_backend.utils.kafka_conn import create_kafka_consumer, create_kafka_producer
from py_backend.utils.supabase import write_to_supabase

logging.basicConfig(level=logging.WARNING)

logging.getLogger("ai_base_class").setLevel(logging.WARNING)
log = logging.getLogger("ai_base_class")

load_dotenv()
BOOTSTRAP_ENDPOINT = ["up-osprey-6230-us1-kafka.upstash.io:9092"]


def extract_json_objects(json_string):
    """Extract JSON objects from responses that get cut off"""
    pattern = r"\{[^{}]*\}"
    return [
        json.loads(match)
        for match in re.findall(pattern, json_string)
        if json.loads(match)
    ]


def update_roles(objects):
    """Replace the role of the AI bot with user"""
    return [
        {**obj, "role": "user"} if obj.get("role") == "ai_bot" else obj
        for obj in objects
    ]


class AIBaseClass:
    """AI Parent Base Class"""

    def __init__(
        self,
        source_id,
        sub_topic_name,
        pub_topic_name,
        inital_openai_messages,
        ignored_roles,
        ignored_source_types,
        message_counter=0,
        message_threshold=10,
        source_type="conversational",
    ):
        self.consumer = create_kafka_consumer()
        self.producer = create_kafka_producer()
        self.sub_topic_name = sub_topic_name
        self.pub_topic_name = pub_topic_name
        self.source_id = source_id
        self.inital_openai_messages = inital_openai_messages
        self.message_counter = message_counter
        self.message_threshold = message_threshold
        self.ignored_roles = ignored_roles or ["system"]
        self.source_type = source_type
        self.ignored_source_types = ignored_source_types

    def subscribe_to_topic(self):
        try:
            self.consumer.subscribe([self.sub_topic_name])
            log.info(
                "%s: subscribe_to_topic - success - %s",
                self.source_id,
                self.sub_topic_name,
            )
        except Exception as err:
            log.error(
                "%s: subscribe_to_topic - error - %s - %s",
                self.source_id,
                self.sub_topic_name,
                err,
            )

    def is_valid_inbound_source_id(self, payload):
        """Check if the inbound source_id is valid"""
        if "source_id" not in payload:
            log.warning("Message does not have a source_id: %s", payload)
            return False

        if payload["source_id"] == self.source_id:
            log.info("Message is from the same source_id, ignoring: %s", payload)
            return False

        return True

    def is_valid_inbound_role(self, payload):
        """Check if the inbound role is valid"""
        if "role" not in payload:
            log.warning("Payload is missing a role: %s", payload)
            return False

        if payload["role"] in self.ignored_roles:
            log.info(
                "Payload has an ignored role %s, ignoring: %s", payload["role"], payload
            )
            return False

        log.info("%s: is_valid_inbound_role - success - %s", self.source_id, payload)
        return True

    def is_valid_inbound_source_type(self, payload):
        """Check if the inbound source_type is valid"""

        if (
            "source_type" in payload
            and payload["source_type"] in self.ignored_source_types
        ):
            log.info(
                "Payload has an ignored source_type %s, ignoring: %s",
                payload["source_type"],
                payload,
            )
            return False

        log.info(
            "%s: is_valid_inbound_source_type - success - %s", self.source_id, payload
        )
        return True

    def set_openai_query(self, inbound_message):
        """Get the OpenAI response"""
        _messages = []
        _messages.extend(self.inital_openai_messages)
        new_messages = [
            {
                "role": inbound_message["role"],
                "content": inbound_message["payload"],
            }
        ]
        _messages.extend(new_messages)
        return _messages

    def fetch_data(self, openai_query):
        """Get the OpenAI response"""
        try:
            # Sending the OpenAI query and getting the response
            response = send_openai_functions_three(messages=openai_query)

            # Writing the response to the database
            write_to_supabase(response, self.source_id)

            # Extracting the message content
            message_content = response["choices"][0]["message"]["content"]  # type: ignore

            # Logging the successful fetch
            log.info(
                "%s: fetch_data - return response from openai_query - %s",
                self.source_id,
                message_content,
            )
            return message_content
        except Exception as err:
            # Logging the error and returning None
            log.error(
                "%s: fetch_data - error - %s - %s",
                self.source_id,
                openai_query,
                err,
            )
            return None

    def format_outbound_messages(self, data):
        """Prepare the outbound messages"""
        # TODO: Add a check to see if the data is None
        try:
            res = [
                {
                    "source_id": self.source_id,
                    "source_type": self.source_type,
                    "role": "assistant",
                    "payload": data,
                }
            ]
            log.info(
                "%s: format_outbound_messages - %s",
                self.source_id,
                res,
            )
            return res
        except Exception as err:
            log.error(
                "%s: format_outbound_messages - error - %s",
                self.source_id,
                err,
            )

    def send_messages_outbound(self, msgs):
        """Send messages to the Kafka topic"""
        log.info(
            "%s: send_messages_outbound - %s",
            self.source_id,
            self.pub_topic_name,
        )

        try:
            for msg in msgs:
                self.producer.send(self.pub_topic_name, value=msg)
                log.info(
                    "%s: send_messages_outbound - success - %s",
                    self.source_id,
                    msg,
                )

        except Exception as err:
            log.error(
                "%s: send_messages_outbound - error - %s - %s",
                self.source_id,
                self.pub_topic_name,
                err,
            )

    def run(self):
        """Run the AI"""

        self.subscribe_to_topic()

        for message in self.consumer:
            # handle_inbound_message
            if (self.is_valid_inbound_source_id(message.value)) is False:
                continue
            if (self.is_valid_inbound_role(message.value)) is False:
                continue
            if (self.is_valid_inbound_source_type(message.value)) is False:
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


class AIBaseClassFunctions(AIBaseClass):
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
        ignored_roles,
        ignored_source_types,
        source_type,
        functions,
        function_name,
        valid_schema,
        message_counter=0,
        message_threshold=5,
    ):
        super().__init__(
            source_id,
            sub_topic_name,
            pub_topic_name,
            inital_openai_messages,
            ignored_roles,
            source_type,
            ignored_source_types,
        )
        self.functions = functions
        self.function_name = function_name
        self.valid_schema = valid_schema
        self.message_counter = message_counter
        self.message_threshold = message_threshold

    def fetch_data(self, openai_query):
        """Get the OpenAI response"""
        try:
            updated_openai_query = update_roles(openai_query)
            res = send_openai_functions_two(
                messages=updated_openai_query,
                functions=self.functions,
                function_name=self.function_name,
            )
            write_to_supabase(res, self.source_id)
            arguments_raw = res["choices"][0]["message"]["function_call"]["arguments"]  # type: ignore
            arguments = json.loads(arguments_raw)
            log.info(
                "%s: fetch_data - return response from openai_query - %s",
                self.source_id,
                arguments,
            )
            return arguments
        except Exception as error:
            log.error(
                "%s: fetch_data - error - %s - %s",
                self.source_id,
                openai_query,
                error,
            )
            return None


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
        ignored_roles,
        ignored_source_types,
        source_type,
        functions,
        function_name,
        valid_schema,
        message_counter=0,
        message_threshold=5,
    ):
        super().__init__(
            source_id,
            sub_topic_name,
            pub_topic_name,
            inital_openai_messages,
            ignored_roles,
            source_type,
            ignored_source_types,
        )
        self.functions = functions
        self.function_name = function_name
        self.valid_schema = valid_schema
        self.message_counter = message_counter
        self.message_threshold = message_threshold

    def fetch_data(self, openai_query):
        """Get the OpenAI response"""
        try:
            updated_openai_query = update_roles(openai_query)
            res = send_openai_functions_two(
                messages=updated_openai_query,
                functions=self.functions,
                function_name=self.function_name,
            )

            write_to_supabase(res, self.source_id)
            function_call_raw = res["choices"][0].to_dict()["message"]["function_call"]  # type: ignore
            arguments = extract_json_objects(function_call_raw["arguments"])
            log.info(
                "%s: fetch_data - return response from openai_query - %s",
                self.source_id,
                arguments,
            )
            return arguments
        except Exception as error:
            log.error(
                "%s: fetch_data - error - %s - %s",
                self.source_id,
                openai_query,
                error,
            )

            return None

    def format_outbound_messages(self, data):
        """Prepare the outbound messages"""
        try:
            res = []
            for msg in data:
                validate(instance=msg, schema=self.valid_schema)
                res.append(
                    {
                        "source_id": self.source_id,
                        "source_type": self.source_type,
                        "role": "ai_bot",
                        "payload": msg,
                    }
                )
                log.info(
                    "%s: format_outbound_messages - success - %s",
                    self.source_id,
                    msg,
                )
            return res
        except Exception as error:
            log.error(
                "%s: format_outbound_messages - error - %s - %s",
                self.source_id,
                data,
                error,
            )
