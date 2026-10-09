# gemini_service.py

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from document_templates import DOCUMENT_TEMPLATES


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# PROMPT
# ============================================================

def build_prompt():
    """
    Build the Gemini extraction prompt dynamically from the
    document templates.
    """

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
    "document_time": "",
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

4. document_time should use 24-hour HH:MM format when a transaction,
   purchase, issue or document time is visible.

5. Do not infer or guess document_time.
   If a time is not visible or cannot be determined, return null.

6. Numeric amounts must be numbers, not strings.

7. currency should preferably use an ISO currency code such as
   MUR, USD, EUR or GBP.

8. summary should be one short sentence.

9. Use the "details" object for category-specific information.

10. Only include details that are relevant to the detected category.

11. For receipts and invoices, extract individual line items
    when they are visible.

12. Do not invent line items.

13. If quantity is not visible, use 1 when the item is clearly
    a single item.

14. For documents without line items, return an empty items array.

15. For handwritten notes or general documents, focus on the
    available information.

16. Return valid JSON only.
    Do not use Markdown or code fences.

Important:

The human user will review and correct the extracted information
before it is saved.
"""


PROMPT = build_prompt()


# ============================================================
# EXTRACTION
# ============================================================

def extract_document(
    image_bytes,
    mime_type,
):
    """
    Send a document image to Gemini and return structured data.
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            PROMPT,
        ],
    )

    text = response.text.strip()

    # --------------------------------------------------------
    # Remove accidental Markdown code fences
    # --------------------------------------------------------

    if text.startswith("```"):

        text = text.replace(
            "```json",
            "",
        )

        text = text.replace(
            "```",
            "",
        )

        text = text.strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = json.loads(text)

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Ensure expected structures exist
    # --------------------------------------------------------

    data.setdefault(
        "document_type",
        "",
    )

    data.setdefault(
        "category",
        "",
    )

    data.setdefault(
        "merchant",
        "",
    )

    data.setdefault(
        "document_date",
        "",
    )

    data.setdefault(
        "document_time",
        "",
    )

    data.setdefault(
        "currency",
        "",
    )

    data.setdefault(
        "subtotal",
        None,
    )

    data.setdefault(
        "tax",
        None,
    )

    data.setdefault(
        "total",
        None,
    )

    data.setdefault(
        "summary",
        "",
    )

    data.setdefault(
        "details",
        {},
    )

    data.setdefault(
        "items",
        [],
    )

    # --------------------------------------------------------
    # Validate structures
    # --------------------------------------------------------

    if not isinstance(
        data["details"],
        dict,
    ):

        data["details"] = {}

    if not isinstance(
        data["items"],
        list,
    ):

        data["items"] = []

    # --------------------------------------------------------
    # Normalise empty time
    # --------------------------------------------------------

    if not data.get("document_time"):

        data["document_time"] = ""

    return data