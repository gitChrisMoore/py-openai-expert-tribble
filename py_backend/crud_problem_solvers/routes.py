import json
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
import sqlite3
from py_backend.crud_problem_solvers import bp
from py_backend.storage.db import get_problem_solver_configs, load_database

ROUTES_ID = "crud_problem_solvers"
load_dotenv()


@bp.route("/", methods=["GET"])
def get_crud_problem_solvers_route():
    conn = load_database(os.environ.get("DB_FILEPATH"))
    data = get_problem_solver_configs(conn)
    return Response(json.dumps(data), mimetype="application/json")
