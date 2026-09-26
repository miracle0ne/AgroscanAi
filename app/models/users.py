from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
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

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=True
    )

    phone = db.Column(
        db.String(30),
        unique=True
    )

    location = db.Column(
        db.String(150)
    )

    password_hash = db.Column(
        db.String(255),
        nullable=True
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )
