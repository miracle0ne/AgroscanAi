from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        unique=True
    )

    location = db.Column(
        db.String(150)
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    role = db.relationship(
        "Role",
        backref="users"
    )

    pilot_records = db.relationship(
        "PilotRecord",
        backref="user",
        lazy=True
    )
