from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app.crops.registry import CropAgent
from app.utils.image import prepare_image
from app.extensions import db
from app.pilot.models import PilotRecord

import io
import base64
import json


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("main/home.html")


@main.route("/about")
def about():
    return render_template("main/about.html")


@main.route("/dashboard")
@login_required
def dashboard():
    recent_scans = (
        PilotRecord.query
        .filter_by(user_id=current_user.id)
        .order_by(PilotRecord.created_at.desc())
        .limit(5)
        .all()
    )

    total_scans = (
        PilotRecord.query
        .filter_by(user_id=current_user.id)
        .count()
    )

    return render_template(
        "main/dashboard.html",
        recent_scans=recent_scans,
        total_scans=total_scans
    )


@main.route("/scan", methods=["POST", "GET"])
@login_required
def scan():

    print("SCAN REQUEST RECEIVED")
    print(
        "CURRENT USER:",
        current_user.user_code,
        current_user.name
    )

    if request.method == "POST":

        file = request.files.get("plant_image")
        crop = request.form.get("crop")

        print("FORM KEYS:", list(request.form.keys()))
        print("FILE KEYS:", list(request.files.keys()))
        print("CROP RECEIVED:", crop)
        print("CURRENT USER:", current_user.user_code)

        if not file or file.filename == "":
            print("SCAN STOP: image missing")
            return render_template("main/scan.html")

        user = current_user

        try:
            print("IMAGE PREPARATION START")

            image_bytes, mime_type = prepare_image(file)

            print(
                "IMAGE PREPARATION OK:",
                mime_type,
                len(image_bytes),
                "bytes"
            )

        except Exception as error:
            print("IMAGE ERROR:", error)
            return render_template("main/scan.html")

        try:
            print("AI ANALYSIS START")

            agent = CropAgent()

            result = agent.analyze_crop(
                crop,
                io.BytesIO(image_bytes),
                mime_type
            )

            print("ANALYSIS RESULT:", result)

        except Exception as error:
            print("AI ANALYSIS ERROR:", error)
            return render_template("main/scan.html")

        image_base64 = (
            base64
            .b64encode(image_bytes)
            .decode("utf-8")
        )

        image_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        ai_analysis = result.get(
            "ai_Analysis",
            {}
        )

        analysis = ai_analysis.get("analysis")

        if analysis:

            pilot_record = PilotRecord(
                user_id=user.id,
                crop=result.get("crop", crop),
                ai_diagnosis=analysis.get(
                    "possible_disease"
                ),
                symptoms=json.dumps(
                    analysis.get("symptoms", [])
                ),
                recommendations=json.dumps(
                    analysis.get("recommendations", [])
                )
            )

            db.session.add(pilot_record)
            db.session.commit()

            print(
                "PILOT RECORD SAVED:",
                pilot_record.id,
                user.user_code
            )

        else:
            print(
                "PILOT RECORD NOT SAVED:",
                ai_analysis.get("error")
            )

        return render_template(
            "main/result.html",
            image_url=image_url,
            crop=result.get("crop", crop),
            ai_analysis=ai_analysis,
            user_code=user.user_code
        )

    return render_template("main/scan.html")
@main.route("/profile")
@login_required
def profile():
    return render_template(
        "main/profile.html"
    )
@main.route("/history")
@login_required
def history():

    scans = (
        PilotRecord.query
        .filter_by(user_id=current_user.id)
        .order_by(PilotRecord.created_at.desc())
        .all()
    )

    for scan in scans:

        try:
            scan.symptoms = (
                json.loads(scan.symptoms)
                if isinstance(scan.symptoms, str)
                else scan.symptoms
            )
        except (json.JSONDecodeError, TypeError):
            scan.symptoms = [scan.symptoms] if scan.symptoms else []

        try:
            scan.recommendations = (
                json.loads(scan.recommendations)
                if isinstance(scan.recommendations, str)
                else scan.recommendations
            )
        except (json.JSONDecodeError, TypeError):
            scan.recommendations = (
                [scan.recommendations]
                if scan.recommendations
                else []
            )

    return render_template(
        "main/history.html",
        scans=scans
    )
