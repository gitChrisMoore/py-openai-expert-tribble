from dotenv import load_dotenv
from flask import Response
from py_backend.admin import bp
from py_backend.storage.db import (
    init_problem_solver_config_table,
    remove_table,
)
from py_backend.storage.tbl_func import init_func_config_table


load_dotenv()


@bp.route("/reset_database", methods=["GET"])
def reset_database():
    remove_table("problem_solver_config")
    remove_table("func_config")
    funcs = init_func_config_table()
    if funcs is None:
        return Response("Error: Func Table Failture", status=500)
    blueprints = init_problem_solver_config_table()
    if blueprints is None:
        return Response("Error: Blueprint Table Failture", status=500)
    return Response("Success", status=200)
