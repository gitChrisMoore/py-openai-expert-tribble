from flask import Blueprint

bp = Blueprint(
    "crud_problem_solvers",
    __name__,
)

from py_backend.crud_problem_solvers import routes
