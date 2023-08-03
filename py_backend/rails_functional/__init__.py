from flask import Blueprint

bp = Blueprint(
    "rails_functional",
    __name__,
)

from py_backend.rails_functional import routes
