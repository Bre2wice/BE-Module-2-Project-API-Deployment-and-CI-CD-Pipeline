from flask import Blueprint

service_ticket_mechanics_bp = Blueprint(
    "service_ticket_mechanics", __name__
)

# This import is necessary so Flask registers the routes
from . import routes 
