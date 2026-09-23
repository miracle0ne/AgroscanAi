import os
import base64
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

    def analyze_image(self, image, mime_type="image/jpeg"):

        if not self.api_key:
            return {
                "error": "cencori api not configured"
            }

        image_bytes = image.read()

        data = {
            
            "model": "gpt-5.4-mini",
            

            "prompt": (
                "Analyze this plant image. "
                "Return JSON only with exactly these fields: "
                "crop, possible_disease, symptoms, severity, recommendations. "
                "If uncertain, use Unknown. "
                "Return at most 3 short symptoms and 3 short recommendations. "
                "Keep each item under 10 words. "
                "Keep the JSON compact."
            ),
          "response_format": "json"
        }

        print("MODEL BEING SENT:", data["model"])

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

        try:
            analysis_text=self.clean_json_text(analysis_text)

            analysis = json.loads(analysis_text)
            analysis = self.normalize_analysis(analysis)

        except json.JSONDecodeError:

            print("FIRST AI RESPONSE INVALID. RETRYING...")

            retry_data_payload = {
                "model": "gpt-5.4-mini",
                "response_format": "json",

                "prompt": (
                    "JSON only: "
                    "crop, possible_disease, symptoms, severity, recommendations. "
                    "Max 1 symptom and 1 recommendation. "
                    "Short phrases. No markdown."
                )
            }

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

            print("RETRY STATUS:", retry_response.status_code)
            print("RETRY RESPONSE:", retry_response.text)

            if retry_response.status_code != 200:
                return {
                    "error": "AI retry failed",
                    "status": retry_response.status_code
                }

            retry_data = retry_response.json()

            retry_text = retry_data.get("analysis")

            if not retry_text:
                return {
                    "error": "AI retry returned no analysis"
                }

            try:
                retry_text = retry_text.strip()

                if retry_text.startswith("```json"):
                    retry_text = retry_text[7:]

                if retry_text.startswith("```"):
                    retry_text = retry_text[3:]

                if retry_text.endswith("```"):
                    retry_text = retry_text[:-3]

                retry_text = retry_text.strip()
                
                analysis = json.loads(retry_text)
                analysis=self.normalize_analysis(analysis)

            except json.JSONDecodeError:

                return {
                    "error": "AI returned invalid JSON after retry",
                    "raw_analysis": retry_text
                }

            return {
                "analysis": analysis,
                "model": retry_data.get("model"),
                "provider": retry_data.get("provider"),
                "usage": retry_data.get("usage"),
                "cost": retry_data.get("cost"),
                "usedFallback": retry_data.get("usedFallback"),
                "originalModel": retry_data.get("originalModel"),
                "originalProvider": retry_data.get(
                    "originalProvider"
                )
            }

        return {
            "analysis": analysis,
            "model": data.get("model"),
            "provider": data.get("provider"),
            "usage": data.get("usage"),
            "cost": data.get("cost"),
            "usedFallback": data.get("usedFallback"),
            "originalModel": data.get("originalModel"),
            "originalProvider": data.get(
                "originalProvider"
            )
        }
    