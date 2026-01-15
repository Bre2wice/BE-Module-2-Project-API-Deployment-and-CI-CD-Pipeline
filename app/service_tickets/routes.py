# app/service_tickets/routes.py
from flask import request, jsonify
from app.extensions import db
from app.models import ServiceTicket, Mechanic, Inventory, Vehicle
from . import service_tickets_bp
from .schemas import service_ticket_schema
from app.utils.util import token_required, mechanic_token_required

# -------------------------------------------------
# CREATE SERVICE TICKET (CUSTOMER ONLY)
# -------------------------------------------------
@service_tickets_bp.route("/", methods=["POST"])
@token_required
def create_ticket(current_customer_id):
    print(current_customer_id)  # or use it in auth checks
    data = request.json

    vehicle = Vehicle.query.get(data["vehicle_id"])
    if not vehicle:
        return jsonify({"message": "Vehicle not found"}), 404

    new_ticket = ServiceTicket(
        vehicle_id=vehicle.id,
        description=data["description"],
        odometer_reading=data.get("odometer_reading"),
        description_of_issue=data.get("description_of_issue"),
        work_performed=data.get("work_performed"),
        estimated_cost=data.get("estimated_cost"),
        final_cost=data.get("final_cost"),
        status=data.get("status", "Pending")
    )

    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201


# -------------------------------------------------
# GET ALL TICKETS FOR CUSTOMER
# -------------------------------------------------
@service_tickets_bp.route("/", methods=["GET"])
@token_required
def get_tickets(current_customer_id):
    # Only tickets for vehicles belonging to this customer
    tickets = (
        ServiceTicket.query
        .join(Vehicle)
        .filter(Vehicle.customer_id == current_customer_id)
        .all()
    )

    result = []
    for t in tickets:
        result.append({
            "id": t.id,
            "vehicle_id": t.vehicle_id,
            "description": t.description,
            "odometer_reading": t.odometer_reading,
            "description_of_issue": t.description_of_issue,
            "work_performed": t.work_performed,
            "estimated_cost": t.estimated_cost,
            "final_cost": t.final_cost,
            "status": t.status,
            "mechanics": [{"id": m.id, "name": m.name} for m in t.mechanics],
            "inventory": [{"id": p.id, "name": p.name, "price": p.price} for p in t.inventory]
        })

    return jsonify(result), 200


# -------------------------------------------------
# EDIT TICKET: ADD/REMOVE MECHANICS & PARTS (MECHANIC OR ADMIN)
# -------------------------------------------------
@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@token_required
def edit_ticket(current_customer_id, ticket_id):
    print(current_customer_id)  # or use it in auth checks
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    # Ensure ticket belongs to current customer
    vehicle = Vehicle.query.get(ticket.vehicle_id)
    if vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()

    # --- Mechanics ---
    for mech_id in data.get("add_mechanics", []):
        mechanic = Mechanic.query.get(mech_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mech_id in data.get("remove_mechanics", []):
        mechanic = Mechanic.query.get(mech_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    # --- Inventory / Parts ---
    for part_id in data.get("add_parts", []):
        part = Inventory.query.get(part_id)
        if part and part not in ticket.inventory:
            ticket.inventory.append(part)

    for part_id in data.get("remove_parts", []):
        part = Inventory.query.get(part_id)
        if part and part in ticket.inventory:
            ticket.inventory.remove(part)

    db.session.commit()

    return jsonify({
        "ticket_id": ticket.id,
        "mechanics": [{"id": m.id, "name": m.name} for m in ticket.mechanics],
        "inventory": [{"id": p.id, "name": p.name, "price": p.price} for p in ticket.inventory]
    }), 200


# -------------------------------------------------
# ASSIGN SINGLE MECHANIC (OPTIONAL / MECHANIC ONLY)
# -------------------------------------------------
@service_tickets_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
@token_required
def assign_mechanic(current_customer_id, ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    # Ensure ticket belongs to current customer
    vehicle = Vehicle.query.get(ticket.vehicle_id)
    if vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Unauthorized"}), 403

    mechanic = Mechanic.query.get_or_404(mechanic_id)
    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()

    return jsonify({"message": "Mechanic assigned to ticket"}), 200


# -------------------------------------------------
# REMOVE SINGLE MECHANIC (OPTIONAL / MECHANIC ONLY)
# -------------------------------------------------
@service_tickets_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
@token_required
def remove_mechanic(current_customer_id, ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    # Ensure ticket belongs to current customer
    vehicle = Vehicle.query.get(ticket.vehicle_id)
    if vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Unauthorized"}), 403

    mechanic = Mechanic.query.get_or_404(mechanic_id)
    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()

    return jsonify({"message": "Mechanic removed from ticket"}), 200


# -------------------------------------------------
# ADD A PART TO TICKET
# -------------------------------------------------
@service_tickets_bp.route("/<int:ticket_id>/add-part", methods=["POST"])
@token_required
def add_part_to_ticket(current_customer_id, ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    # Ensure ticket belongs to current customer
    vehicle = Vehicle.query.get(ticket.vehicle_id)
    if vehicle.customer_id != current_customer_id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()
    part_id = data.get("part_id")
    quantity = data.get("quantity", 1)

    part = Inventory.query.get_or_404(part_id)

    # Add part to ticket
    ticket.inventory.append(part)
    db.session.commit()

    return jsonify({"message": f"Added {quantity} x {part.name} to ticket {ticket.id}"}), 201
