from flask import Blueprint

bp = Blueprint(
    "objectives",
    __name__,
)

from py_backend.objectives import routes
