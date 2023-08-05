from flask import Blueprint

bp = Blueprint(
    "funcs",
    __name__,
)

from py_backend.funcs import routes
