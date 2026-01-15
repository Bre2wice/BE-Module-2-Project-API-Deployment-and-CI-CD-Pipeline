# app/customers/__init__.py

from flask import Blueprint

customers_bp = Blueprint("customers", __name__)

from . import routes
