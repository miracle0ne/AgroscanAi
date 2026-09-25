from flask import Blueprint, render_template, request

from app.crops.registry import CropAgent
from app.utils.image import prepare_image
from app.models.users import User
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


@main.route("/scan", methods=["POST", "GET"])
def scan():

    print("SCAN REQUEST RECEIVED")

    if request.method == "POST":

        file = request.files.get("plant_image")
        crop = request.form.get("crop")
        user_code = request.form.get("user_code")

        print("FORM KEYS:", list(request.form.keys()))
        print("FILE KEYS:", list(request.files.keys()))
        print("CROP RECEIVED:", crop)
        print("USER CODE RECEIVED:", user_code)

        if not user_code:
            print("SCAN STOP: user_code missing")
            return render_template("main/scan.html")

        user = User.query.filter_by(
            user_code=user_code
        ).first()

        if not user:
            print("SCAN STOP: user not found")
            return render_template("main/scan.html")

        if not file or file.filename == "":
            print("SCAN STOP: image missing")
            return render_template("main/scan.html")

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

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

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
