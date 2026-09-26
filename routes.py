from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    result = db.session.execute(db.text("SELECT 1"))
    print("DATABASE TEST =", result.scalar())