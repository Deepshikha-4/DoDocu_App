
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
    raise ValueError("GEMINI_API_KEY is not set.")


# ============================================================
# CLASSIFICATION OPTIONS
# ============================================================

# Document type describes the format or nature of the document.
DOCUMENT_TYPES = [
    "receipt",
    "invoice",
    "handwritten_note",
    "other",
]

# Category describes the subject or purpose of the document.
DOCUMENT_CATEGORIES = [
    "grocery",
    "clothing",
    "restaurant",
    "travel",
    "electronics",
    "official",
    "general",
]


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)


# ============================================================
# PROMPT
# ============================================================

def build_prompt():
    """
    Build the Gemini extraction prompt dynamically from the
    document templates.

    Document type and category are independent classifications:
    - document_type describes what kind of document it is.
    - category describes its subject or purpose.
    """

    template_information = {}

    for category, template in DOCUMENT_TEMPLATES.items():

        template_information[category] = {
            "description": template.get(
                "description",
                "",
            ),
            "fields": [
                field[0]
                for field in template.get("fields", [])
            ],
            "has_items": template.get(
                "has_items",
                False,
            ),
        }

    return f"""
You are DoDocu, an AI document and receipt extraction assistant.

Analyse the uploaded document image and extract its information.

CLASSIFICATION

Determine TWO independent values.

1. document_type

This describes the type or format of the document.

Choose exactly one of:
{json.dumps(DOCUMENT_TYPES, indent=2)}

Definitions:
- receipt: Evidence of a completed purchase or payment.
- invoice: A bill or request for payment for goods or services.
- handwritten_note: A document primarily containing handwritten
  notes or information.
- other: Any document that does not fit the types above.

Do not classify a document as an invoice merely because it contains
prices. Use invoice only when the document is identifiable as an
invoice or bill.

2. category

This describes the subject or purpose of the document.

Choose exactly one of:
{json.dumps(DOCUMENT_CATEGORIES, indent=2)}

Definitions:
- grocery: Groceries and food items purchased from grocery shops
  or supermarkets.
- clothing: Clothing, footwear and fashion purchases.
- restaurant: Restaurant, cafe, takeaway and food-service
  transactions.
- travel: Transport and travel documents or transactions,
  including bus, train, metro, taxi, flight and other travel
  tickets or receipts.
- electronics: Electronic devices, equipment and accessories.
- official: Official, administrative, government or institutional
  documents.
- general: Documents that do not clearly fit another category.

IMPORTANT CLASSIFICATION RULES

- Document type and category must be determined independently.
- An invoice is a document type, NOT a category.
- A flight ticket is not a document type or category by itself.
  Classify it as document_type "other" and category "travel",
  unless the document clearly meets another document-type definition.
- A bus ticket, train ticket or taxi receipt should normally use
  category "travel".
- A restaurant receipt should normally use document_type "receipt"
  and category "restaurant".
- A grocery receipt should normally use document_type "receipt"
  and category "grocery".
- An invoice for electronic equipment should use document_type
  "invoice" and category "electronics".
- Do not use "travel" as a document_type.
- Do not use "invoice" as a category.
- Use "general" when the subject cannot be confidently classified.
- Return the exact lowercase values from the permitted lists.
- Never invent a new document_type or category.

CATEGORY-SPECIFIC EXTRACTION GUIDANCE

The following templates describe the category-specific fields
supported by DoDocu:

{json.dumps(template_information, indent=2)}

Use these templates as guidance for relevant details and line items.
The template keys describe categories, not document types.

OUTPUT FORMAT

Return ONLY valid JSON using this structure:

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

EXTRACTION RULES

1. Do not invent information. Use null for unavailable numeric
   values and empty strings for unavailable text values.

2. document_date should use YYYY-MM-DD when possible.

3. document_time should use 24-hour HH:MM format when a transaction,
   purchase, issue or document time is explicitly visible.
   Do not infer or guess a time. If unavailable, return null.

4. Numeric amounts must be numbers, not strings.

5. currency should preferably use an ISO currency code such as
   MUR, USD, EUR or GBP. If unknown, use an empty string.

6. summary should be one short sentence describing the document.

7. Use the details object for relevant category-specific information.
   Include only information supported by the document.

8. Extract individual line items from receipts and invoices when
   visible and relevant. Do not invent line items.

9. If quantity is not visible, use 1 when the item is clearly
   a single item.

10. For documents without line items, return an empty items array.

11. For handwritten notes and general documents, prioritise the
    information actually present in the document.

12. Ensure details is a JSON object and items is a JSON array.

13. Return valid JSON only. Do not use Markdown or code fences.

The human user will review and correct the extracted information
before it is saved.
"""


PROMPT = build_prompt()


# ============================================================
# CLASSIFICATION NORMALISATION
# ============================================================

def normalise_classification(data):
    """
    Normalise document_type and category to the supported values.

    Unrecognised or missing values receive safe defaults so that
    the user can review and correct the extraction before saving.
    """

    document_type = str(
        data.get("document_type") or ""
    ).strip().lower()

    category = str(
        data.get("category") or ""
    ).strip().lower()

    # Handle common alternative labels.
    document_type_aliases = {
        "handwritten note": "handwritten_note",
        "handwritten notes": "handwritten_note",
        "note": "handwritten_note",
        "bill": "invoice",
        "ticket": "other",
        "document": "other",
        "other document": "other",
    }

    category_aliases = {
        "food": "grocery",
        "supermarket": "grocery",
        "clothes": "clothing",
        "fashion": "clothing",
        "dining": "restaurant",
        "transport": "travel",
        "transportation": "travel",
        "flight": "travel",
        "flights": "travel",
        "electronics and technology": "electronics",
        "government": "official",
        "administrative": "official",
        "other": "general",
    }

    document_type = document_type_aliases.get(
        document_type,
        document_type,
    )

    category = category_aliases.get(
        category,
        category,
    )

    # Ensure the values match the application's supported options.
    if document_type not in DOCUMENT_TYPES:
        document_type = "other"

    if category not in DOCUMENT_CATEGORIES:
        category = "general"

    data["document_type"] = document_type
    data["category"] = category

    return data


# ============================================================
# EXTRACTION
# ============================================================

def extract_document(image_bytes, mime_type):
    """
    Send a document image to Gemini and return structured data
    with normalised document_type and category values.
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

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    text = response.text.strip()

    # --------------------------------------------------------
    # Remove accidental Markdown code fences
    # --------------------------------------------------------

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].strip().lower() in (
            "```",
            "```json",
        ):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:
        data = json.loads(text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Gemini response must be a JSON object."
        )

    # --------------------------------------------------------
    # Ensure expected fields exist
    # --------------------------------------------------------

    defaults = {
        "document_type": "",
        "category": "",
        "merchant": "",
        "document_date": "",
        "document_time": "",
        "currency": "",
        "subtotal": None,
        "tax": None,
        "total": None,
        "summary": "",
        "details": {},
        "items": [],
    }

    for key, default in defaults.items():
        data.setdefault(key, default)


    # Validate structures

    if not isinstance(data["details"], dict):
        data["details"] = {}

    if not isinstance(data["items"], list):
        data["items"] = []

    # Normalise classification values

    data = normalise_classification(data)

    # Normalise optional text fields

    for key in (
        "merchant",
        "document_date",
        "document_time",
        "currency",
        "summary",
    ):
        if data.get(key) is None:
            data[key] = ""

    # Empty or missing time should remain an empty string.
    if not str(data.get("document_time", "")).strip():
        data["document_time"] = ""

    return data
