from flask import Blueprint, render_template, request
import os
from werkzeug.utils import secure_filename
from app.crops.registry import CropAgent
import io
import base64
main = Blueprint(
    "main",
    __name__
)


@main.route("/")
def home():
    return render_template("main/home.html")


@main.route("/scan", methods=["POST", "GET"])
def scan():

    if request.method == "POST":

        file = request.files.get("plant_image")
        crop = request.form.get("crop")

        if not file or file.filename == "":
            return render_template("main/scan.html")

        # Read image into memory
        image_bytes = file.read()

        # Analyze image directly from memory
        agent = CropAgent()

        result = agent.analyze_crop(
            crop,
            io.BytesIO(image_bytes)
        )

        print("ANALYSIS RESULT:", result)

        # Convert image to Base64 for displaying in browser
        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            f"data:{file.mimetype};base64,{image_base64}"
        )

        ai_analysis = result["ai_Analysis"]

        return render_template(
            "main/result.html",
            image_url=image_url,
            crop=result["crop"],
            ai_analysis=ai_analysis
        )

    return render_template("main/scan.html")