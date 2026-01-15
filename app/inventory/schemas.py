from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Inventory  # your Inventory model

class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True  # include foreign keys if there are any
