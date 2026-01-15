# app/blueprints/vehicles/routes.py
from flask import request, jsonify
from app.extensions import db
from app.models import Vehicle
from . import vehicles_bp
from .schemas import vehicle_schema, vehicles_schema
from app.utils.util import token_required


# -----------------------------
# CREATE a vehicle
# -----------------------------
@vehicles_bp.route("/", methods=["POST"])
@token_required
def create_vehicle(current_customer_id):
    data = request.json


    vehicle = Vehicle(
        customer_id=current_customer_id,
        make=data["make"],
        model=data["model"],
        year=data["year"],
        vin=data["vin"]
    )
    db.session.add(vehicle)
    db.session.commit()
    return vehicle_schema.jsonify(vehicle), 201


# -----------------------------
# GET all vehicles for current customer
# -----------------------------
@vehicles_bp.route("/", methods=["GET"])
@token_required
def get_vehicles(current_customer_id):
    vehicles = Vehicle.query.filter_by(customer_id=current_customer_id).all()
    return vehicles_schema.jsonify(vehicles), 200


# -----------------------------
# GET vehicle by ID
# -----------------------------
@vehicles_bp.route("/<int:id>", methods=["GET"])
@token_required
def get_vehicle(id, current_customer_id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle or vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Vehicle not found or unauthorized"}), 404
    return vehicle_schema.jsonify(vehicle), 200


# -----------------------------
# UPDATE a vehicle
# -----------------------------
@vehicles_bp.route("/<int:id>", methods=["PUT"])
@token_required
def update_vehicle(id, current_customer_id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle or vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Vehicle not found or unauthorized"}), 404

    data = request.json
    vehicle.make = data.get("make", vehicle.make)
    vehicle.model = data.get("model", vehicle.model)
    vehicle.year = data.get("year", vehicle.year)
    vehicle.vin = data.get("vin", vehicle.vin)
    # Always use token's customer_id for security
    vehicle.customer_id = current_customer_id

    db.session.commit()
    return vehicle_schema.jsonify(vehicle), 200


# -----------------------------
# DELETE a vehicle
# -----------------------------
@vehicles_bp.route("/<int:id>", methods=["DELETE"])
@token_required
def delete_vehicle(id, current_customer_id):
    vehicle = db.session.get(Vehicle, id)
    if not vehicle or vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Vehicle not found or unauthorized"}), 404

    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted"}), 200
