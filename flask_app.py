from app.models import db
from app import create_app

app = create_app('DevelopmentConfig')

with app.app_context():
    # bd.drop_all()
    db.create_all()

app.run()    
