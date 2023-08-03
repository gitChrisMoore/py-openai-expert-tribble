from flask import Blueprint

bp = Blueprint(
    "market_obsticle",
    __name__,
)

from py_backend.market_obsticle import routes
