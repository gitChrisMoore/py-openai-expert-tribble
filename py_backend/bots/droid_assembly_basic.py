import logging
import json
from py_backend.bots.AIBaseClass import AIBaseClass
from py_backend.bots.BlueprintClass import (
    BlueprintClass,
)
from py_backend.storage.db_blueprint import load_blueprint_by_id


logging.getLogger("droid_assembly").setLevel(logging.WARNING)
log = logging.getLogger("droid_assembly")


def load_blueprint(blueprint_id):
    """Load the blueprint and objective from the database by their IDs."""
    res_status_blueprint, blueprint = load_blueprint_by_id(blueprint_id)

    if not res_status_blueprint:
        error_msg = f"Failed to load blueprint with ID: {blueprint_id}"
        log.error(error_msg)
        raise ValueError(error_msg)

    return blueprint


def create_blueprint_instance(blueprint):
    """Create the blueprint instance from the blueprint data"""
    try:
        bp_instance = BlueprintClass(**blueprint)
        return bp_instance
    except TypeError as err:
        print.error("There was an issue with the blueprint data format: %s", err)
    except ValueError as err:
        logging.error("Invalid value provided in blueprint data: %s", err)
    except Exception as err:  # This should be the catch-all for any unexpected errors
        logging.error(
            "An unexpected error occurred while creating the blueprint instance: %s",
            err,
        )


def initialize_bot_basic(bp):
    try:
        # Check if required attributes/keys are present in bp and fun
        required_bp_attributes = [
            "blueprint_name",
            "sub_topic_name",
            "pub_topic_name",
            "initial_context",
            "ignored_roles",
            "source_type",
            "ignored_source_types",
        ]

        for attr in required_bp_attributes:
            if not hasattr(bp, attr):
                raise AttributeError(f"'{attr}' is missing from the blueprint object.")

        bot = AIBaseClass(
            source_id=bp.blueprint_name,
            sub_topic_name=bp.sub_topic_name,
            pub_topic_name=bp.pub_topic_name,
            inital_openai_messages=json.loads(bp.initial_context),
            ignored_roles=bp.ignored_roles,
            source_type="functional",
            ignored_source_types=bp.ignored_source_types,
        )

        return bot

    except (AttributeError, KeyError) as err:
        logging.error(err)
    except Exception as err:
        logging.error("Unexpected error occurred during AI bot initialization: %s", err)

    return None


def run_droid_basic(blueprint_id):
    """Run the droid based on the provided blueprint and objective IDs."""
    print(f"Loading blueprint with ID: {blueprint_id}")
    blueprint = load_blueprint(blueprint_id)

    # Create Blueprint instance
    bp = create_blueprint_instance(blueprint)

    # Initialize the AI bot
    bot = initialize_bot_basic(bp)

    if bot:
        print(f"Starting AI: {bot.source_id}")
        bot.run()
        print(f"Shutting down AI: {bot.source_id}")
