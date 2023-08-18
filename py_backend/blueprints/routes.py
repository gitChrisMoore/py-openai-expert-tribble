import json
from flask import jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from py_backend.blueprints import bp
from py_backend.storage.db_models import Blueprint, Objective

DB_FILEPATH = "py_backend/storage/data_base.db"


def update_blueprint_logic(blueprint_data, blueprint_id):
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    blueprint = session.query(Blueprint).filter_by(blueprint_id=blueprint_id).first()
    if not blueprint:
        return jsonify(error="Blueprint not found"), 404

    # Check for each field in blueprint_data if it exists and is not None, then update
    if blueprint_data.get("blueprint_name") is not None:
        blueprint.blueprint_name = blueprint_data.blueprint_name

    if blueprint_data.get("blueprint_description") is not None:
        blueprint.blueprint_description = blueprint_data.blueprint_description

    if blueprint_data.get("sub_topic_name") is not None:
        blueprint.sub_topic_name = blueprint_data.sub_topic_name

    if blueprint_data.get("pub_topic_name") is not None:
        blueprint.pub_topic_name = blueprint_data.pub_topic_name

    if blueprint_data.get("initial_context") is not None:
        blueprint.initial_context = blueprint_data.initial_context

    # Updating related objectives
    objectives_data = blueprint_data.get("objectives", [])
    if objectives_data:
        new_objective_ids = [
            obj_data["objective_id"]
            for obj_data in objectives_data
            if obj_data["objective_id"] is not None
        ]
        new_objectives = (
            session.query(Objective)
            .filter(Objective.objective_id.in_(new_objective_ids))
            .all()
        )
        blueprint.blueprint_objectives = new_objectives

    session.commit()

    # Fetch the updated blueprint for the response
    blueprint = session.query(Blueprint).filter_by(blueprint_id=blueprint_id).first()
    blueprint_json = blueprint_to_json(blueprint)

    return jsonify(blueprint_json), 200


def blueprint_to_json(blueprint):
    """Converts a Blueprint instance into a JSON-serializable format."""
    return {
        "blueprint_id": blueprint.blueprint_id,
        "blueprint_name": blueprint.blueprint_name,
        "blueprint_description": blueprint.blueprint_description,
        "sub_topic_name": blueprint.sub_topic_name,
        "pub_topic_name": blueprint.pub_topic_name,
        "initial_context": json.loads(blueprint.initial_context),  # type: ignore
        "objectives": [
            {
                "objective_id": obj.objective_id,
            }
            for obj in blueprint.blueprint_objectives
        ],
    }


def json_to_blueprint(json_data):
    """Converts JSON data into a Blueprint instance."""

    # Extracting objectives
    objectives = [
        Objective(objective_id=obj["objective_id"]) for obj in json_data["objectives"]
    ]

    # Creating a Blueprint instance
    blueprint = Blueprint(
        blueprint_id=json_data["blueprint_id"],
        blueprint_name=json_data["blueprint_name"],
        blueprint_description=json_data["blueprint_description"],
        sub_topic_name=json_data["sub_topic_name"],
        pub_topic_name=json_data["pub_topic_name"],
        initial_context=json.dumps(
            json_data["initial_context"]
        ),  # Assuming initial_context is a JSON string
        blueprint_objectives=objectives,
    )

    return blueprint


@bp.route("/", methods=["GET"])
def get_blueprints():
    """Returns all blueprints from the database."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        # Query all blueprints from the database
        blueprints = session.query(Blueprint).all()

        # Convert blueprints into a JSON-serializable format
        blueprints_json = [blueprint_to_json(bp) for bp in blueprints]
        return jsonify(blueprints_json), 200
    except Exception as error:
        # Handle unexpected errors
        print(str(error))
        return jsonify({"error": "An error occurred while fetching blueprints"}), 500
    finally:
        # Close the session
        session.close()


@bp.route("/<string:blueprint_id>", methods=["GET"])
def get_blueprint_by_id(blueprint_id):
    """Returns a single blueprint from the database by ID."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        blueprint = (
            session.query(Blueprint).filter_by(blueprint_id=blueprint_id).first()
        )
        if blueprint is None:
            return jsonify({"error": "Blueprint not found"}), 404

        blueprint_json = blueprint_to_json(blueprint)
        return jsonify(blueprint_json), 200
    except Exception as error:
        # Handle unexpected errors
        print(str(error))
        return jsonify({"error": "An error occurred while fetching the blueprint"}), 500
    finally:
        # Close the session
        session.close()


@bp.route("/<string:blueprint_id>", methods=["PUT"])
def update_blueprint(blueprint_id):
    """Updates a single blueprint in the database by ID."""
    # engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    # session = Session(engine)

    print(request.json)
    try:
        data = request.json
        if data is None:
            return jsonify(error="Invalid JSON data"), 400

        blueprint_id = data.get("blueprint_id")
        if blueprint_id is None:
            return jsonify(error="Missing blueprint_id"), 400

        # blueprint = (
        # session.query(Blueprint).filter_by(blueprint_id=blueprint_id).first()
        # )
        # if not blueprint:
        # return jsonify(error="Blueprint not found"), 404

        blueprint_data = json_to_blueprint(request.json)

        return update_blueprint_logic(blueprint_data, blueprint_id)

        # blueprint.blueprint_name = blueprint_data.blueprint_name
        # blueprint.blueprint_description = blueprint_data.blueprint_description
        # blueprint.sub_topic_name = blueprint_data.sub_topic_name
        # blueprint.pub_topic_name = blueprint_data.pub_topic_name
        # blueprint.initial_context = blueprint_data.initial_context

        # # Updating related objectives
        # objectives_data = data.get("objectives", [])
        # new_objective_ids = [obj_data["objective_id"] for obj_data in objectives_data]
        # new_objectives = (
        #     session.query(Objective)
        #     .filter(Objective.objective_id.in_(new_objective_ids))
        #     .all()
        # )
        # blueprint.blueprint_objectives = new_objectives

        # session.commit()
        # # Fetch the updated blueprint for the response
        # blueprint = (
        #     session.query(Blueprint).filter_by(blueprint_id=blueprint_id).first()
        # )
        # blueprint_json = blueprint_to_json(blueprint)

        # return jsonify(blueprint_json), 200

    except Exception as error:
        # Handle unexpected errors
        print(str(error))
        return jsonify({"error": "An error occurred while updating the blueprint"}), 500
    finally:
        # Close the session
        # session.close()
        pass
