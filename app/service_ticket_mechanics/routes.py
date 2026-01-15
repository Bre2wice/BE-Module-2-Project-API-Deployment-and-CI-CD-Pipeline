from flask import request, jsonify
from . import service_ticket_mechanics_bp
from app.models import ServiceTicketMechanic, ServiceTicket, Mechanic
from .schemas import st_mech_schema, st_mechs_schema
from app.extensions import db, limiter
from app.utils.util import mechanic_token_required


# -----------------------------
# GET all links
# -----------------------------
@service_ticket_mechanics_bp.get("/")
def get_all_links():
    links = ServiceTicketMechanic.query.all()
    # <-- change here
    return jsonify(st_mechs_schema.dump(links))


# -----------------------------
# GET link by ID
# -----------------------------
@service_ticket_mechanics_bp.get("/<int:id>")
def get_link(id):
    link = ServiceTicketMechanic.query.get_or_404(id)
    # <-- change here
    return jsonify(st_mech_schema.dump(link))


# -----------------------------
# POST: assign mechanic to ticket
# -----------------------------
@service_ticket_mechanics_bp.post("/")
@limiter.limit("5 per minute")
@mechanic_token_required
def create_link(current_mechanic_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    ticket_id = data.get("service_ticket_id")
    mechanic_id = data.get("mechanic_id")

    if not ticket_id or not mechanic_id:
        return jsonify({"message": "service_ticket_id and mechanic_id required"}), 400

    # 🔐 AUTHORIZATION CHECK (THIS IS WHAT YOU WERE MISSING)
    if mechanic_id != current_mechanic_id:
        return jsonify({"message": "Unauthorized"}), 403

    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    new_link = ServiceTicketMechanic(
        ticket_id=ticket_id,
        mechanic_id=mechanic_id,
        hours_worked=data.get("hours_worked"),
        role=data.get("role")
    )

    db.session.add(new_link)
    db.session.commit()

    return jsonify(st_mech_schema.dump(new_link)), 201


