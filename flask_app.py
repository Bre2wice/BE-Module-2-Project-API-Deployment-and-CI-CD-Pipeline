from app import create_app
from app.models import db

# IMPORTANT: pass the config name as a STRING
app = create_app('ProductionConfig')

with app.app_context():
    db.create_all()
