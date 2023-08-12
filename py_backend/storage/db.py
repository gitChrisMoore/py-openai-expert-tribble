import os
import sqlite3

DB_FILEPATH = "py_backend/storage/data_base.db"


def load_database(database_name):
    """Checks if a local database exists in the same folder and loads it.

    Args:
      database_name: The name of the database file.

    Returns:
      A connection object to the database.
    """

    database_path = os.path.join(os.getcwd(), database_name)
    if not os.path.isfile(database_path):
        raise FileNotFoundError(f"Database '{database_name}' not found.")

    conn = sqlite3.connect(database_path)
    return conn


def create_database(database_name):
    """Creates a database if it doesn't exist.

    Args:
      database_name: The name of the database file.

    Returns:
      A connection object to the database.
    """

    database_path = os.path.join(os.getcwd(), database_name)
    if os.path.isfile(database_path):
        return load_database(database_name)
    else:
        conn = sqlite3.connect(database_path)
        return conn


def create_problem_solver_config_table(conn):
    """Creates a table to store problem solver configurations.

    Args:
      conn: A connection object to the database.

    Returns:
      A connection object to the database.
    """

    sql = """
        CREATE TABLE IF NOT EXISTS problem_solver_config (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            sub_topic_name TEXT NOT NULL,
            pub_topic_name TEXT NOT NULL,
            initial_context TEXT NOT NULL,
            functions TEXT NOT NULL
        );
    """
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return conn


def get_problem_solver_config(conn):
    """Returns all problem solver configurations.

    Args:
      conn: A connection object to the database.

    Returns:
      A list of tuples containing the configurations.
    """

    sql = """
        SELECT * FROM problem_solver_config;
    """
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows


import json


def save_problem_solver_config(conn, dict_to_save):
    """Saves a problem solver configuration.

    Args:
        conn: A connection object to the database.
        dict_to_save: A dictionary containing the configuration.

      Returns:
        A connection object to the database.
    """

    cursor = conn.cursor()

    # Check for duplicate id.
    cursor.execute(
        "SELECT id FROM problem_solver_config WHERE id = ?", (dict_to_save["id"],)
    )
    rows = cursor.fetchall()
    if rows:
        raise ValueError(
            "Problem solver config with id {} already exists.".format(
                dict_to_save["id"]
            )
        )

    # Check for duplicate name.
    cursor.execute(
        "SELECT id FROM problem_solver_config WHERE name = ?", (dict_to_save["name"],)
    )
    rows = cursor.fetchall()
    if rows:
        raise ValueError(
            "Problem solver config with name {} already exists.".format(
                dict_to_save["name"]
            )
        )

    conn.execute(
        "INSERT INTO problem_solver_config (id, name, description, sub_topic_name, pub_topic_name, initial_context, functions) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            dict_to_save["id"],
            dict_to_save["name"],
            dict_to_save["description"],
            dict_to_save["sub_topic_name"],
            dict_to_save["pub_topic_name"],
            json.dumps(dict_to_save["initial_context"]),
            json.dumps(dict_to_save["functions"]),
        ),
    )
    conn.commit()
    return conn


def remove_table(table_name):
    """Removes a table from the database.

    Args:
      conn: A connection object to the database.
      table_name: The name of the table to remove.
    """
    conn = create_database(DB_FILEPATH)
    conn.execute("DROP TABLE IF EXISTS {}".format(table_name))
    conn.commit()


def get_problem_solver_configs(conn):
    """Gets all problem solver configs from the database and returns them as a list of dicts."""

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problem_solver_config")
    problem_solver_configs = []
    for row in cursor:
        problem_solver_configs.append(
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "sub_topic_name": row[3],
                "pub_topic_name": row[4],
                "initial_context": row[5],
                "functions": row[6],
            }
        )
    return problem_solver_configs


def get_problem_solver_and_objectives(conn, problem_solver_id):
    """
    Retrieves a problem solver configuration and its associated objectives.

    Args:
      conn: A connection object to the database.
      problem_solver_id: The ID of the problem solver configuration to retrieve.

    Returns:
      A dictionary representing the problem solver configuration, with the objective IDs included as a list.
    """

    cur = conn.cursor()

    # Query to retrieve the problem solver configuration
    cur.execute(
        """
        SELECT * FROM problem_solver_config
        WHERE id = ?;
    """,
        (problem_solver_id,),
    )
    problem_solver_row = cur.fetchone()
    if problem_solver_row is None:
        return None
    problem_solver = {
        "id": problem_solver_row[0],
        "name": problem_solver_row[1],
        "description": problem_solver_row[2],
        "sub_topic_name": problem_solver_row[3],
        "pub_topic_name": problem_solver_row[4],
        "initial_context": problem_solver_row[5],
        "functions": problem_solver_row[6],
        "objective_ids": [],
    }

    # Query to retrieve the associated objectives
    cur.execute(
        """
        SELECT id FROM func_config
        WHERE config_id = ?;
    """,
        (problem_solver_id,),
    )
    objectives_rows = cur.fetchall()
    problem_solver["objective_ids"] = [row[0] for row in objectives_rows]

    return problem_solver


def get_problem_solver_config_by_id(conn, id):
    """Gets a single problem solver config by id.

    Args:
        conn: A connection object to the database.
        id: The id of the problem solver config to get.

      Returns:
        A dictionary containing the problem solver config, or None if the problem solver config does not exist.
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problem_solver_config WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row is None:
        return None
    else:
        return {
            "id": row[0],
            "description": row[1],
            "name": row[2],
            "sub_topic_name": row[3],
            "pub_topic_name": row[4],
            "initial_context": json.loads(row[5]),
            "functions": json.loads(row[6]),
        }


def init_problem_solver_config_table():
    conn = create_database(DB_FILEPATH)
    remove_table("problem_solver_config")
    create_problem_solver_config_table(conn)

    json_file_path = "py_backend/storage/init_problem_solver_config_data.json"
    with open(json_file_path, "r") as file:
        problem_solver_configs = json.load(file)

    for problem_solver_config in problem_solver_configs:
        save_problem_solver_config(conn, problem_solver_config)

    list_of_problem_solvers = get_problem_solver_configs(conn)

    return list_of_problem_solvers
