import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from py_backend.funcs import bp
from py_backend.storage.db import (
    load_database,
)
from py_backend.storage.tbl_func import get_func_configs, save_func_config


load_dotenv()


def to_front_end(dicts):
    res = []
    for dict in dicts:
        res.append(
            {
                "id": dict["id"],
                "name": dict["name"],
                "description": dict["description"],
                "parameters": json.loads(dict["parameters"]),
            }
        )
    return res


@bp.route("/", methods=["GET"])
def get_funcs():
    conn = load_database(os.environ.get("DB_FILEPATH"))
    configs = get_func_configs(conn)
    data = to_front_end(configs)
    return Response(json.dumps(data), mimetype="application/json")


@bp.route("/", methods=["POST"])
def post_funcs():
    conn = load_database(os.environ.get("DB_FILEPATH"))
    data = request.get_json()
    print(data)
    save_func_config(conn, data)
    return Response(json.dumps(data), mimetype="application/json")
