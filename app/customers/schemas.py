# app/customers/schemas.py

from app.extensions import ma, db
from app.models import Customer
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields


# -----------------------------
# Main Customer Schema
# -----------------------------
class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        sqla_session = db.session
        include_relationships = True


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


# -----------------------------
# Login Schema (email + password only)
# -----------------------------
class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


login_schema = LoginSchema()
