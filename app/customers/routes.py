from flask import request, jsonify
from . import customers_bp
from app.models import Customer
from .schemas import customer_schema, customers_schema, login_schema
from app.extensions import db, limiter, cache
from app.utils.util import encode_token, token_required
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError


# -----------------------------
# GET ALL CUSTOMERS (CACHED)
# -----------------------------
@customers_bp.get("/")
@limiter.limit("5 per minute")
def get_customers():
    cached = cache.get("all_customers")
    if cached:
        return jsonify(cached)

    customers = Customer.query.all()
    data = customers_schema.dump(customers)

    cache.set("all_customers", data, timeout=60)
    return jsonify(data)


# -----------------------------
# CREATE CUSTOMER
# -----------------------------
@customers_bp.post("/")
@limiter.limit("5 per minute")
def create_customer():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    if "password" in data:
        data["password"] = generate_password_hash(
            data["password"],
            method="pbkdf2:sha256"
        )

    try:
        new_customer = customer_schema.load(data, session=db.session)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(new_customer)
    db.session.commit()

    cache.delete("all_customers")
    return jsonify(customer_schema.dump(new_customer)), 201


# -----------------------------
# UPDATE CUSTOMER (AUTH REQUIRED)
# -----------------------------
@customers_bp.put("/<int:id>")
@limiter.limit("5 per minute")
@token_required
def update_customer(customer_id, id):
    if customer_id != id:
        return jsonify({"error": "Unauthorized"}), 403

    customer = Customer.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No input data provided"}), 400

    for field in ["name", "phone", "email", "address"]:
        if field in data:
            setattr(customer, field, data[field])

    db.session.commit()
    cache.delete("all_customers")

    return jsonify(customer_schema.dump(customer))


# -----------------------------
# DELETE CUSTOMER (AUTH REQUIRED)
# -----------------------------
@customers_bp.delete("/<int:id>")
@limiter.limit("5 per minute")
@token_required
def delete_customer(customer_id, id):
    if customer_id != id:
        return jsonify({"error": "Unauthorized"}), 403

    customer = Customer.query.get_or_404(id)

    if customer.vehicles:
        return jsonify({
            "error": "Cannot delete customer with vehicles"
        }), 400

    db.session.delete(customer)
    db.session.commit()
    cache.delete("all_customers")

    return jsonify({"message": "Customer deleted"})


# -----------------------------
# LOGIN CUSTOMER
# -----------------------------
@customers_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    customer = Customer.query.filter_by(email=data["email"]).first()

    if not customer or not check_password_hash(
        customer.password,
        data["password"]
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    token = encode_token(customer.id)
    return jsonify({
        "token": token,
        "customer_id": customer.id
    })


# -----------------------------
# GET CURRENT CUSTOMER'S TICKETS
# -----------------------------
@customers_bp.get("/my-tickets")
@token_required
def my_tickets(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    tickets = [
        ticket
        for vehicle in customer.vehicles
        for ticket in vehicle.service_tickets
    ]

    return jsonify([
        {
            "id": t.id,
            "description": t.description,
            "status": t.status
        }
        for t in tickets
    ])
