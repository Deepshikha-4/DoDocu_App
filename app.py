# app.py

import io
from datetime import date

import pandas as pd
import streamlit as st
from PIL import Image

from database import (
    init_database,
    save_document,
    get_documents,
)

from gemini_service import extract_document

from document_templates import (
    DOCUMENT_TEMPLATES,
    get_template,
)

from analytics import (
    documents_to_dataframe,
    calculate_metrics,
    spending_by_category,
    spending_by_merchant,
    spending_over_time,
)

# PAGE CONFIG
st.set_page_config(
    page_title="DoDocu",
    page_icon="dodocu_icon.png",
    layout="wide"
)

# PRESENTATION FONT SIZE
st.markdown(
    """
    <style>

    /* Normal paragraph text */
    .stMarkdown p,
    .stMarkdown li {
        font-size: 18px !important;
        line-height: 1.5 !important;
    }

    /* Main section headings */
    h1 {
        font-size: 34px !important;
    }

    h2 {
        font-size: 30px !important;
    }

    /* Card / subsection headings */
    h3 {
        font-size: 24px !important;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] label {
        font-size: 16px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# DATABASE
init_database()

# BRANDING
col1, col2 = st.columns([0.12, 0.88])

with col1:
    st.image(
        "dodocu_icon.png",
        width=110
    )

with col2:
    st.title("DoDocu")
    st.markdown(
        "### Making paper clutter as extinct as the Dodo."
    )
    st.caption("### Snap. Extract. Extinct.")

# SIDEBAR
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📷 Scan Document",
        "📊 Records & Analytics",
    ]
)

# HOME
if page == "🏠 Home":

    # INTRODUCTION
    st.header("What is DoDocu?")

    st.markdown(
        """
        **DoDocu** is an AI-powered document and receipt scanner
        that transforms paper-based information into structured,
        searchable and analysable digital records.

        Instead of manually reading, typing and organising information
        from receipts, invoices, tickets and other paper documents,
        DoDocu uses artificial intelligence to extract the information
        and prepare it for human review and digital storage.
        """
    )

    st.divider()

    # PROBLEM
    st.header("What problems does DoDocu solve?")

    problem_col1, problem_col2, problem_col3 = st.columns(3)

    with problem_col1:

        st.markdown("### 🗂️ Paper Clutter")

        st.write(
            "Important information can remain trapped in physical "
            "receipts, invoices, tickets and other paper documents."
        )

    with problem_col2:

        st.markdown("### 🔎 Difficult to Analyse")

        st.write(
            "Paper documents are difficult to search, organise, "
            "compare and analyse once they have accumulated."
        )
    with problem_col3:

        st.markdown("### ⌨️ Manual Data Entry")

        st.write(
            "Manually reading and entering document information "
            "takes time and can introduce data-entry errors."
        )

    st.divider()

    # WORKFLOW
    st.header("How does DoDocu work?")

    st.markdown(
        """
        DoDocu combines document scanning, AI extraction, human
        verification and structured database storage into one workflow.
        """
    )

    step1, step2, step3, step4, step5 = st.columns(5)

    with step1:

        st.markdown("### 📷 1. Prepare & Upload")

        st.write(
            "Upload image of a receipt, invoice, ticket or "
            "document. (Optional tool such as Notebloc can be "
            "used first to create a clearer image."
        )

    with step2:

        st.markdown("### 🤖 2. Extract")

        st.write(
            "The image is sent to the Google Gemini API, where "
            "the Gemini model analyses the document and extracts "
            "the available information."
        )

    with step3:

        st.markdown("### 🧾 3. Structure & Review")

        st.write(
            "The extracted information is displayed using the "
            "appropriate document template, such as a grocery "
            "receipt, restaurant receipt, transport ticket or invoice."
        )

    with step4:

        st.markdown("### 👤 4. Verify & Save")

        st.write(
            "The user reviews and corrects the AI-generated "
            "information before saving the final record."
        )

    with step5:

        st.markdown("### 📊 5. Analyse")

        st.write(
            "The verified record is stored in Neon PostgreSQL "
            "and becomes available for searching, viewing and analytics."
        )

    st.divider()

    # USERS
    st.header("Who can use DoDocu?")

    user_col1, user_col2, user_col3 = st.columns(3)

    with user_col1:

        st.markdown("### 👤 Individuals")

        st.write(
            "Keep personal receipts, tickets, invoices and "
            "other important documents organised digitally."
        )

    with user_col2:

        st.markdown("### 💼 Small Businesses")

        st.write(
            "Digitise business documents and reduce time spent on "
            "manual data entry and document organisation."
        )

    with user_col3:

        st.markdown("### 🧑‍💻 Freelancers & Self-Employed Professionals")

        st.write(
            "Capture financial documents and use the stored data "
            "to review spending by category, merchant and time."
        )

    st.divider()

    # CAPABILITIES
    st.header("What can DoDocu do?")

    capabilities_col1, capabilities_col2 = st.columns(2)

    with capabilities_col1:

        st.markdown(
            """
            - Upload document images
            - Extract information using Google Gemini
            - Classify documents into categories
            - Present category-specific information
            - Allow human review and correction
            """
        )

    with capabilities_col2:

        st.markdown(
            """
            - Store structured records in PostgreSQL
            - Store category-specific document details
            - Store individual receipt and invoice line items
            - Analyse spending by category and merchant
            - Analyse spending over time
            """
        )

    st.divider()

    # DOCUMENT TYPES
    st.header("What types of documents can DoDocu handle?")

    columns = st.columns(3)

    categories = list(DOCUMENT_TEMPLATES.items())

    for index, (category, template) in enumerate(categories):

        with columns[index % 3]:

            st.markdown(
                f"### {template['label']}"
            )

            st.write(
                template["description"]
            )

    st.divider()

    # TECHNOLOGY STACK
    st.header("What technologies power DoDocu?")

    tech_col1, tech_col2, tech_col3 = st.columns(3)

    with tech_col1:

        st.markdown("### 1. Python")

        st.write(
            "Core programming language used to build the "
            "application logic and data-processing workflow."
        )

    with tech_col2:

        st.markdown("### 2. Streamlit")

        st.write(
            "Framework used to build the interactive web "
            "application and user interface."
        )

    with tech_col3:

        st.markdown("### 3. Google Gemini API")

        st.write(
            "Provides AI-powered document understanding and "
            "information extraction using the Gemini 3.6 Flash model."
        )

    tech_col4, tech_col5, tech_col6 = st.columns(3)

    with tech_col4:

        st.markdown("### 4. Neon PostgreSQL")

        st.write(
            "Cloud PostgreSQL database used to persist the "
            "structured document records."
        )

    with tech_col5:

        st.markdown("### 5. SQLAlchemy")

        st.write(
            "ORM used to define the database models and "
            "manage communication with PostgreSQL."
        )

    with tech_col6:

        st.markdown("### 6. Pandas")

        st.write(
            "Used to transform stored records into data structures "
            "for filtering, reporting and analytics."
        )

    st.divider()

    # FUTURE WORK
    st.header("What could DoDocu do next?")

    st.markdown(
        """
        DoDocu can be extended beyond document storage and analytics.

        Possible extensions include:

        -  Advanced document search and filtering
        -  Improved document classification and extraction
        -  More advanced financial and document analytics
        -  Budget Planning and financial forecasting
        -  Email integration for processing documents received by email
        -  Calendar integration for events, bookings and appointments
        """
    )

    st.divider()

    # CONCLUSION
    st.header("What is DoDocu ultimately about?")

    st.markdown(
        """
        DoDocu demonstrates how **AI, application development and
        database technology** can be combined to turn unstructured
        paper-based information into structured digital data.

        **Snap. Extract. Extinct.**
        """
    )

# SCAN DOCUMENT
elif page == "📷 Scan Document":

    st.header("📷 Scan Document")

    uploaded_file = st.file_uploader(
        "Upload a receipt, invoice, ticket or document",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        col1, col2 = st.columns(2)

        # IMAGE
        with col1:

            st.subheader("Uploaded Document")

            st.image(
                image,
                use_container_width=True
            )

        # EXTRACTION
        with col2:

            st.subheader("AI Extraction")

            if st.button(
                "✨ Extract with DoDocu",
                type="primary"
            ):

                with st.spinner(
                    "Dodo is scanning your document..."
                ):

                    try:

                        image_bytes = io.BytesIO()

                        save_format = (
                            image.format
                            if image.format in ["JPEG", "PNG"]
                            else "JPEG"
                        )

                        if (
                            save_format == "JPEG"
                            and image.mode in ("RGBA", "P")
                        ):

                            image = image.convert("RGB")

                        image.save(
                            image_bytes,
                            format=save_format
                        )

                        mime_type = (
                            "image/jpeg"
                            if save_format == "JPEG"
                            else "image/png"
                        )

                        result = extract_document(
                            image_bytes.getvalue(),
                            mime_type
                        )

                        st.session_state["extracted"] = result

                        st.success(
                            "Delicious! Document digested!"
                        )

                    except Exception as e:

                        st.error(
                            f"Extraction failed: {e}"
                        )

    # REVIEW
    if "extracted" in st.session_state:

        data = st.session_state["extracted"]

        st.divider()

        st.header(
            "👤 Review Extracted Information"
        )

        st.info(
            "AI-generated information should be reviewed "
            "and corrected before saving."
        )

        # COMMON INFORMATION
        st.subheader("Document Information")

        col1, col2, col3 = st.columns(3)

        with col1:

            document_type = st.text_input(
                "Document Type",
                value=data.get(
                    "document_type"
                ) or ""
            )

            category = st.selectbox(
                "Category",
                options=list(DOCUMENT_TEMPLATES.keys()),
                format_func=lambda x:
                    DOCUMENT_TEMPLATES[x]["label"],
                index=(
                    list(DOCUMENT_TEMPLATES.keys())
                    .index(data.get("category"))
                    if data.get("category")
                    in DOCUMENT_TEMPLATES
                    else 0
                ),
            )

            merchant = st.text_input(
                "Merchant / Organisation",
                value=data.get(
                    "merchant"
                ) or ""
            )

        with col2:

            document_date = st.text_input(
                "Date",
                value=data.get(
                    "document_date"
                ) or ""
            )

            currency = st.text_input(
                "Currency",
                value=data.get(
                    "currency"
                ) or ""
            )

        with col3:

            subtotal = st.number_input(
                "Subtotal",
                value=float(
                    data.get("subtotal") or 0
                ),
                min_value=0.0,
            )

            tax = st.number_input(
                "Tax",
                value=float(
                    data.get("tax") or 0
                ),
                min_value=0.0,
            )

            total = st.number_input(
                "Total",
                value=float(
                    data.get("total") or 0
                ),
                min_value=0.0,
            )

        summary = st.text_area(
            "Summary",
            value=data.get(
                "summary"
            ) or ""
        )

        # CATEGORY-SPECIFIC INFORMATION
        st.subheader("Category-Specific Information")

        template = get_template(category)

        existing_details = data.get(
            "details",
            {}
        )

        details = {}

        detail_columns = st.columns(2)

        for index, field in enumerate(
            template["fields"]
        ):

            field_name, label, field_type = field

            with detail_columns[index % 2]:

                current_value = existing_details.get(
                    field_name
                )

                if field_type == "number":

                    details[field_name] = st.number_input(
                        label,
                        value=float(
                            current_value or 0
                        ),
                        min_value=0.0,
                        key=f"detail_{field_name}",
                    )

                else:

                    details[field_name] = st.text_input(
                        label,
                        value=str(
                            current_value or ""
                        ),
                        key=f"detail_{field_name}",
                    )

        # LINE ITEMS
        items = []

        if template["has_items"]:

            st.subheader("Line Items")

            existing_items = data.get(
                "items",
                []
            )

            if existing_items:

                edited_items = []

                for index, item in enumerate(
                    existing_items
                ):

                    st.markdown(
                        f"**Item {index + 1}**"
                    )

                    c1, c2, c3, c4 = st.columns(4)

                    with c1:

                        description = st.text_input(
                            "Description",
                            value=item.get(
                                "description"
                            ) or "",
                            key=f"item_desc_{index}",
                        )

                    with c2:

                        quantity = st.number_input(
                            "Quantity",
                            value=float(
                                item.get(
                                    "quantity"
                                ) or 1
                            ),
                            min_value=0.0,
                            key=f"item_qty_{index}",
                        )

                    with c3:

                        unit_price = st.number_input(
                            "Unit Price",
                            value=float(
                                item.get(
                                    "unit_price"
                                ) or 0
                            ),
                            min_value=0.0,
                            key=f"item_price_{index}",
                        )

                    with c4:

                        item_total = st.number_input(
                            "Total",
                            value=float(
                                item.get(
                                    "total"
                                ) or 0
                            ),
                            min_value=0.0,
                            key=f"item_total_{index}",
                        )

                    edited_items.append({
                        "description": description,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "total": item_total,
                    })

                items = edited_items

            else:

                st.info(
                    "No line items were detected."
                )

        # SAVE
        st.divider()

        if st.button(
            "💾 Save to DoDocu",
            type="primary"
        ):

            try:

                parsed_date = None

                if document_date:

                    parsed_date = date.fromisoformat(
                        document_date
                    )

                final_data = {
                    "document_type": document_type,
                    "category": category,
                    "merchant": merchant,
                    "document_date": parsed_date,
                    "currency": currency.upper(),
                    "subtotal": subtotal,
                    "tax": tax,
                    "total": total,
                    "summary": summary,
                    "details": details,
                    "items": items,
                }

                record_id = save_document(
                    final_data
                )

                st.success(
                    f"Document saved successfully! "
                    f"Record ID: {record_id}"
                )

                del st.session_state["extracted"]

            except ValueError:

                st.error(
                    "Please enter the date using "
                    "YYYY-MM-DD format."
                )

            except Exception as e:

                st.error(
                    f"Could not save record: {e}"
                )

# RECORDS & ANALYTICS
elif page == "📊 Records & Analytics":

    st.header("📊 Records & Analytics")

    documents = get_documents()

    if not documents:

        st.info(
            "No documents have been saved yet."
        )

    else:

        data = documents_to_dataframe(
            documents
        )

        metrics = calculate_metrics(
            data
        )

        # FILTERS
        st.subheader("Filters")

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:

            categories = sorted(
                data["Category"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_categories = st.multiselect(
                "Category",
                categories,
            )

        with filter_col2:

            currencies = sorted(
                data["Currency"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_currencies = st.multiselect(
                "Currency",
                currencies,
            )

        filtered_data = data.copy()

        if selected_categories:

            filtered_data = filtered_data[
                filtered_data["Category"].isin(
                    selected_categories
                )
            ]

        if selected_currencies:

            filtered_data = filtered_data[
                filtered_data["Currency"].isin(
                    selected_currencies
                )
            ]

        # METRICS
        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Documents",
                len(filtered_data)
            )

        with col2:

            st.metric(
                "Average Document",
                (
                    f"{filtered_data['Total'].mean():,.2f}"
                    if not filtered_data.empty
                    else "0.00"
                )
            )

        # RECORDS
        st.divider()

        st.subheader("Saved Records")

        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True,
        )

        # ANALYTICS
        if not filtered_data.empty:

            st.divider()

            st.subheader(
                "📊 Spending by Category"
            )

            category_data = spending_by_category(
                filtered_data
            )

            if not category_data.empty:

                for currency in category_data[
                    "Currency"
                ].dropna().unique():

                    currency_data = (
                        category_data[
                            category_data["Currency"]
                            == currency
                        ]
                        .set_index("Category")["Total"]
                    )

                    st.markdown(
                        f"**{currency}**"
                    )

                    st.bar_chart(
                        currency_data
                    )

            st.subheader(
                "🏪 Spending by Merchant"
            )

            merchant_data = spending_by_merchant(
                filtered_data
            )

            if not merchant_data.empty:

                for currency in merchant_data[
                    "Currency"
                ].dropna().unique():

                    currency_data = (
                        merchant_data[
                            merchant_data["Currency"]
                            == currency
                        ]
                        .set_index("Merchant")["Total"]
                    )

                    st.markdown(
                        f"**{currency}**"
                    )

                    st.bar_chart(
                        currency_data
                    )

            st.subheader(
                "📅 Spending Over Time"
            )

            time_data = spending_over_time(
                filtered_data
            )

            if not time_data.empty:

                for currency in time_data[
                    "Currency"
                ].dropna().unique():

                    currency_data = (
                        time_data[
                            time_data["Currency"]
                            == currency
                        ]
                        .set_index("Month")["Total"]
                    )

                    st.markdown(
                        f"**{currency}**"
                    )

                    st.line_chart(
                        currency_data
                    )