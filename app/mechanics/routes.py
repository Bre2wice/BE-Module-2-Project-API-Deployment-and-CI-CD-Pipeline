# app/mechanics/routes.py
from flask import request, jsonify
from app.extensions import db
from app.models import Mechanic
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt, JWTError, ExpiredSignatureError
from functools import wraps
from app.utils.util import mechanic_token_required
import datetime

# Secret key for JWT
SECRET_KEY = "super-secret-key"  # replace with env var in production

# -----------------------------
# Mechanic Token Required Decorator
# -----------------------------
def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_mechanic_id = payload.get("mechanic_id")
            if not current_mechanic_id:
                return jsonify({"message": "Invalid token"}), 403
        except ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 403
        except JWTError:
            return jsonify({"message": "Token is invalid"}), 403
        return f(current_mechanic_id, *args, **kwargs)
    return decorated

# -----------------------------
# CREATE MECHANIC
# -----------------------------
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    data = request.json
    if not data.get("password"):
        return jsonify({"message": "Password is required"}), 400

    mechanic = Mechanic(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        address=data.get("address"),
        salary=data.get("salary"),
        password=generate_password_hash(
    data["password"],
    method="pbkdf2:sha256"
)

    )
    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201

# -----------------------------
# LOGIN MECHANIC
# -----------------------------
@mechanics_bp.route("/login", methods=["POST"])
def login_mechanic():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    mechanic = Mechanic.query.filter_by(email=email).first()
    if not mechanic:
        return jsonify({"message": "Mechanic not found"}), 404

    if not check_password_hash(mechanic.password, password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    # -----------------------------
    # Generate JWT token
    # -----------------------------
    token = jwt.encode(
        {
            "mechanic_id": mechanic.id,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)  # expires in 1 hour
        },
        SECRET_KEY,
        algorithm="HS256"
    )


    return jsonify({"token": token}), 200

# -----------------------------
# GET ALL MECHANICS
# -----------------------------
@mechanics_bp.route("/", methods=["GET"])
def get_mechanics():
    all_mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(all_mechanics)

# -----------------------------
# UPDATE MECHANIC (protected)
# -----------------------------
@mechanics_bp.route("/<int:id>", methods=["PUT"])
@mechanic_token_required
def update_mechanic(current_mechanic_id, id):
    mechanic = Mechanic.query.get_or_404(id)
    data = request.json

    mechanic.name = data.get("name", mechanic.name)
    mechanic.email = data.get("email", mechanic.email)
    mechanic.phone = data.get("phone", mechanic.phone)
    mechanic.address = data.get("address", mechanic.address)
    mechanic.salary = data.get("salary", mechanic.salary)
    password=data.get("password")

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# -----------------------------
# DELETE MECHANIC (protected)
# -----------------------------
@mechanics_bp.route("/<int:id>", methods=["DELETE"])
@mechanic_token_required
def delete_mechanic(current_mechanic_id, id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic deleted"}), 200

# -----------------------------
# POPULAR MECHANICS (Advanced Query)
# -----------------------------
@mechanics_bp.route("/popular", methods=["GET"])
def popular_mechanics():
    mechanics = Mechanic.query.all()
    mechanics.sort(key=lambda m: len(m.service_tickets), reverse=True)

    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))
    mechanics_paginated = mechanics[offset:offset + limit]

    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone,
            "tickets_worked": len(m.service_tickets)
        }
        for m in mechanics_paginated
    ])
