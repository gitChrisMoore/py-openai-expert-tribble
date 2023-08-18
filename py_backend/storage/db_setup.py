import json
from sqlalchemy import create_engine
from py_backend.blueprints.routes import update_blueprint_logic
from py_backend.storage.db_blueprint import create_blueprint, save_blueprint

from py_backend.storage.db_models import Base
from py_backend.storage.db_objective import save_objective

DB_FILEPATH = "py_backend/storage/data_base.db"
INIT_FILEPATH = "py_backend/storage/"


def create_tables():
    """Creates all the tables in the database."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    Base.metadata.create_all(engine)


def drop_tables():
    """Drops all the tables in the database."""
    engine = create_engine(f"sqlite:///{DB_FILEPATH}")
    Base.metadata.drop_all(engine)


def load_blueprints():
    """Loads the blueprints data from the JSON file and saves it to the database."""

    with open(INIT_FILEPATH + "init_blueprints_data.json", "r") as file:
        blueprints_data = json.load(file)

    # Iterate through the blueprints and use the save_blueprint function
    for blueprint_data in blueprints_data:
        success, message = create_blueprint(blueprint_data)
        if not success:
            print(
                f"Failed to save blueprint '{blueprint_data['blueprint_name']}': {message}"
            )
            continue

    print("Blueprints data has been loaded successfully.")


def load_objectives():
    """Loads the objectives data from the JSON file and saves it to the database."""

    with open(INIT_FILEPATH + "init_objectives_data.json", "r") as file:
        objectives_data = json.load(file)

    # Iterate through the objectives and use the save_objective function
    for objective_data in objectives_data:
        success, message = save_objective(objective_data)
        if not success:
            print(
                f"Failed to save objective '{objective_data['objective_name']}': {message}"
            )
            continue

    print("Objectives data has been loaded successfully.")


def add_test_data_relationships():
    # Simulating the data you want to send
    data = {
        "blueprint_id": "e7602ac8-80f7-4584-aec4-053ce3590291",
        "objectives": [
            {"objective_id": "31db3025-00c3-4258-a717-718e9a11388b"},
            {"objective_id": "94264995-61ee-4f67-ad6d-be8a4be667c3"},
        ],
    }
    # Using the test client to send a PUT request
    update_blueprint_logic(data, "e7602ac8-80f7-4584-aec4-053ce3590291")


def initialize_database():
    """Initializes the database by creating the tables and loading the data."""
    drop_tables()
    create_tables()
    #
    load_objectives()
    load_blueprints()
    add_test_data_relationships()
