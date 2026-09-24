from flask import Blueprint, request, jsonify
from app.extensions import db
from app.pilot.models import PilotRecord
from app.models.users import User


pilot = Blueprint("pilot", __name__, url_prefix="/pilot")


@pilot.route("/record", methods=["POST"])
def create_record():
    data = request.get_json(silent=True) or {}

    user_code = data.get("user_code")

    crop = data.get("crop")

    if not crop:
        return jsonify({
            "error": "crop is required"
        }), 400


    if not user_code:
        return jsonify({
            "error": "user_code is required"
        }), 400

    user = User.query.filter_by(
        user_code=user_code
    ).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    record = PilotRecord(
        user_id=user.id,
        crop=crop,
        image_reference=data.get("image_reference"),
        ai_diagnosis=data.get("ai_diagnosis"),
        symptoms=data.get("symptoms"),
        recommendations=data.get("recommendations"),
        actual_diagnosis=data.get("actual_diagnosis"),
        correct=data.get("correct"),
        recommendation_followed=data.get(
            "recommendation_followed"
        ),
        outcome=data.get("outcome"),
        feedback=data.get("feedback"),
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        "message": "Pilot record created successfully",
        "id": record.id,
        "user_code": user.user_code
    }), 201
