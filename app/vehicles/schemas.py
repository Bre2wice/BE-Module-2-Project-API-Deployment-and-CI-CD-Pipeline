from app.extensions import ma
from app.models import Vehicle


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        load_instance = True
        include_fk = True


vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)
