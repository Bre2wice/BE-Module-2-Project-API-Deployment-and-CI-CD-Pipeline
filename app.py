from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Secretgarden@localhost/mechanic_shop'


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class= Base)
ma =Marshmallow()

db.init_app(app)
ma.init_app(app)

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    vehicles = db.relationship("Vehicle", back_populates="customer")

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))
    
    vin: Mapped[str] = mapped_column(db.String(17), unique=True, nullable=False)
    make: Mapped[str] = mapped_column(db.String(50), nullable=False)
    model: Mapped[str] = mapped_column(db.String(50), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    
    customer = db.relationship("Customer", back_populates="vehicles")

class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(db.ForeignKey("vehicles.id"))
    
    service_date: Mapped[str] = mapped_column(db.Date)
    odometer_reading: Mapped[int] = mapped_column()
    description_of_issue: Mapped[str] = mapped_column(db.Text)
    work_performed: Mapped[str] = mapped_column(db.Text)
    estimated_cost: Mapped[float] = mapped_column(db.Float)
    final_cost: Mapped[float] = mapped_column(db.Float)
    status: Mapped[str] = mapped_column(db.String(20))

    # Relationship
    vehicle = db.relationship("Vehicle", backref="service_tickets")

class ServiceTicketMechanic(db.Model):
    __tablename__ = "service_ticket_mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"))
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey("mechanics.id"))
    hours_worked: Mapped[float] = mapped_column(db.Float)
    role: Mapped[str] = mapped_column(db.String(50))

    # Relationships
    service_ticket = db.relationship("ServiceTicket", backref="mechanics_assigned")
    mechanic = db.relationship("Mechanic", backref="tickets_worked")


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20))
    address: Mapped[str] = mapped_column(db.String(200))
    salary: Mapped[float] = mapped_column(db.Float)

# ----------------- Customer Schema -----------------
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    vehicles = ma.Nested('VehicleSchema', many=True)  # Include related vehicles
    class Meta:
        model = Customer
        load_instance = True  # deserialize to model instances
        include_fk = True

# ----------------- Vehicle Schema -----------------
class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        load_instance = True
        include_fk = True

# ----------------- Service Ticket Schema -----------------
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

# ----------------- Mechanic Schema -----------------
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True

# ----------------- ServiceTicketMechanic Schema -----------------
class ServiceTicketMechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicketMechanic
        load_instance = True
        include_fk = True

  
# ----------------- CRUD Routes -----------------
# -------- Customer Routes --------
@app.route("/customers", methods=["POST"])
def add_customer():
    data = request.json
    new_customer = Customer(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone", ""),    # default empty string if not provided
        address=data.get("address", "") # default empty string if not provided
    )
    db.session.add(new_customer)
    db.session.commit()
    return CustomerSchema().jsonify(new_customer)


@app.route("/customers", methods=["GET"])
def get_customers():
    all_customers = Customer.query.all()
    return CustomerSchema(many=True).jsonify(all_customers)

@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return CustomerSchema().jsonify(customer)

@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.json
    customer.name = data.get("name", customer.name)
    customer.email = data.get("email", customer.email)
    db.session.commit()
    return CustomerSchema().jsonify(customer)

@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"})

# -------- Vehicle Routes --------
@app.route("/vehicles", methods=["POST"])
def add_vehicle():
    data = request.json
    vehicle = Vehicle(
        vin=data["vin"],
        make=data["make"],
        model=data["model"],
        year=data["year"],
        customer_id=data["customer_id"]
    )
    db.session.add(vehicle)
    db.session.commit()
    return VehicleSchema().jsonify(vehicle)

@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    all_vehicles = Vehicle.query.all()
    return VehicleSchema(many=True).jsonify(all_vehicles)

@app.route("/vehicles/<int:id>", methods=["GET"])
def get_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    return VehicleSchema().jsonify(vehicle)

@app.route("/vehicles/<int:id>", methods=["PUT"])
def update_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    data = request.json
    vehicle.vin = data.get("vin", vehicle.vin)
    vehicle.make = data.get("make", vehicle.make)
    vehicle.model = data.get("model", vehicle.model)
    vehicle.year = data.get("year", vehicle.year)
    vehicle.customer_id = data.get("customer_id", vehicle.customer_id)
    db.session.commit()
    return VehicleSchema().jsonify(vehicle)

@app.route("/vehicles/<int:id>", methods=["DELETE"])
def delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Vehicle deleted"})

# -------- Service Ticket Routes --------
@app.route("/service_tickets", methods=["POST"])
def add_service_ticket():
    data = request.json
    ticket = ServiceTicket(
        vehicle_id=data["vehicle_id"],
        service_date=data.get("service_date", date.today()),
        odometer_reading=data.get("odometer_reading"),
        description_of_issue=data.get("description_of_issue"),
        work_performed=data.get("work_performed"),
        estimated_cost=data.get("estimated_cost"),
        final_cost=data.get("final_cost"),
        status=data.get("status", "Pending")
    )
    db.session.add(ticket)
    db.session.commit()
    return ServiceTicketSchema().jsonify(ticket)

