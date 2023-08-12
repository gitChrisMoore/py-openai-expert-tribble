import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from py_backend.storage.db_models import Blueprint


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
