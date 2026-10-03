import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=API_KEY)


PROMPT = """
You are an AI document and receipt extraction assistant.

Analyze the uploaded image.

Determine whether it is:
- receipt
- invoice
- handwritten_note
- other

If it is a receipt, classify it into a useful category such as:
- grocery
- clothing
- restaurant
- bakery
- electronics
- fuel
- travel
- medical
- office
- other

Extract the information below.

Return ONLY valid JSON.

{
    "document_type": "",
    "category": "",
    "merchant": "",
    "receipt_date": "",
    "currency": "",
    "subtotal": 0,
    "tax": 0,
    "total": 0,
    "summary": ""
}

Rules:

- Use null when information cannot be determined.
- Do not invent information.
- receipt_date must use YYYY-MM-DD when possible.
- subtotal, tax and total must be numbers.
- currency should preferably be an ISO currency code such as MUR, USD, EUR, GBP.
- summary should be one short sentence.
"""
def extract_document(image_bytes, mime_type):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),
            PROMPT,
        ],
    )
    text = response.text.strip()

    # Remove accidental markdown code fences
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
    return json.loads(text)