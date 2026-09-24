from app.extensions import db
from datetime import datetime


class PilotRecord(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    crop = db.Column(
        db.String(200),
        nullable=False
    )

    image_reference = db.Column(
        db.String(255)
    )

    ai_diagnosis = db.Column(
        db.Text
    )

    symptoms = db.Column(
        db.Text
    )

    recommendations = db.Column(
        db.Text
    )

    actual_diagnosis = db.Column(
        db.Text
    )

    correct = db.Column(
        db.Boolean
    )

    recommendation_followed = db.Column(
        db.Boolean
    )

    outcome = db.Column(
        db.Text
    )

    feedback = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
