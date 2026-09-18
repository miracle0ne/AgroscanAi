from flask import Blueprint, render_template, request
import os
from werkzeug.utils import secure_filename
from app.crops.registry import CropAgent

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

        filename = secure_filename(file.filename)

        upload_folder = os.path.join(
            "app",
            "static",
            "uploads"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image_path = os.path.join(
            upload_folder,
            filename
        )

        # Save uploaded image first
        file.save(image_path)

        # Analyze using saved file path
        agent = CropAgent()

        result = agent.analyze_crop(
            crop,
            image_path
        )

        print(result)

        image_url = f"uploads/{filename}"

        ai_analysis = result["ai_Analysis"]

        return render_template(
            "main/result.html",
            image_url=image_url,
            crop=result["crop"],
            ai_analysis=ai_analysis
        )

    return render_template("main/scan.html")