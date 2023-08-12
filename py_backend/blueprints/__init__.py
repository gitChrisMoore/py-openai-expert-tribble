from flask import Blueprint

bp = Blueprint(
    "blueprints",
    __name__,
)

from py_backend.blueprints import routes
