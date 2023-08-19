import json
from sqlalchemy import create_engine

from sqlalchemy.orm import Session, joinedload
from py_backend.storage.db_models import Blueprint
from py_backend.storage.db_utils import object_as_dict


DB_FILEPATH = "py_backend/storage/data_base.db"


def save_blueprint(blueprint_data):
    """Saves a blueprint to the database."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        blueprint = Blueprint(
            blueprint_name=blueprint_data["blueprint_name"],
            blueprint_description=blueprint_data["blueprint_description"],
            sub_topic_name=blueprint_data["sub_topic_name"],
            pub_topic_name=blueprint_data["pub_topic_name"],
            initial_context=json.dumps(blueprint_data["initial_context"]),
        )
    except Exception as error:
        return False, f"Error constructing Blueprint instance: {str(error)}"

    session.add(blueprint)
    try:
        session.commit()
        return (
            True,
            f"Blueprint '{blueprint_data['blueprint_name']}' has been saved successfully.",
        )
    except Exception as error:
        session.rollback()
        return False, str(error)


def load_blueprint_by_name(blueprint_name: str):
    """Loads a blueprint from the database by its name."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        db_query = (
            session.query(Blueprint)
            .options(joinedload(Blueprint.blueprint_objectives))
            .filter_by(blueprint_name=blueprint_name)
            .one()
        )

        # Ensure blueprint retrieved is an instance of the Blueprint dataclass
        if isinstance(db_query, Blueprint):
            return True, object_as_dict(db_query)

        raise ValueError("Retrieved object is not an instance of Blueprint")

    except Exception as error:
        return False, str(error)

    finally:
        session.close()


def load_blueprint_by_id(blueprint_id: str):
    """Loads a blueprint from the database by its name."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        db_query = (
            session.query(Blueprint)
            .options(joinedload(Blueprint.blueprint_objectives))
            .filter_by(blueprint_id=blueprint_id)
            .one()
        )

        # Ensure blueprint retrieved is an instance of the Blueprint dataclass
        if isinstance(db_query, Blueprint):
            return True, object_as_dict(db_query)

        raise ValueError("Retrieved object is not an instance of Blueprint")

    except Exception as error:
        return False, str(error)

    finally:
        session.close()


def create_blueprint(blueprint_data):
    """Creates a new blueprint in the database."""

    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    blueprint_id = blueprint_data.get("blueprint_id")

    # Check for duplicate blueprint_name or blueprint_id
    existing_blueprint_name = (
        session.query(Blueprint)
        .filter_by(blueprint_name=blueprint_data["blueprint_name"])
        .first()
    )

    if blueprint_id:
        existing_blueprint_id = (
            session.query(Blueprint).filter_by(blueprint_id=blueprint_id).first()
        )
        if existing_blueprint_id:
            return False, f"Blueprint with ID '{blueprint_id}' already exists."
    if existing_blueprint_name:
        return (
            False,
            f"Blueprint with name '{blueprint_data['blueprint_name']}' already exists.",
        )

    try:
        blueprint = Blueprint(
            blueprint_id=blueprint_id,
            blueprint_name=blueprint_data["blueprint_name"],
            blueprint_description=blueprint_data["blueprint_description"],
            sub_topic_name=blueprint_data["sub_topic_name"],
            pub_topic_name=blueprint_data["pub_topic_name"],
            initial_context=json.dumps(blueprint_data["initial_context"]),
        )
    except Exception as error:
        return False, f"Error constructing Blueprint instance: {str(error)}"

    session.add(blueprint)
    try:
        session.commit()
        return (
            True,
            f"Blueprint '{blueprint_data['blueprint_name']}' has been created successfully.",
        )
    except Exception as error:
        session.rollback()
        return False, str(error)
    finally:
        session.close()
