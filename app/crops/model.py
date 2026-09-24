import os
import requests
import time
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

    def parse_analysis(self, text):

        text = self.clean_json_text(text)

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            pass

        # Try to extract the JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:

            candidate = text[start:end + 1]

            try:
                return json.loads(candidate)

            except json.JSONDecodeError:
                pass

        return None

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

        data = {

            "model": "gpt-5.4-mini",

            "prompt": (
                "Analyze this plant image. "
                "Return ONLY valid JSON. "
                "Use exactly these fields: "
                "crop, possible_disease, symptoms, severity, "
                "recommendations. "
                "Use English only. "
                "Use ASCII characters only. "
                "No markdown. "
                "No code fences. "
                "No explanation. "
                "Return one single-line JSON object. "
                "Symptoms must be an array of up to 3 short phrases. "
                "Recommendations must be an array of up to 3 short phrases. "
                "If uncertain, use Unknown."
            ),

            "response_format": "json"
        }

        print("MODEL BEING SENT:", data["model"])

        start_time = time.perf_counter()

        response = requests.post(
            "https://cencori.com/api/ai/vision",
            headers={
                "CENCORI_API_KEY": self.api_key
            },
            files={
                "file": (
                    "plant.jpg",
                    image_bytes,
                    mime_type
                )
            },
            data=data
        )

        elapsed = time.perf_counter() - start_time

        print("CENCORI TIME:", round(elapsed, 2), "seconds")
        print("CENCORI STATUS:", response.status_code)
        print("CENCORI RESPONSE:", response.text)

        data = response.json()

        if response.status_code != 200:
            return {
                "error": "Cencori request failed",
                "status": response.status_code,
                "message": data.get(
                    "message",
                    "Unknown Cencori error"
                )
            }

        analysis_text = data.get("analysis")

        if not analysis_text:
            return {
                "error": "AI analysis was not returned"
            }

        analysis = self.parse_analysis(
            analysis_text
        )

        if analysis is not None:

            analysis = self.normalize_analysis(
                analysis
            )

            return {
                "analysis": analysis,
                "model": data.get("model"),
                "provider": data.get("provider"),
                "usage": data.get("usage"),
                "cost": data.get("cost"),
                "usedFallback": data.get(
                    "usedFallback"
                ),
                "originalModel": data.get(
                    "originalModel"
                ),
                "originalProvider": data.get(
                    "originalProvider"
                )
            }

        print(
            "FIRST AI RESPONSE INVALID. RETRYING..."
        )

        retry_data_payload = {

            "model": "gpt-5.4-mini",

            "response_format": "json",

            "prompt": (
                "Look at the plant image again. "
                "Return ONLY one valid JSON object. "
                "One line only. "
                "English ASCII characters only. "
                "No markdown. "
                "No code fences. "
                "No explanation. "
                "Use exactly these fields: "
                "crop, possible_disease, symptoms, severity, "
                "recommendations. "
                "symptoms must be an array with exactly 1 short item. "
                "recommendations must be an array with exactly 1 "
                "short safe recommendation. "
                "If uncertain, use Unknown."
            )
        }

        retry_start_time = time.perf_counter()

        retry_response = requests.post(
            "https://cencori.com/api/ai/vision",
            headers={
                "CENCORI_API_KEY": self.api_key
            },
            files={
                "file": (
                    "plant.jpg",
                    image_bytes,
                    "image/jpeg"
                )
            },
            data=retry_data_payload
        )

        retry_elapsed = time.perf_counter() - retry_start_time

        print(
            "RETRY TIME:",
            round(retry_elapsed, 2),
            "seconds"
        )

        print(
            "RETRY STATUS:",
            retry_response.status_code
        )

        print(
            "RETRY RESPONSE:",
            retry_response.text
        )

        if retry_response.status_code != 200:
            return {
                "error": "AI retry failed",
                "status": retry_response.status_code
            }

        retry_data = retry_response.json()

        retry_text = retry_data.get(
            "analysis"
        )

        if not retry_text:
            return {
                "error": "AI retry returned no analysis"
            }

        analysis = self.parse_analysis(
            retry_text
        )

        if analysis is None:

            return {
                "error": (
                    "AI returned invalid JSON "
                    "after retry"
                ),
                "raw_analysis": retry_text
            }

        analysis = self.normalize_analysis(
            analysis
        )

        return {
            "analysis": analysis,
            "model": retry_data.get("model"),
            "provider": retry_data.get("provider"),
            "usage": retry_data.get("usage"),
            "cost": retry_data.get("cost"),
            "usedFallback": retry_data.get(
                "usedFallback"
            ),
            "originalModel": retry_data.get(
                "originalModel"
            ),
            "originalProvider": retry_data.get(
                "originalProvider"
            )
        }
