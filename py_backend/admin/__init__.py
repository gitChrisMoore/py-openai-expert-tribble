from flask import Blueprint

bp = Blueprint(
    "admin",
    __name__,
)

from py_backend.admin import routes
