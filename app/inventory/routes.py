from flask import request, jsonify
from . import inventory_bp
from app.models import Inventory
from .schemas import InventorySchema
from app.extensions import db
from app.utils.util import mechanic_token_required  # optional auth

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

# -----------------------------
# GET all inventory
# -----------------------------
@inventory_bp.get("/")
def get_inventory():
    items = Inventory.query.all()
    return jsonify(inventories_schema.dump(items))

# -----------------------------
# GET single inventory item
# -----------------------------
@inventory_bp.get("/<int:id>")
def get_item(id):
    item = Inventory.query.get_or_404(id)
    return jsonify(inventory_schema.dump(item))

# -----------------------------
# CREATE inventory item
# -----------------------------
@inventory_bp.post("/")
@mechanic_token_required
def create_item(current_mechanic_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    item = Inventory(
        name=data["name"],
        price=data["price"]
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "added_by_mechanic_id": current_mechanic_id
    }), 201


# -----------------------------
# UPDATE inventory item
# -----------------------------
@inventory_bp.put("/<int:id>")
@mechanic_token_required
def update_item(current_mechanic_id, id):
    item = Inventory.query.get_or_404(id)
    data = request.get_json()

    for field in ["name", "price"]:
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    return jsonify({
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "updated_by_mechanic_id": current_mechanic_id
    })


# -----------------------------
# DELETE inventory item
# -----------------------------
@inventory_bp.delete("/<int:id>")
@mechanic_token_required
def delete_item(current_mechanic_id, id):
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({
        "message": "Inventory item deleted",
        "deleted_by_mechanic_id": current_mechanic_id
    })
