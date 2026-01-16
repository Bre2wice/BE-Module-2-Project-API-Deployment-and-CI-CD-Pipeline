from app.models import db
from app import create_app
from app.config import ProductionConfig

app = create_app(ProductionConfig)

with app.app_context():
    # bd.drop_all()
    db.create_all()
    
