# app/models.py

from app.extensions import db

# ------------------------------------------------
# Customer Model
# ------------------------------------------------
class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.String(255))

    vehicles = db.relationship(
        "Vehicle",
        backref="customer",
        cascade="all, delete-orphan"
    )


# ------------------------------------------------
# Vehicle Model
# ------------------------------------------------
class Vehicle(db.Model):
    __tablename__ = "vehicle"

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(120), nullable=False)
    model = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )

    vin = db.Column(
        db.String(17),
        unique=True,
        nullable=False
    )

    service_tickets = db.relationship(
        "ServiceTicket",
        backref="vehicle",
        cascade="all, delete-orphan"
    )


# ------------------------------------------------
# Join Table: ServiceTicketMechanic (MANY-TO-MANY)
# ------------------------------------------------
class ServiceTicketMechanic(db.Model):
    __tablename__ = "service_ticket_mechanics"

    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        nullable=False
    )

    mechanic_id = db.Column(
        db.Integer,
        db.ForeignKey("mechanic.id"),
        nullable=False
    )

    hours_worked = db.Column(db.Float, nullable=True)

    role = db.Column(db.String(50), nullable=True)



# ------------------------------------------------
# Mechanic Model
# ------------------------------------------------
class Mechanic(db.Model):
    __tablename__ = "mechanic"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    salary = db.Column(db.Float)
    password = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        secondary="service_ticket_mechanics",
        back_populates="mechanics"
    )


# ------------------------------------------------
# Join Table: ServiceTicketInventory (MANY-TO-MANY)
# ------------------------------------------------
service_ticket_inventory = db.Table(
    "service_ticket_inventory",
    db.Column(
        "ticket_id",
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        primary_key=True
    ),
    db.Column(
        "inventory_id",
        db.Integer,
        db.ForeignKey("inventory.id"),
        primary_key=True
    )
)


# ------------------------------------------------
# Inventory Model
# ------------------------------------------------
class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket",
        secondary=service_ticket_inventory,
        back_populates="inventory"
    )


# ------------------------------------------------
# Service Ticket Model
# ------------------------------------------------
class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default="open")

    odometer_reading = db.Column(db.Integer)
    description_of_issue = db.Column(db.String(255), nullable=False)
    work_performed = db.Column(db.String(255))
    estimated_cost = db.Column(db.Float)
    final_cost = db.Column(db.Float)
    status = db.Column(db.String(50), default="Pending")

    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("vehicle.id"),
        nullable=False
    )

    mechanics = db.relationship(
        "Mechanic",
        secondary="service_ticket_mechanics",
        back_populates="service_tickets"
    )

    inventory = db.relationship(
        "Inventory",
        secondary=service_ticket_inventory,
        back_populates="service_tickets"
    )

