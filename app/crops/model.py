import os
import requests
import time
import json
import base64

from dotenv import load_dotenv

load_dotenv()


class Agromodel:

    def __init__(self):

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "deepseek/deepseek-v4.1-flash"
        )

        self.base_url = (
            "https://openrouter.ai/api/v1"
        )

    def normalize_analysis(self, analysis):

        for field in [
            "symptoms",
            "recommendations"
        ]:

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

        if not text or not isinstance(text, str):
            return None

        text = self.clean_json_text(text)

        try:

            return json.loads(text)

        except json.JSONDecodeError:

            pass

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:

            candidate = text[
                start:end + 1
            ]

            try:

                return json.loads(candidate)

            except json.JSONDecodeError:

                pass

        return None

    def _request_analysis(
        self,
        image_data_url,
        prompt
    ):

        payload = {

            "model": self.model,

            "messages": [

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url": image_data_url
                            }
                        }

                    ]
                }

            ],

            "temperature": 0,

            "max_tokens": 15000

        }

        response = requests.post(

            f"{self.base_url}/chat/completions",

            headers={

                "Authorization":
                    f"Bearer {self.api_key}",

                "Content-Type":
                    "application/json",

                "HTTP-Referer":
                    "https://agroscanai.pxxlspace.cv",

                "X-Title":
                    "AgroScan AI"

            },

            json=payload,

            timeout=90
        )

        return response

    def analyze_image(
        self,
        image,
        mime_type="image/jpeg"
    ):

        if not self.api_key:

            return {
                "error":
                    "openrouter api not configured"
            }

        image_bytes = image.read()

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_data_url = (
            f"data:{mime_type};base64,"
            f"{image_base64}"
        )

        prompt = (

            "Analyze this plant image for "
            "agricultural disease detection. "

            "Return ONLY valid JSON. "

            "Use exactly these fields: "
            "crop, possible_disease, symptoms, "
            "severity, recommendations. "

            "Use English only. "

            "Use ASCII characters only. "

            "No markdown. "
            "No code fences. "
            "No explanation. "

            "Return one single-line JSON object. "

            "Symptoms must be an array of "
            "up to 3 short phrases. "

            "Recommendations must be an array of "
            "up to 3 short phrases. "

            "If uncertain, use Unknown."

        )

        print(
            "OPENROUTER MODEL:",
            self.model
        )

        start_time = time.perf_counter()

        try:

            response = self._request_analysis(
                image_data_url,
                prompt
            )

        except requests.RequestException as error:

            return {
                "error":
                    "OpenRouter request failed",

                "message":
                    str(error)
            }

        elapsed = (
            time.perf_counter()
            - start_time
        )

        print(
            "OPENROUTER TIME:",
            round(elapsed, 2),
            "seconds"
        )

        print(
            "OPENROUTER STATUS:",
            response.status_code
        )

        print(
            "OPENROUTER RESPONSE:",
            response.text
        )

        try:

            data = response.json()

        except ValueError:

            return {
                "error":
                    "OpenRouter returned invalid JSON",

                "status":
                    response.status_code
            }

        if response.status_code != 200:

            error_data = data.get(
                "error",
                {}
            )

            if isinstance(error_data, dict):

                message = error_data.get(
                    "message",
                    "Unknown OpenRouter error"
                )

            else:

                message = str(error_data)

            return {
                "error":
                    "OpenRouter request failed",

                "status":
                    response.status_code,

                "message":
                    message
            }

        try:

            analysis_text = (
                data["choices"][0]
                ["message"]["content"]
            )

        except (
            KeyError,
            IndexError,
            TypeError
        ):

            return {
                "error":
                    "AI analysis was not returned"
            }

        analysis = self.parse_analysis(
            analysis_text
        )

        if analysis is not None:

            analysis = (
                self.normalize_analysis(
                    analysis
                )
            )

            return {
                "analysis": analysis,

                "model":
                    data.get("model"),

                "provider":
                    data.get("provider"),

                "usage":
                    data.get("usage")
            }

        print(
            "FIRST AI RESPONSE INVALID."
        )

        print(
            "RETRYING WITH OPENROUTER..."
        )

        retry_prompt = (

            "Look at the plant image again. "

            "Return ONLY one valid JSON object. "

            "One line only. "

            "English ASCII characters only. "

            "No markdown. "
            "No code fences. "
            "No explanation. "

            "Use exactly these fields: "
            "crop, possible_disease, symptoms, "
            "severity, recommendations. "

            "Symptoms must be an array with "
            "exactly 1 short item. "

            "Recommendations must be an array "
            "with exactly 1 short safe recommendation. "

            "If uncertain, use Unknown."

        )

        retry_start_time = (
            time.perf_counter()
        )

        try:

            retry_response = (
                self._request_analysis(
                    image_data_url,
                    retry_prompt
                )
            )

        except requests.RequestException as error:

            return {
                "error":
                    "OpenRouter retry failed",

                "message":
                    str(error)
            }

        retry_elapsed = (
            time.perf_counter()
            - retry_start_time
        )

        print(
            "OPENROUTER RETRY TIME:",
            round(retry_elapsed, 2),
            "seconds"
        )

        print(
            "OPENROUTER RETRY STATUS:",
            retry_response.status_code
        )

        print(
            "OPENROUTER RETRY RESPONSE:",
            retry_response.text
        )

        if retry_response.status_code != 200:

            return {
                "error":
                    "OpenRouter retry failed",

                "status":
                    retry_response.status_code
            }

        try:

            retry_data = (
                retry_response.json()
            )

        except ValueError:

            return {
                "error":
                    "OpenRouter retry returned invalid JSON"
            }

        try:

            retry_text = (
                retry_data["choices"][0]
                ["message"]["content"]
            )

        except (
            KeyError,
            IndexError,
            TypeError
        ):

            return {
                "error":
                    "OpenRouter retry returned no analysis"
            }

        analysis = self.parse_analysis(
            retry_text
        )

        if analysis is None:

            return {
                "error":
                    "AI returned invalid JSON "
                    "after retry",

                "raw_analysis":
                    retry_text
            }

        analysis = (
            self.normalize_analysis(
                analysis
            )
        )

        return {
            "analysis": analysis,

            "model":
                retry_data.get("model"),

            "provider":
                retry_data.get("provider"),

            "usage":
                retry_data.get("usage")
        }
