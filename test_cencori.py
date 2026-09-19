import os
import base64
import requests

api_key = os.getenv("CENCORI_API_KEY")

with open("app/static/images/tomato1.jpeg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "gemini-2.5-flash",
    "image_base64": image_base64,
    "prompt": "Describe this plant image briefly."
}

response = requests.post(
    "https://cencori.com/api/ai/vision",
    headers={
        "CENCORI_API_KEY": api_key,
        "Content-Type": "application/json"
    },
    json=payload
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
