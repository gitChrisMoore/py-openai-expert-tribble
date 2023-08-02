from flask import Blueprint

bp = Blueprint(
    "market_obsticle",
    __name__,
)
from app.market_obsticle import routes
