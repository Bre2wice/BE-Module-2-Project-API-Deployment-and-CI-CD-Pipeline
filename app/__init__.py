from flask import Flask
from app.extensions import db, ma, limiter, cache
from flask_migrate import Migrate

# Import blueprints
from app.customers import customers_bp
from app.mechanics import mechanics_bp
from app.service_tickets import service_tickets_bp
from app.service_ticket_mechanics import service_ticket_mechanics_bp
from app.vehicles import vehicles_bp
from app.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs' #Sets the endpoint for our documentation
API_URL = '/static/swagger.yaml' #Grabs the host from our swagger file


swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "MechanicAPI"
    }
)

def create_app(testing=False):
    app = Flask(__name__, static_folder="static")

    # ----------------------------
    # Configuration
    # ----------------------------
    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["RATELIMIT_ENABLED"] = False
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "mysql+mysqlconnector://root:Secretgarden@localhost/mechanic_shop"
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "super-secret-key"

    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60

    # ----------------------------
    # Initialize extensions
    # ----------------------------
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    Migrate(app, db)

    # ----------------------------
    # Register Blueprints
    # ----------------------------
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service_tickets")
    app.register_blueprint(service_ticket_mechanics_bp, url_prefix="/service_ticket_mechanics")
    app.register_blueprint(vehicles_bp, url_prefix="/vehicles")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    return app











