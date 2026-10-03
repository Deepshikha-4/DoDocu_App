# document_templates.py

DOCUMENT_TEMPLATES = {
    "grocery": {
        "label": "🛒 Grocery Receipt",
        "description": "Supermarket, grocery store and food purchases.",
        "fields": [
            ("receipt_number", "Receipt Number", "text"),
            ("payment_method", "Payment Method", "text"),
            ("discount", "Discount", "number"),
        ],
        "has_items": True,
    },

    "restaurant": {
        "label": "🍽️ Restaurant Receipt",
        "description": "Restaurants, cafés, bakeries and food establishments.",
        "fields": [
            ("receipt_number", "Receipt Number", "text"),
            ("payment_method", "Payment Method", "text"),
            ("tip", "Tip", "number"),
            ("service_charge", "Service Charge", "number"),
        ],
        "has_items": True,
    },

    "transport": {
        "label": "🚌 Bus / Transport Ticket",
        "description": "Bus, taxi, train and other transport tickets.",
        "fields": [
            ("operator", "Operator", "text"),
            ("ticket_number", "Ticket Number", "text"),
            ("passenger_name", "Passenger Name", "text"),
            ("departure", "Departure", "text"),
            ("destination", "Destination", "text"),
            ("departure_time", "Departure Time", "text"),
            ("arrival_time", "Arrival Time", "text"),
            ("seat_number", "Seat Number", "text"),
            ("payment_method", "Payment Method", "text"),
            ("fare", "Fare", "number"),
        ],
        "has_items": False,
    },

    "flight": {
        "label": "✈️ Flight / Travel Ticket",
        "description": "Flights and other travel booking documents.",
        "fields": [
            ("airline", "Airline", "text"),
            ("passenger_name", "Passenger Name", "text"),
            ("ticket_number", "Ticket Number", "text"),
            ("booking_reference", "Booking Reference", "text"),
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

    "invoice": {
        "label": "🧾 Invoice",
        "description": "Business and supplier invoices.",
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

    "general": {
        "label": "📄 General Document",
        "description": "Documents that do not fit another category.",
        "fields": [
            ("title", "Title", "text"),
            ("reference_number", "Reference Number", "text"),
            ("organization", "Organization / Person", "text"),
            ("notes", "Notes", "text"),
        ],
        "has_items": False,
    },
}

def get_template(category):
    """Return a document template or the general template."""
    return DOCUMENT_TEMPLATES.get(
        category,
        DOCUMENT_TEMPLATES["general"]
    )

def get_template_options():
    """Return categories suitable for a Streamlit selectbox."""
    return {
        category: template["label"]
        for category, template in DOCUMENT_TEMPLATES.items()
    }