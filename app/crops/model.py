import os
import requests
import json


class Agromodel:

    def __init__(self):
        self.api_key = os.getenv("CENCORI_API_KEY")

    def normalize_analysis(self, analysis):

        for field in ["symptoms", "recommendations"]:

            value = analysis.get(field)

            if isinstance(value, str):
                analysis[field] = [value]

            elif value is None:
                analysis[field] = []

        return analysis

    def clean_json_text(self, text):

        text = text.strip()

        if text.startswith("```json"):
            text = text[7:]

        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    def analyze_image(
        self,
        image,
        mime_type="image/jpeg"
    ):

        if not self.api_key:
            return {
                "error": "cencori api not configured"
            }

        image_bytes = image.read()

        if not image_bytes:
            return {
                "error": "empty image"
            }

        data = {
            "model": "gemini-2.5-flash",
            "prompt": "Analyze this plant image. Return JSON only with crop, possible_disease, symptoms, severity, and recommendations. If the plant looks healthy, use possible_disease as \"No visible disease\", severity as \"Healthy\", symptoms as an empty array, and give one short monitoring recommendation. Keep symptoms and recommendations short.",
            "response_format": "json"
        }

        print("MODEL BEING SENT:", data["model"])
        print("IMAGE BYTES:", len(image_bytes))
        print("IMAGE MIME:", mime_type)

        response = requests.post(
            "https://cencori.com/api/ai/vision",

            headers={
                "CENCORI_API_KEY": self.api_key
            },

            files={
                "file": (
                    "plant",
                    image_bytes,
                    mime_type
                )
            },

            data=data,

            timeout=60
        )

        print("CENCORI STATUS:", response.status_code)
        print("CENCORI RESPONSE:", response.text)

        try:
            response_data = response.json()

        except ValueError:

            return {
                "error": "Invalid response from Cencori",
                "status": response.status_code
            }

        if response.status_code != 200:

            return {
                "error": "Cencori request failed",
                "status": response.status_code,
                "message": response_data.get(
                    "message",
                    "Unknown Cencori error"
                )
            }

        analysis_text = response_data.get("analysis")

        if not analysis_text:

            return {
                "error": "AI analysis was not returned"
            }

        try:

            analysis_text = self.clean_json_text(
                analysis_text
            )

            analysis = json.loads(
                analysis_text
            )

            analysis = self.normalize_analysis(
                analysis
            )

        except json.JSONDecodeError:

            print("FIRST AI RESPONSE INVALID. RETRYING...")

            retry_data = {

                "model": "gemini-2.5-flash",

                "response_format": "json",

                "prompt": (
                    "JSON only: "
                    "crop, possible_disease, symptoms, "
                    "severity, recommendations. "
                    "Max 1 symptom and 1 recommendation. "
                    "Short phrases. "
                    "No markdown."
                )
            }

            retry_response = requests.post(

                "https://cencori.com/api/ai/vision",

                headers={
                    "CENCORI_API_KEY": self.api_key
                },

                files={
                    "file": (
                        "plant",
                        image_bytes,
                        mime_type
                    )
                },

                data=retry_data,

                timeout=60
            )

            print("RETRY STATUS:", retry_response.status_code)
            print("RETRY RESPONSE:", retry_response.text)

            if retry_response.status_code != 200:

                return {
                    "error": "AI retry failed",
                    "status": retry_response.status_code
                }

            try:

                retry_result = retry_response.json()

                retry_text = retry_result.get("analysis")

                if not retry_text:
                    return {
                        "error": "AI retry returned no analysis"
                    }

                retry_text = self.clean_json_text(
                    retry_text
                )

                analysis = json.loads(
                    retry_text
                )

                analysis = self.normalize_analysis(
                    analysis
                )

            except (
                ValueError,
                TypeError,
                json.JSONDecodeError
            ):

                return {
                    "error": "AI returned invalid JSON"
                }

        return {
            "analysis": analysis,
            "model": response_data.get("model"),
            "provider": response_data.get("provider"),
            "usage": response_data.get("usage"),
            "cost": response_data.get("cost"),
            "usedFallback": response_data.get(
                "usedFallback"
            ),
            "originalModel": response_data.get(
                "originalModel"
            ),
            "originalProvider": response_data.get(
                "originalProvider"
            )
        }
