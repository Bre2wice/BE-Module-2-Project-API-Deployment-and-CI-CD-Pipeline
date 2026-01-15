from app.extensions import ma
from app.models import ServiceTicketMechanic
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class STMechSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicketMechanic
        include_fk = True
        load_instance = True

st_mech_schema = STMechSchema()
st_mechs_schema = STMechSchema(many=True)
