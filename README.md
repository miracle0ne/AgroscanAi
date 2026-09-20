# 🌿 AgroScan AI

AgroScan AI is an AI-powered plant disease detection platform designed to help African farmers identify possible plant diseases from uploaded plant images.

## 🚀 Live Demo

https://agroscanai.pxxlspace.cv/

## 🎯 What AgroScan AI Does

1. Farmer selects a supported crop.
2. Farmer uploads a plant image.
3. AgroScan AI sends the image for AI vision analysis.
4. The system returns:
   - Detected crop
   - Possible disease
   - Severity
   - Visible symptoms
   - Recommended actions
5. The result is displayed in a simple farmer-friendly interface.

## 🧠 AI Analysis

AgroScan AI uses **Cencori** for vision analysis.

The application currently uses:

- Model: `gemini-2.5-flash`
- Provider: Google
- Image-based plant analysis
- Structured JSON responses
- Retry handling for incomplete AI responses

## 📊 Web Analytics

**Sabilytics** is integrated into the application to provide website analytics and help understand how users interact with the platform.

## ☁️ Deployment

AgroScan AI is deployed using **Pxxl**.

Live application:

https://agroscanai.pxxlspace.cv/

## 🛠️ Technology Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Migrate
- Cencori
- Sabilytics
- PostgreSQL
- Gunicorn
- Bootstrap
- HTML/CSS
- Pillow
- NumPy

## 📁 Project Structure

```text
AgroscanAi/
├── app/
│   ├── crops/
│   ├── main/
│   ├── templates/
│   └── ...
├── models/
├── requirements.txt
├── run.py
├── pxxl.toml
└── README.md
```

## ⚙️ Local Setup

Clone the repository:

    git clone https://github.com/miracle0ne/AgroscanAi.git
    cd AgroscanAi

## 🔐 Environment Variables

Store API keys and secrets in environment variables. Never commit them to Git.

## ⚠️ Disclaimer

AgroScan AI provides preliminary AI-generated information for educational and informational purposes. AI results should not be treated as a definitive agricultural diagnosis.

## 🌍 Vision

AgroScan AI aims to make plant health information more accessible to African farmers through affordable and easy-to-use AI technology.

## 👨‍💻 Built By

**MiracleSoft**

Powered by MiracleSoft.
