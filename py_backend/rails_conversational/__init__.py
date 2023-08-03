from flask import Blueprint

bp = Blueprint(
    "rails_conversational",
    __name__,
)

from py_backend.rails_conversational import routes
