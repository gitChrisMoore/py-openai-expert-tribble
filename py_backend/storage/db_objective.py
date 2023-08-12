import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from py_backend.storage.db_models import Objective


DB_FILEPATH = "py_backend/storage/data_base.db"


def save_objective(objective_data):
    """Saves an individual objective to the database."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    session = Session(engine)

    try:
        # Construct the Objective instance
        objective = Objective(
            objective_id=objective_data.get("objective_id") or objective_data.get("id"),
            objective_name=objective_data.get("objective_name")
            or objective_data.get("name"),
            objective_description=objective_data.get("objective_description")
            or objective_data.get("description"),
            parameters=json.dumps(objective_data["parameters"]),
        )
    except Exception as error:
        return False, f"Error constructing Objective instance: {str(error)}"

    # Add to the session and commit
    session.add(objective)
    try:
        session.commit()
        return (
            True,
            f"Blueprint '{objective_data['objective_name']}' has been saved successfully.",
        )
    except Exception as error:
        session.rollback()
        return False, str(error)
