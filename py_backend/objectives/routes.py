import json
from flask import jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from py_backend.objectives import bp
from py_backend.storage.db_models import Objective

DB_FILEPATH = "py_backend/storage/data_base.db"


def objective_to_json(objective):
    """Converts an Objective instance to a JSON-serializable dictionary."""
    return {
        "objective_id": objective.objective_id,
        "objective_name": objective.objective_name,
        "objective_description": objective.objective_description,
        "parameters": json.loads(objective.parameters),
    }


@bp.route("/", methods=["GET"])
def get_objectives():
    """Returns all objectives from the database."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        # Query all objectives from the database
        objectives = session.query(Objective).all()

        # Convert objectives into a JSON-serializable format
        objectives_json = [objective_to_json(obj) for obj in objectives]
        return jsonify(objectives_json), 200
    except Exception as error:
        # Handle unexpected errors
        print(str(error))
        return jsonify({"error": "An error occurred while fetching objectives"}), 500
    finally:
        # Close the session
        session.close()
