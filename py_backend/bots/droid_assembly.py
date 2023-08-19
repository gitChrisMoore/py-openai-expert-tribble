import logging
import json
from py_backend.bots.AIBaseClass import AIBaseClassFunctions, AIFlatten
from py_backend.bots.BlueprintClass import (
    BlueprintClass,
    FunctionSchema,
    ParameterSchema,
)
from py_backend.storage.db_blueprint import load_blueprint_by_id
from py_backend.storage.db_objective import load_objective_by_id
from dataclasses import asdict


logging.getLogger("droid_assembly").setLevel(logging.WARNING)
log = logging.getLogger("droid_assembly")


def load_blueprint_and_objective(blueprint_id, objective_id):
    """Load the blueprint and objective from the database by their IDs."""
    res_status_blueprint, blueprint = load_blueprint_by_id(blueprint_id)
    res_status_objective, objective = load_objective_by_id(objective_id)

    if not res_status_blueprint:
        error_msg = f"Failed to load blueprint with ID: {blueprint_id}"
        log.error(error_msg)
        raise ValueError(error_msg)

    if not res_status_objective:
        error_msg = f"Failed to load objective with ID: {objective_id}"
        log.error(error_msg)
        raise ValueError(error_msg)

    return blueprint, objective


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


def create_function_from_objective(objective):
    """Model and create the AI functions data scehma from the objective data"""
    # Check if required keys exist in the objective
    required_keys = ["parameters", "objective_name", "objective_description"]
    for key in required_keys:
        if key not in objective:
            logging.error(f"Key '{key}' missing in objective data.")
            return None

    try:
        par = asdict(ParameterSchema(objective["parameters"]))
        # print("par", par["properties"])
        print("asdasd", json.loads(objective["parameters"])["properties"])
        # fun = asdict(
        #     FunctionSchema(
        #         name=objective["objective_name"],
        #         description=objective["objective_description"],
        #         parameters=par,  # type: ignore
        #     )
        # )
        fun = {
            "name": objective["objective_name"],
            "description": objective["objective_description"],
            "parameters": {
                "type": "object",
                "properties": json.loads(objective["parameters"])["properties"],
            },
        }
        return fun

    except TypeError as err:
        logging.error(
            "Issue with the data format when creating function from objective: %s", err
        )
    except ValueError as err:
        logging.error("Invalid value provided in objective data: %s", err)
    except Exception as err:
        logging.error(
            "Unexpected error occurred while creating function from objective: %s", err
        )

    return None


def initialize_ai_bot(bp, fun):
    """Assign the droid to the right AIBaseClass method"""
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

        bot = AIBaseClassFunctions(
            source_id=bp.blueprint_name,
            sub_topic_name=bp.sub_topic_name,
            pub_topic_name=bp.pub_topic_name,
            inital_openai_messages=json.loads(bp.initial_context),
            functions=[fun],
            function_name=fun["name"],
            valid_schema=fun["parameters"],
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


def initialize_ai_bot_flatten(bp, fun):
    """Assign the droid to the right AIBaseClass method"""
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

        bot = AIFlatten(
            source_id=bp.blueprint_name,
            sub_topic_name=bp.sub_topic_name,
            pub_topic_name=bp.pub_topic_name,
            inital_openai_messages=json.loads(bp.initial_context),
            functions=[fun],
            function_name=fun["name"],
            valid_schema=fun["parameters"],
            ignored_roles=bp.ignored_roles,
            source_type=bp.source_type,
            ignored_source_types=bp.ignored_source_types,
        )

        return bot

    except (AttributeError, KeyError) as err:
        logging.error(err)
    except Exception as err:
        logging.error("Unexpected error occurred during AI bot initialization: %s", err)

    return None


def run_droid(blueprint_id, objective_id):
    """Run the droid based on the provided blueprint and objective IDs."""
    blueprint, objective = load_blueprint_and_objective(blueprint_id, objective_id)

    # Create Blueprint instance
    bp = create_blueprint_instance(blueprint)

    # Create function from objective
    function = create_function_from_objective(objective)

    # Initialize the AI bot
    bot = initialize_ai_bot_flatten(bp, function)

    if bot:
        print(f"Starting AI: {bot.source_id}")
        bot.run()
        print(f"Shutting down AI: {bot.source_id}")
