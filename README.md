# 🦤 DoDocu

**Making paper clutter as extinct as the Dodo.**

DoDocu is an AI-powered document and receipt scanner built with **Python, Streamlit, Google Gemini, and Neon PostgreSQL**.

Users can upload a receipt or document image, extract structured information using Gemini, review the extracted information, and save the record to a PostgreSQL database.

## ✨ Version 1.0 Features

* 📷 Upload receipt/document images
* 🤖 Extract information using Google Gemini
* 📝 Review and edit extracted information
* 💾 Save records to Neon PostgreSQL
* 📊 View saved records and basic analytics
* 🐳 Docker-ready for deployment

## 🛠️ Tech Stack

* **Python**
* **Streamlit** — Web application
* **Google Gemini API** — AI document extraction
* **Neon PostgreSQL** — Database
* **SQLAlchemy** — Database interaction
* **Docker** — Containerization

## 🚀 Run Locally

Create and activate your Python environment, then install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_neon_database_url
```

Start the application:

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔐 Environment Variables

The following variables are required:

| Variable         | Description                       |
| ---------------- | --------------------------------- |
| `GEMINI_API_KEY` | Google Gemini API key             |
| `DATABASE_URL`   | Neon PostgreSQL connection string |

**Do not commit `.env` or API keys to GitHub.**

## 📁 Project Structure

```text
dodocu_app/
├── app.py
├── database.py
├── gemini_service.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

## 📌 Version

**DoDocu v1.0.0**

Initial MVP focused on AI document extraction, human review, database persistence, and basic analytics.

## 🔮 Future Enhancements

* Receipt line-item extraction
* Advanced analytics and spending ledger
* Document search and filtering
* Calendar/event integration
* Improved validation and error handling
* User authentication