@app.route("/service_tickets", methods=["GET"])
def get_service_tickets():
    all_tickets = ServiceTicket.query.all()
    return ServiceTicketSchema(many=True).jsonify(all_tickets)

@app.route("/service_tickets/<int:id>", methods=["GET"])
def get_service_ticket(id):
    ticket = ServiceTicket.query.get_or_404(id)
    return ServiceTicketSchema().jsonify(ticket)

@app.route("/service_tickets/<int:id>", methods=["PUT"])
def update_service_ticket(id):
    ticket = ServiceTicket.query.get_or_404(id)
    data = request.json
    ticket.vehicle_id = data.get("vehicle_id", ticket.vehicle_id)
    ticket.service_date = data.get("service_date", ticket.service_date)
    ticket.odometer_reading = data.get("odometer_reading", ticket.odometer_reading)
    ticket.description_of_issue = data.get("description_of_issue", ticket.description_of_issue)
    ticket.work_performed = data.get("work_performed", ticket.work_performed)
    ticket.estimated_cost = data.get("estimated_cost", ticket.estimated_cost)
    ticket.final_cost = data.get("final_cost", ticket.final_cost)
    ticket.status = data.get("status", ticket.status)
    db.session.commit()
    return ServiceTicketSchema().jsonify(ticket)

@app.route("/service_tickets/<int:id>", methods=["DELETE"])
def delete_service_ticket(id):
    ticket = ServiceTicket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": "Service Ticket deleted"})

# -------- Mechanic Routes --------
@app.route("/mechanics", methods=["POST"])
def add_mechanic():
    data = request.json
    mechanic = Mechanic(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        address=data.get("address"),
        salary=data.get("salary")
    )
    db.session.add(mechanic)
    db.session.commit()
    return MechanicSchema().jsonify(mechanic)

@app.route("/mechanics", methods=["GET"])
def get_mechanics():
    all_mechanics = Mechanic.query.all()
    return MechanicSchema(many=True).jsonify(all_mechanics)

@app.route("/mechanics/<int:id>", methods=["GET"])
def get_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    return MechanicSchema().jsonify(mechanic)

@app.route("/mechanics/<int:id>", methods=["PUT"])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    data = request.json
    mechanic.name = data.get("name", mechanic.name)
    mechanic.email = data.get("email", mechanic.email)
    mechanic.phone = data.get("phone", mechanic.phone)
    mechanic.address = data.get("address", mechanic.address)
    mechanic.salary = data.get("salary", mechanic.salary)
    db.session.commit()
    return MechanicSchema().jsonify(mechanic)

@app.route("/mechanics/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic deleted"})

# -------- ServiceTicketMechanic Routes --------
@app.route("/service_ticket_mechanics", methods=["POST"])
def add_service_ticket_mechanic():
    data = request.json
    stm = ServiceTicketMechanic(
        service_ticket_id=data["service_ticket_id"],
        mechanic_id=data["mechanic_id"],
        hours_worked=data.get("hours_worked", 0),
        role=data.get("role", "Technician")
    )
    db.session.add(stm)
    db.session.commit()
    return ServiceTicketMechanicSchema().jsonify(stm)

@app.route("/service_ticket_mechanics", methods=["GET"])
def get_service_ticket_mechanics():
    all_stm = ServiceTicketMechanic.query.all()
    return ServiceTicketMechanicSchema(many=True).jsonify(all_stm)

@app.route("/service_ticket_mechanics/<int:id>", methods=["GET"])
def get_service_ticket_mechanic(id):
    stm = ServiceTicketMechanic.query.get_or_404(id)
    return ServiceTicketMechanicSchema().jsonify(stm)

@app.route("/service_ticket_mechanics/<int:id>", methods=["PUT"])
def update_service_ticket_mechanic(id):
    stm = ServiceTicketMechanic.query.get_or_404(id)
    data = request.json
    stm.service_ticket_id = data.get("service_ticket_id", stm.service_ticket_id)
    stm.mechanic_id = data.get("mechanic_id", stm.mechanic_id)
    stm.hours_worked = data.get("hours_worked", stm.hours_worked)
    stm.role = data.get("role", stm.role)
    db.session.commit()
    return ServiceTicketMechanicSchema().jsonify(stm)

@app.route("/service_ticket_mechanics/<int:id>", methods=["DELETE"])
def delete_service_ticket_mechanic(id):
    stm = ServiceTicketMechanic.query.get_or_404(id)
    db.session.delete(stm)
    db.session.commit()
    return jsonify({"message": "ServiceTicketMechanic deleted"})


with app.app_context():
        db.create_all()
print("Tables created successfully!")
if __name__ == "__main__":
    app.run(debug=True)