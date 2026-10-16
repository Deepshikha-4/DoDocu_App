# document_templates.py
"""Canonical DoDocu document types, subject categories, and review fields.

Document type answers: "What kind of document is this?"
Category answers: "What subject or spending area does it relate to?"
"""

DOCUMENT_TYPES = {
    "receipt": "🧾 Receipt",
    "invoice": "📑 Invoice",
    "ticket": "🎫 Ticket",
    "handwritten_note": "✍️ Handwritten Note",
    "other": "📄 Other Document",
}

CATEGORIES = {
    "grocery": {
        "label": "🛒 Grocery",
        "description": "Supermarket and grocery purchases.",
    },
    "clothing": {
        "label": "👕 Clothing",
        "description": "Clothing, footwear and accessories.",
    },
    "restaurant": {
        "label": "🍽️ Restaurant & Dining",
        "description": "Restaurants, cafés, bakeries and food establishments.",
    },
    "travel": {
        "label": "🧳 Travel",
        "description": "Bus, taxi, train, metro, flight and other travel-related costs or documents.",
    },
    "electronics": {
        "label": "💻 Electronics",
        "description": "Electronic devices, equipment and accessories.",
    },
    "official": {
        "label": "🏛️ Official",
        "description": "Government, administrative and other official documents or payments.",
    },
    "general": {
        "label": "📄 General",
        "description": "Documents that do not fit another listed category.",
    },
}

# Fields are selected by document type, not by category.
# Categories classify the subject area independently.
DOCUMENT_TEMPLATES = {
    "receipt": {
        "label": DOCUMENT_TYPES["receipt"],
        "description": "Proof of payment for goods or services.",
        "fields": [
            ("receipt_number", "Receipt Number", "text"),
            ("payment_method", "Payment Method", "text"),
            ("discount", "Discount", "number"),
            ("tip", "Tip", "number"),
            ("service_charge", "Service Charge", "number"),
        ],
        "has_items": True,
    },
    "invoice": {
        "label": DOCUMENT_TYPES["invoice"],
        "description": "A request for payment issued by a supplier or service provider.",
        "fields": [
            ("invoice_number", "Invoice Number", "text"),
            ("invoice_date", "Invoice Date", "text"),
            ("due_date", "Due Date", "text"),
            ("supplier", "Supplier", "text"),
            ("customer", "Customer", "text"),
            ("payment_terms", "Payment Terms", "text"),
            ("discount", "Discount", "number"),
        ],
        "has_items": True,
    },
    "ticket": {
        "label": DOCUMENT_TYPES["ticket"],
        "description": "A transport or travel ticket.",
        "fields": [
            ("operator", "Operator / Airline", "text"),
            ("ticket_number", "Ticket Number", "text"),
            ("booking_reference", "Booking Reference", "text"),
            ("passenger_name", "Passenger Name", "text"),
            ("departure", "Departure / Origin", "text"),
            ("destination", "Destination", "text"),
            ("departure_airport", "Departure Airport", "text"),
            ("destination_airport", "Destination Airport", "text"),
            ("departure_time", "Departure Time", "text"),
            ("arrival_time", "Arrival Time", "text"),
            ("flight_number", "Flight Number", "text"),
            ("seat_number", "Seat Number", "text"),
            ("payment_method", "Payment Method", "text"),
            ("fare", "Fare", "number"),
        ],
        "has_items": False,
    },
    "handwritten_note": {
        "label": DOCUMENT_TYPES["handwritten_note"],
        "description": "A note or record written by hand.",
        "fields": [
            ("title", "Title", "text"),
            ("reference_number", "Reference Number", "text"),
            ("organization", "Organization / Person", "text"),
            ("notes", "Notes", "text"),
        ],
        "has_items": False,
    },
    "other": {
        "label": DOCUMENT_TYPES["other"],
        "description": "A supported document that does not fit another document type.",
        "fields": [
            ("title", "Title", "text"),
            ("reference_number", "Reference Number", "text"),
            ("organization", "Organization / Person", "text"),
            ("notes", "Notes", "text"),
        ],
        "has_items": False,
    },
}

DOCUMENT_TYPE_ALIASES = {
    "document": "other",
    "general": "other",
    "general document": "other",
    "handwritten note": "handwritten_note",
    "bus": "ticket",
    "flight": "ticket",
    "bus ticket": "ticket",
    "flight ticket": "ticket",
    "travel ticket": "ticket",
    "transport ticket": "ticket",
    "booking confirmation": "ticket",
}

CATEGORY_ALIASES = {
    "groceries": "grocery",
    "dining": "restaurant",
    "food": "restaurant",
    "transport": "travel",
    "flight": "travel",
    "clothing and accessories": "clothing",
    "invoice": "general",  # Legacy category; invoice is now a document type.
}


def normalize_document_type(value):
    """Return a supported document-type code, including legacy labels."""
    if not value:
        return "other"
    key = str(value).strip().casefold().replace("-", "_")
    if key in DOCUMENT_TYPES:
        return key
    return DOCUMENT_TYPE_ALIASES.get(key.replace("_", " "), "other")


def normalize_category(value):
    """Return a supported category code, including legacy category values."""
    if not value:
        return "general"
    key = str(value).strip().casefold().replace("-", "_")
    if key in CATEGORIES:
        return key
    return CATEGORY_ALIASES.get(key.replace("_", " "), "general")


def get_template(document_type):
    """Return the field template for a document type."""
    return DOCUMENT_TEMPLATES.get(
        normalize_document_type(document_type),
        DOCUMENT_TEMPLATES["other"],
    )


def get_template_options():
    """Return document types suitable for a Streamlit selectbox."""
    return DOCUMENT_TYPES.copy()
