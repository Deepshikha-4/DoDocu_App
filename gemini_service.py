# gemini_service.py

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from document_templates import DOCUMENT_TEMPLATES

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=API_KEY)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

def build_prompt():
    template_information = {}

    for category, template in DOCUMENT_TEMPLATES.items():
        template_information[category] = {
            "description": template["description"],
            "fields": [
                field[0]
                for field in template["fields"]
            ],
            "has_items": template["has_items"],
        }

    return f"""
You are DoDocu, an AI document and receipt extraction assistant.
Analyze the uploaded document image.
First determine the document category.

Available categories:

{json.dumps(template_information, indent=2)}

Return ONLY valid JSON.

Use this structure:

{{
    "document_type": "",
    "category": "",
    "merchant": "",
    "document_date": "",
    "currency": "",
    "subtotal": null,
    "tax": null,
    "total": null,
    "summary": "",
    "details": {{}},
    "items": []
}}

For items, use this structure:

[
    {{
        "description": "",
        "quantity": 1,
        "unit_price": null,
        "total": null
    }}
]

Rules:

1. Do not invent information.
2. Use null when information cannot be determined.
3. document_date should use YYYY-MM-DD when possible.
4. Numeric amounts must be numbers, not strings.
5. currency should preferably use an ISO currency code such as MUR, USD, EUR or GBP.
6. summary should be one short sentence.
7. Use the "details" object for category-specific information.
8. Only include details that are relevant to the detected category.
9. For receipts and invoices, extract individual line items when they are visible.
10. Do not invent line items.
11. If quantity is not visible, use 1 when the item is clearly a single item.
12. For documents without line items, return an empty items array.
13. For handwritten notes or general documents, focus on the available information.
14. Return valid JSON only. Do not use Markdown or code fences.

Important:
The human user will review and correct the extracted information before it is saved.
"""

PROMPT = build_prompt()

def extract_document(image_bytes, mime_type):
    """Send a document image to Gemini and return structured data."""

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),
            PROMPT,
        ],
    )
    text = response.text.strip()

    # Remove accidental Markdown code fences
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    # Ensure expected structures exist
    data.setdefault("details", {})
    data.setdefault("items", [])

    if not isinstance(data["details"], dict):
        data["details"] = {}

    if not isinstance(data["items"], list):
        data["items"] = []

    return data