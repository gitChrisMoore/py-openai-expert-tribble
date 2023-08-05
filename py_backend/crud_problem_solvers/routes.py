import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response

import sqlite3
from py_backend.crud_problem_solvers import bp
from py_backend.storage.db import (
    get_problem_solver_configs,
    load_database,
    save_problem_solver_config,
)

# ROUTES_ID = "crud_problem_solvers"
load_dotenv()


def to_front_end(dicts):
    res = []
    for dict in dicts:
        res.append(
            {
                "id": dict["id"],
                "name": dict["name"],
                "description": dict["description"],
                "sub_topic_name": dict["sub_topic_name"],
                "pub_topic_name": dict["pub_topic_name"],
                "initial_context": json.loads(dict["initial_context"]),
                "functions": json.loads(dict["functions"]),
            }
        )
    return res


@bp.route("/", methods=["GET"])
def get_crud_problem_solvers_route():
    conn = load_database(os.environ.get("DB_FILEPATH"))
    configs = get_problem_solver_configs(conn)
    data = to_front_end(configs)
    return Response(json.dumps(data), mimetype="application/json")


@bp.route("/", methods=["POST"])
def post_crud_problem_solvers_route():
    conn = load_database(os.environ.get("DB_FILEPATH"))
    data = request.get_json()
    print(data)
    save_problem_solver_config(conn, data)
    return Response(json.dumps(data), mimetype="application/json")