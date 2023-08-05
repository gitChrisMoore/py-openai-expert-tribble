import os
import sqlite3
import json

from py_backend.storage.db import create_database

DB_FILEPATH = "py_backend/storage/data_base.db"


def create_func_config_table(conn):
    """Creates a table to store func configurations.

    Args:
      conn: A connection object to the database.

    Returns:
      A connection object to the database.
    """

    sql = """
        CREATE TABLE IF NOT EXISTS func_config (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            parameters TEXT NOT NULL
        );
    """
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return conn


def get_func_config(conn):
    """Returns all func configurations.

    Args:
      conn: A connection object to the database.

    Returns:
      A list of tuples containing the configurations.
    """

    sql = """
        SELECT * FROM func_config;
    """
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return rows


def save_func_config(conn, dict_to_save):
    """Saves a func configuration.

    Args:
        conn: A connection object to the database.
        dict_to_save: A dictionary containing the configuration.

      Returns:
        A connection object to the database.
    """

    cursor = conn.cursor()

    # Check for duplicate id.
    cursor.execute("SELECT id FROM func_config WHERE id = ?", (dict_to_save["id"],))
    rows = cursor.fetchall()
    if rows:
        raise ValueError(
            "Func config with id {} already exists.".format(dict_to_save["id"])
        )

    # Check for duplicate name.
    cursor.execute("SELECT id FROM func_config WHERE name = ?", (dict_to_save["name"],))
    rows = cursor.fetchall()
    if rows:
        raise ValueError(
            "Func config with name {} already exists.".format(dict_to_save["name"])
        )

    conn.execute(
        "INSERT INTO func_config (id, name, description, parameters) VALUES (?, ?, ?, ?)",
        (
            dict_to_save["id"],
            dict_to_save["name"],
            dict_to_save["description"],
            json.dumps(dict_to_save["parameters"]),
        ),
    )
    conn.commit()
    return conn


def remove_table(conn, table_name):
    """Removes a table from the database.

    Args:
      conn: A connection object to the database.
      table_name: The name of the table to remove.
    """

    conn.execute("DROP TABLE IF EXISTS {}".format(table_name))
    conn.commit()


def get_func_configs(conn):
    """Gets all func configs from the database and returns them as a list of dicts."""

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM func_config")
    func_configs = []
    for row in cursor:
        func_configs.append(
            {"id": row[0], "name": row[1], "description": row[2], "parameters": row[3]}
        )
    return func_configs


def get_func_config_by_id(conn, id):
    """Gets a single func config by id.

    Args:
        conn: A connection object to the database.
        id: The id of the func config to get.

      Returns:
        A dictionary containing the func config, or None if the func config does not exist.
    """

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM func_config WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row is None:
        return None
    else:
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "parameters": row[3],
        }


def init_func_config_table():
    conn = create_database(DB_FILEPATH)
    remove_table(conn, "func_config")
    create_func_config_table(conn)

    json_file_path = "py_backend/storage/init_func_config_data.json"
    with open(json_file_path, "r") as file:
        func_configs = json.load(file)

    for func_config in func_configs:
        save_func_config(conn, func_config)

    list_of_problem_solvers = get_func_configs(conn)

    return list_of_problem_solvers
