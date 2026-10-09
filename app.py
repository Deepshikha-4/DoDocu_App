# app.py

import io

from datetime import (
    date,
    datetime,
    timedelta,
)

import pandas as pd
import streamlit as st
from PIL import Image
import plotly.express as px

from database import (
    init_database,
    save_document,
    get_documents,
    get_filter_options,
    get_document,
    DuplicateDocumentError,
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
    spending_by_category_over_time,
    spending_by_document,
)
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DoDocu",
    page_icon="dodocu_test_icon.png",
    layout="wide",
)

# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>
    .stMarkdown p,
    .stMarkdown li {
        font-size: 17px !important;
        line-height: 1.65 !important;
    }

    h1 {
        font-size: 34px !important;
    }

    h2 {
        font-size: 28px !important;
    }

    h3 {
        font-size: 21px !important;
    }

    [data-testid="stSidebar"] label {
        font-size: 16px !important;
    }

    /* Home page hero */
    .home-hero {
        background: linear-gradient(125deg, #102b3f 0%, #174b59 65%, #23736d 100%);
        padding: 38px 38px 34px 38px;
        border-radius: 18px;
        color: #ffffff;
        margin: 18px 0 28px 0;
    }

    .home-eyebrow {
        color: #a8e5d8;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .home-hero h1 {
        color: #ffffff !important;
        font-size: 39px !important;
        line-height: 1.2 !important;
        margin: 0 0 16px 0;
        font-weight: 700;
    }

    .home-hero p {
        color: #e2edf0;
        font-size: 17px;
        line-height: 1.7;
        max-width: 760px;
        margin: 0;
    }

    .home-hero .hero-tagline {
        color: #a8e5d8;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin-top: 22px;
    }

    /* Section headings */
    .home-section-label {
        color: #398a80;
        text-transform: uppercase;
        letter-spacing: 1.7px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .home-section-title {
        color: #183448;
        font-size: 27px;
        line-height: 1.3;
        font-weight: 700;
        margin: 0 0 10px 0;
    }

    .home-section-intro {
        color: #647783;
        font-size: 16px;
        line-height: 1.7;
        margin-bottom: 20px;
    }

    /* Content cards */
    .home-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 145, 155, 0.24);
        border-radius: 13px;
        padding: 22px 20px;
        min-height: 155px;
        height: 100%;
    }

    .home-card .card-number {
        color: #398a80;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin-bottom: 12px;
    }

    .home-card h3 {
        color: var(--text-color);
        font-size: 18px !important;
        margin: 0 0 9px 0;
        font-weight: 700;
    }

    .home-card p {
        color: var(--text-color);
        opacity: 0.82;
        font-size: 14px !important;
        line-height: 1.65 !important;
        margin: 0;
    }

    /* Workflow cards */
    .workflow-card {
        border-top: 3px solid #398a80;
        background: var(--secondary-background-color);
        border-radius: 0 0 12px 12px;
        padding: 19px 15px;
        min-height: 180px;
        height: 100%;
    }

    .workflow-card .step {
        color: #398a80;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }

    .workflow-card h3 {
        color: var(--text-color);
        font-size: 17px !important;
        margin: 0 0 8px 0;
    }

    .workflow-card p {
        color: var(--text-color);
        opacity: 0.82;
        font-size: 13px !important;
        line-height: 1.6 !important;
        margin: 0;
    }

    /* Technology and closing panels */
    .tech-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 145, 155, 0.24);
        border-radius: 11px;
        padding: 17px;
        min-height: 120px;
        height: 100%;
    }

    .tech-card h3 {
        font-size: 16px !important;
        margin: 0 0 7px 0;
        color: var(--text-color);
    }

    .tech-card p {
        font-size: 13px !important;
        line-height: 1.6 !important;
        color: var(--text-color);
        opacity: 0.82;
        margin: 0;
    }

    .home-closing {
        background: rgba(57, 138, 128, 0.10);
        border: 1px solid rgba(57, 138, 128, 0.28);
        border-radius: 15px;
        padding: 27px;
        margin: 12px 0 20px 0;
    }

    .home-closing h3 {
        color: var(--text-color);
        margin-top: 0;
    }

    .home-closing p {
        color: var(--text-color);
        font-size: 16px !important;
    }

    @media (max-width: 768px) {
        .home-hero {
            padding: 25px 22px;
        }

        .home-hero h1 {
            font-size: 30px !important;
        }

        .home-section-title {
            font-size: 23px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================
init_database()
# ============================================================
# BRANDING
# ============================================================

st.image(
    "dodocu_ppt_banner.png",
    width=500,
)

st.markdown(
    "### Making paper clutter as extinct as the Dodo."
)

st.caption(
    "### Snap. Extract. Extinct."
)

# ============================================================
# SIDEBAR
# ============================================================
if st.session_state.pop("navigate_to_scan", False):
    st.session_state["main_navigation"] = "📷 Scan Document"

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📷 Scan Document",
        "📊 Records & Analytics",
    ],
    key="main_navigation",
)

# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    # Hero section
    st.markdown(
        """
        <div class="home-hero">
            <div class="home-eyebrow">AI-powered document intelligence</div>
            <h1>From paper documents<br>to organised digital records.</h1>
            <p>
                DoDocu transforms receipts, invoices, travel tickets and other
                document images into structured digital records. AI extracts
                relevant information, you review and correct the results, and
                the verified records can be retrieved, filtered and analysed.
            </p>
            <div class="hero-tagline">SNAP. EXTRACT. EXTINCT.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Product overview
    st.markdown(
        """
        <div class="home-section-label">The product</div>
        <div class="home-section-title">Less paperwork. More useful information.</div>
        <div class="home-section-intro">
            Important information is often trapped in paper receipts, invoices,
            tickets and image files. DoDocu helps turn those documents into
            organised records, making it easier to retrieve details, review
            transactions and understand recorded spending.
        </div>
        """,
        unsafe_allow_html=True,
    )

    benefit_col1, benefit_col2, benefit_col3 = st.columns(3)

    with benefit_col1:
        st.markdown(
            """
            <div class="home-card">
                <div class="card-number">01 / CAPTURE</div>
                <h3>Bring documents together</h3>
                <p>
                    Upload JPG or PNG images of receipts, invoices, tickets
                    and other supported documents into one application.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with benefit_col2:
        st.markdown(
            """
            <div class="home-card">
                <div class="card-number">02 / UNDERSTAND</div>
                <h3>Extract and organise information</h3>
                <p>
                    Use Gemini AI to identify available dates, merchants,
                    currency, amounts, summaries and other document-specific
                    details, including line items where supported.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with benefit_col3:
        st.markdown(
            """
            <div class="home-card">
                <div class="card-number">03 / REVIEW AND USE</div>
                <h3>Keep useful, reviewable records</h3>
                <p>
                    Correct extracted information before saving it, then
                    filter saved records and explore recorded spending
                    through summaries and interactive charts.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Application workflow
    st.markdown(
        """
        <div class="home-section-label">Application workflow</div>
        <div class="home-section-title">From document image to actionable information</div>
        <div class="home-section-intro">
            DoDocu combines AI extraction with human review, relational data
            storage and analytics. Each stage transforms the information so
            it can be checked, stored and used later.
        </div>
        """,
        unsafe_allow_html=True,
    )

    workflow = [
        (
            "STEP 01",
            "Upload",
            "Select a JPG or PNG image of a receipt, invoice, ticket or other supported document.",
        ),
        (
            "STEP 02",
            "Interpret",
            "The Google Gemini API processes the image and identifies available text and document information.",
        ),
        (
            "STEP 03",
            "Extract and classify",
            "DoDocu organises the returned information into common fields, a document type, a category and relevant template fields.",
        ),
        (
            "STEP 04",
            "Review and correct",
            "Inspect the extracted values and edit incorrect or missing information before saving.",
        ),
        (
            "STEP 05",
            "Store",
            "Save the reviewed record and its supported category details and line items in the PostgreSQL database.",
        ),
        (
            "STEP 06",
            "Retrieve and analyse",
            "Filter saved records and explore totals and spending patterns by category, merchant and month.",
        ),
    ]

    workflow_columns = st.columns(3)

    for index, (step, title, description) in enumerate(workflow):
        with workflow_columns[index % 3]:
            st.markdown(
                f"""
                <div class="workflow-card">
                    <div class="step">{step}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")

    st.info(
        "AI extraction may be incomplete or inaccurate. Reviewing and "
        "correcting the extracted information before saving is an important "
        "part of the DoDocu workflow."
    )

    st.write("")

    # Technology stack
    st.markdown(
        """
        <div class="home-section-label">Under the hood</div>
        <div class="home-section-title">The technology behind DoDocu</div>
        <div class="home-section-intro">
            Python connects the user interface, AI extraction, database
            operations and analytics. Each technology has a distinct role
            in the application's workflow.
        </div>
        """,
        unsafe_allow_html=True,
    )

    technologies = [
        (
            "Python",
            "Application logic, validation, data processing and integration between the application's components.",
        ),
        (
            "Streamlit",
            "Interactive web interface for document uploads, information review, record management and analytics.",
        ),
        (
            "Custom CSS",
            "Global styling for typography, headings, spacing, cards and the visual presentation of the interface.",
        ),
        (
            "Google Gemini API — Gemini 3.6 Flash",
            "Interprets uploaded document images and extracts relevant information, such as dates, merchants, amounts and other document-specific details.",
        ),
        (
            "Neon PostgreSQL",
            "Cloud-hosted relational database that persistently stores document records and their associated structured information.",
        ),
        (
            "SQLAlchemy",
            "Object-relational mapping (ORM) and database-access layer used to define models and interact with PostgreSQL.",
        ),
        (
            "Pandas",
            "Transforms retrieved records into DataFrames for filtering, aggregation and analytical calculations.",
        ),
        (
            "Plotly",
            "Creates interactive visualisations, including monthly spending trends, category breakdowns and merchant comparisons.",
        ),
    ]

    tech_columns = st.columns(3)

    for index, (name, description) in enumerate(technologies):
        with tech_columns[index % 3]:
            st.markdown(
                f"""
                <div class="tech-card">
                    <h3>{name}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")

    st.write("")

    # Structured information
    st.markdown(
        """
        <div class="home-section-label">Structured information</div>
        <div class="home-section-title">More than a digital scan</div>
        <div class="home-section-intro">
            DoDocu aims to turn document images into information that can be
            reviewed and queried. The fields available depend on what the
            document contains and what the AI can identify.
        </div>
        """,
        unsafe_allow_html=True,
    )

    information_col1, information_col2, information_col3 = st.columns(3)

    with information_col1:
        st.markdown(
            """
            <div class="home-card">
                <h3>Common fields</h3>
                <p>
                    Document type, category, merchant or organisation,
                    date, time, currency, subtotal, tax, total and summary,
                    where available.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with information_col2:
        st.markdown(
            """
            <div class="home-card">
                <h3>Category-specific details</h3>
                <p>
                    Template-based fields help capture information relevant
                    to different categories of documents, rather than
                    treating every document as identical.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with information_col3:
        st.markdown(
            """
            <div class="home-card">
                <h3>Line items</h3>
                <p>
                    For supported document templates, individual items can
                    include a description, quantity, unit price and line total.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Supported document categories
    st.markdown(
        """
        <div class="home-section-label">Document coverage</div>
        <div class="home-section-title">Designed for everyday documents</div>
        <div class="home-section-intro">
            Document type describes what a document is, while category
            describes the area it relates to. DoDocu uses templates to
            organise relevant fields for the selected category.
        </div>
        """,
        unsafe_allow_html=True,
    )

    categories = list(DOCUMENT_TEMPLATES.items())
    category_columns = st.columns(3)

    for index, (category, template) in enumerate(categories):
        with category_columns[index % 3]:
            st.markdown(
                f"""
                <div class="home-card">
                    <h3>{template['label']}</h3>
                    <p>{template['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")

    st.caption(
        "The available categories and fields depend on the document templates "
        "configured in DoDocu."
    )

    # Intended users
    st.markdown(
        """
        <div class="home-section-label">Who it is for</div>
        <div class="home-section-title">Useful wherever documents accumulate</div>
        """,
        unsafe_allow_html=True,
    )

    audience_col1, audience_col2, audience_col3 = st.columns(3)

    with audience_col1:
        st.markdown(
            """
            <div class="home-card">
                <h3>Individuals and households</h3>
                <p>
                    Keep everyday purchase records, household expenses,
                    travel documents and important receipts organised.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with audience_col2:
        st.markdown(
            """
            <div class="home-card">
                <h3>Small businesses</h3>
                <p>
                    Keep transaction documents together and make routine
                    financial information easier to retrieve and review.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with audience_col3:
        st.markdown(
            """
            <div class="home-card">
                <h3>Freelancers and independent professionals</h3>
                <p>
                    Organise business-related documents and review recorded
                    expenses by available category, merchant and date filters.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Future direction
    st.markdown(
        """
        <div class="home-section-label">Looking ahead</div>
        <div class="home-section-title">A foundation for smarter document management</div>
        <div class="home-section-intro">
            The current application establishes a workflow for capturing,
            reviewing, storing and analysing document information.
            These are potential extensions, not claims about current features.
        </div>
        """,
        unsafe_allow_html=True,
    )

    future_col1, future_col2 = st.columns(2)

    with future_col1:
        st.markdown(
            """
            <div class="home-card">
                <h3>Enhanced search and insights</h3>
                <p>
                    More advanced retrieval, improved extraction quality,
                    budget tracking, richer financial summaries and
                    forecasting.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with future_col2:
        st.markdown(
            """
            <div class="home-card">
                <h3>Connected document workflows</h3>
                <p>
                    Potential email integration to identify tickets and
                    payment confirmations, with calendar integration for
                    relevant events and bookings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Closing statement
    st.markdown(
        """
        <div class="home-closing">
            <h3>Paper in. Useful data out.</h3>
            <p>
                DoDocu demonstrates how AI, application development and
                relational database technology can turn everyday document
                images into structured, reviewable and analysable information.
                AI assists with extraction; users remain in control of
                reviewing the results before saving.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Start scanning a document",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["navigate_to_scan"] = True
        st.rerun()

    if st.session_state.pop("home_navigation", False):
        st.info(
            "Select **📷 Scan Document** from the sidebar to begin."
        )

        

# ============================================================
# SCAN DOCUMENT
# ============================================================

elif page == "📷 Scan Document":

    st.header(
        "📷 Scan Document"
    )

    uploaded_file = st.file_uploader(
        "Upload a receipt, invoice, ticket or document",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
    )

    if uploaded_file:

        image = Image.open(
            uploaded_file
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "Uploaded Document"
            )

            st.image(
                image,
                use_container_width=True,
            )

        with col2:

            st.subheader(
                "AI Extraction"
            )

            if st.button(
                "✨ Extract with DoDocu",
                type="primary",
            ):

                with st.spinner(
                    "Dodo is scanning your document..."
                ):

                    try:

                        image_bytes = io.BytesIO()

                        save_format = (
                            image.format
                            if image.format
                            in [
                                "JPEG",
                                "PNG",
                            ]
                            else "JPEG"
                        )

                        if (
                            save_format == "JPEG"
                            and image.mode
                            in (
                                "RGBA",
                                "P",
                            )
                        ):

                            image = image.convert(
                                "RGB"
                            )

                        image.save(
                            image_bytes,
                            format=save_format,
                        )

                        mime_type = (
                            "image/jpeg"
                            if save_format == "JPEG"
                            else "image/png"
                        )

                        result = extract_document(
                            image_bytes.getvalue(),
                            mime_type,
                        )

                        st.session_state[
                            "extracted"
                        ] = result

                        st.success(
                            "Delicious! Document digested!"
                        )

                    except Exception as e:

                        st.error(
                            f"Extraction failed: {e}"
                        )

    # ========================================================
    # REVIEW
    # ========================================================

    if "extracted" in st.session_state:

        data = st.session_state[
            "extracted"
        ]

        st.divider()

        st.header(
            "👤 Review Extracted Information"
        )

        st.info(
            "AI-generated information should be reviewed "
            "and corrected before saving."
        )

        # ====================================================
        # COMMON INFORMATION
        # ====================================================

        st.subheader(
            "Document Information"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            document_type = st.text_input(
                "Document Type",
                value=data.get(
                    "document_type"
                )
                or "",
            )

            category = st.selectbox(
                "Category",
                options=list(
                    DOCUMENT_TEMPLATES.keys()
                ),
                format_func=lambda x:
                    DOCUMENT_TEMPLATES[x]["label"],
                index=(
                    list(
                        DOCUMENT_TEMPLATES.keys()
                    ).index(
                        data.get("category")
                    )
                    if data.get("category")
                    in DOCUMENT_TEMPLATES
                    else 0
                ),
            )

            merchant = st.text_input(
                "Merchant / Organisation",
                value=data.get(
                    "merchant"
                )
                or "",
            )

        with col2:

            document_date = st.text_input(
                "Date",
                value=data.get(
                    "document_date"
                )
                or "",
                placeholder="YYYY-MM-DD",
            )

            document_time = st.text_input(
                "Time",
                value=data.get(
                    "document_time"
                )
                or "",
                placeholder="HH:MM",
                help=(
                    "Enter the transaction or document time "
                    "in 24-hour format. This is used for "
                    "exact duplicate detection."
                ),
            )

            currency = st.text_input(
                "Currency",
                value=data.get(
                    "currency"
                )
                or "",
                max_chars=10,
            )

        with col3:

            subtotal = st.number_input(
                "Subtotal",
                value=float(
                    data.get("subtotal")
                    or 0
                ),
                min_value=0.0,
            )

            tax = st.number_input(
                "Tax",
                value=float(
                    data.get("tax")
                    or 0
                ),
                min_value=0.0,
            )

            total = st.number_input(
                "Total",
                value=float(
                    data.get("total")
                    or 0
                ),
                min_value=0.0,
            )

        summary = st.text_area(
            "Summary",
            value=data.get(
                "summary"
            )
            or "",
        )

        # ====================================================
        # CATEGORY-SPECIFIC INFORMATION
        # ====================================================

        st.subheader(
            "Category-Specific Information"
        )

        template = get_template(
            category
        )

        existing_details = data.get(
            "details",
            {},
        )

        details = {}

        detail_columns = st.columns(2)

        for index, field in enumerate(
            template["fields"]
        ):

            (
                field_name,
                label,
                field_type,
            ) = field

            with detail_columns[
                index % 2
            ]:

                current_value = (
                    existing_details.get(
                        field_name
                    )
                )

                if field_type == "number":

                    details[
                        field_name
                    ] = st.number_input(
                        label,
                        value=float(
                            current_value
                            or 0
                        ),
                        min_value=0.0,
                        key=(
                            f"detail_{field_name}"
                        ),
                    )

                else:

                    details[
                        field_name
                    ] = st.text_input(
                        label,
                        value=str(
                            current_value
                            or ""
                        ),
                        key=(
                            f"detail_{field_name}"
                        ),
                    )

        # ====================================================
        # LINE ITEMS
        # ====================================================

        items = []

        if template["has_items"]:

            st.subheader(
                "Line Items"
            )

            existing_items = data.get(
                "items",
                [],
            )

            if existing_items:

                edited_items = []

                for index, item in enumerate(
                    existing_items
                ):

                    st.markdown(
                        f"**Item {index + 1}**"
                    )

                    c1, c2, c3, c4 = st.columns(
                        4
                    )

                    with c1:

                        description = st.text_input(
                            "Description",
                            value=item.get(
                                "description"
                            )
                            or "",
                            key=(
                                f"item_desc_{index}"
                            ),
                        )

                    with c2:

                        quantity = st.number_input(
                            "Quantity",
                            value=float(
                                item.get(
                                    "quantity"
                                )
                                or 1
                            ),
                            min_value=0.0,
                            key=(
                                f"item_qty_{index}"
                            ),
                        )

                    with c3:

                        unit_price = st.number_input(
                            "Unit Price",
                            value=float(
                                item.get(
                                    "unit_price"
                                )
                                or 0
                            ),
                            min_value=0.0,
                            key=(
                                f"item_price_{index}"
                            ),
                        )

                    with c4:

                        item_total = st.number_input(
                            "Total",
                            value=float(
                                item.get(
                                    "total"
                                )
                                or 0
                            ),
                            min_value=0.0,
                            key=(
                                f"item_total_{index}"
                            ),
                        )

                    edited_items.append(
                        {
                            "description": description,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "total": item_total,
                        }
                    )

                items = edited_items

            else:

                st.info(
                    "No line items were detected."
                )

        # ====================================================
        # SAVE
        # ====================================================

        st.divider()

        if st.button(
            "💾 Save to DoDocu",
            type="primary",
        ):

            try:

                # ------------------------------------------------
                # DATE
                # ------------------------------------------------

                parsed_date = None

                if document_date.strip():

                    parsed_date = date.fromisoformat(
                        document_date.strip()
                    )

                # ------------------------------------------------
                # TIME
                # ------------------------------------------------

                parsed_time = None

                if document_time.strip():

                    time_value = (
                        document_time.strip()
                    )

                    try:

                        parsed_time = (
                            datetime.strptime(
                                time_value,
                                "%H:%M",
                            ).time()
                        )

                    except ValueError:

                        parsed_time = (
                            datetime.strptime(
                                time_value,
                                "%H:%M:%S",
                            ).time()
                        )

                # ------------------------------------------------
                # FINAL DATA
                # ------------------------------------------------

                final_data = {
                    "document_type": document_type.strip(),
                    "category": category,
                    "merchant": merchant.strip(),
                    "document_date": parsed_date,
                    "document_time": parsed_time,
                    "currency": currency.strip().upper(),
                    "subtotal": subtotal,
                    "tax": tax,
                    "total": total,
                    "summary": summary.strip(),
                    "details": details,
                    "items": items,
                }

                # ------------------------------------------------
                # SAVE
                # ------------------------------------------------

                record_id = save_document(
                    final_data
                )

                st.success(
                    f"Document saved successfully! "
                    f"Record ID: {record_id}"
                )

                del st.session_state[
                    "extracted"
                ]

                st.rerun()

            except DuplicateDocumentError as exc:

                st.warning(
                    "⚠️ Duplicate document detected."
                )

                st.info(
                    f"A matching document already exists "
                    f"as Record #{exc.existing_document_id}. "
                    f"The new document was not saved."
                )

            except ValueError:

                st.error(
                    "Please enter the date using "
                    "YYYY-MM-DD and the time using "
                    "HH:MM or HH:MM:SS."
                )

            except Exception as e:

                st.error(
                    f"Could not save record: {e}"
                )


# ============================================================
# RECORDS & ANALYTICS
# ============================================================

elif page == "📊 Records & Analytics":

    st.header(
        "📊 Records & Analytics"
    )

    st.caption(
        "Filter your saved documents and analyse "
        "your spending patterns."
    )

    # ========================================================
    # FILTER OPTIONS
    # ========================================================

    filter_options = get_filter_options()

    category_options = {
        category["name"]: category["code"]
        for category in filter_options[
            "categories"
        ]
    }

    # ========================================================
    # FILTER FORM
    # ========================================================

    st.subheader(
        "🔎 Filter Records"
    )

    st.caption(
        "* Recommended filter. All filters are optional; "
        "you can apply only the filters you need."
    )

    with st.form(
        "records_filter_form"
    ):

        filter_col1, filter_col2, filter_col3 = (
            st.columns(3)
        )

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        with filter_col1:

            selected_category_names = (
                st.multiselect(
                    "Category *",
                    options=list(
                        category_options.keys()
                    ),
                    key="filter_categories",
                )
            )

        # ----------------------------------------------------
        # CURRENCY
        # ----------------------------------------------------

        with filter_col2:

            selected_currencies = (
                st.multiselect(
                    "Currency *",
                    options=filter_options[
                        "currencies"
                    ],
                    key="filter_currencies",
                )
            )

        # ----------------------------------------------------
        # MONTH
        # ----------------------------------------------------

        with filter_col3:

            selected_months = (
                st.multiselect(
                    "Month",
                    options=filter_options[
                        "months"
                    ],
                    key="filter_months",
                )
            )

        filter_col4, filter_col5 = (
            st.columns(2)
        )

        # ----------------------------------------------------
        # MERCHANT
        # ----------------------------------------------------

        with filter_col4:

            selected_merchants = (
                st.multiselect(
                    "Merchant",
                    options=filter_options[
                        "merchants"
                    ],
                    key="filter_merchants",
                )
            )

        # ----------------------------------------------------
        # DOCUMENT TYPE
        # ----------------------------------------------------

        with filter_col5:

            selected_document_types = (
                st.multiselect(
                    "Document Type",
                    options=filter_options[
                        "document_types"
                    ],
                    key="filter_document_types",
                )
            )

        # ----------------------------------------------------
        # DATE RANGE
        # ----------------------------------------------------

        st.markdown(
            "#### Date Range *"
        )

        date_filter = st.selectbox(
            "Select Date Range",
            [
                "All Time",
                "This Month",
                "Last Month",
                "This Year",
                "Custom Range",
            ],
            key="filter_date_range",
        )

        start_date = None
        end_date = None

        today = date.today()

        if date_filter == "This Month":

            start_date = today.replace(
                day=1
            )

            end_date = today

        elif date_filter == "Last Month":

            first_this_month = (
                today.replace(
                    day=1
                )
            )

            end_date = (
                first_this_month
                - timedelta(
                    days=1
                )
            )

            start_date = (
                end_date.replace(
                    day=1
                )
            )

        elif date_filter == "This Year":

            start_date = date(
                today.year,
                1,
                1,
            )

            end_date = today

        elif date_filter == "Custom Range":

            custom_col1, custom_col2 = (
                st.columns(2)
            )

            with custom_col1:

                start_date = st.date_input(
                    "Start Date",
                    value=date(
                        today.year,
                        1,
                        1,
                    ),
                    key="filter_start_date",
                )

            with custom_col2:

                end_date = st.date_input(
                    "End Date",
                    value=today,
                    key="filter_end_date",
                )

        # ----------------------------------------------------
        # APPLY
        # ----------------------------------------------------

        apply_filters = st.form_submit_button(
            "🔎 Apply Filters",
            type="primary",
            use_container_width=True,
        )

    # ========================================================
    # APPLY FILTERS ONLY AFTER BUTTON
    # ========================================================

    if apply_filters:

        if (
            start_date
            and end_date
            and start_date > end_date
        ):

            st.error(
                "Start Date cannot be after End Date."
            )

            st.stop()

        selected_categories = [
            category_options[name]
            for name in selected_category_names
        ]

        # ----------------------------------------------------
        # DATABASE QUERY
        # ----------------------------------------------------

        documents = get_documents(
            categories=(
                selected_categories
                or None
            ),

            months=(
                selected_months
                or None
            ),

            currencies=(
                selected_currencies
                or None
            ),

            merchants=(
                selected_merchants
                or None
            ),

            document_types=(
                selected_document_types
                or None
            ),

            start_date=start_date,

            end_date=end_date,
        )

        filtered_data = (
            documents_to_dataframe(
                documents
            )
        )

        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        st.session_state[
            "filtered_documents"
        ] = documents

        st.session_state[
            "filtered_data"
        ] = filtered_data

        st.session_state[
            "filters_applied"
        ] = True

    # ========================================================
    # WAIT UNTIL USER APPLIES FILTERS
    # ========================================================

    if not st.session_state.get(
        "filters_applied",
        False,
    ):

        st.info(
            "Select all or some filters above, then click "
            "**Apply Filters** to view the results."
        )

        st.stop()

    # ========================================================
    # CURRENT FILTER RESULTS
    # ========================================================

    data = st.session_state.get(
        "filtered_data",
        pd.DataFrame(),
    )

    documents = st.session_state.get(
        "filtered_documents",
        [],
    )
    
    # Keep records in ascending ID order.
    if not data.empty and "ID" in data.columns:
        data = data.sort_values(
            by="ID",
            ascending=True,
            kind="stable",
        ).reset_index(drop=True)

    # Keep the database document objects in the same ID order.
    documents = sorted(
        documents,
        key=lambda document: document.id,
    )

    # ========================================================
    # FILTER OUTPUT
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Filter Results"
    )

    if data.empty:

        st.warning(
            "No documents match the selected filters."
        )

        st.stop()

    st.success(
        f"{len(data):,} document(s) found."
    )

    # ========================================================
    # RECORD TABLE
    # ========================================================

    st.subheader(
        "📄 Records"
    )

    display_columns = [
        "ID",
        "Date",
        "Time",
        "Merchant",
        "Category",
        "Currency",
        "Subtotal",
        "Tax",
        "Total",
        "Type",
    ]

    display_data = data[
        [
            column
            for column in display_columns
            if column in data.columns
        ]
    ].copy()

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # METRICS
    # ========================================================

    st.divider()
    st.subheader("Overview")

    metrics = calculate_metrics(data)

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            "Documents recorded",
            f"{metrics['documents']:,}",
            help="Number of saved documents matching the filters.",
        )

    with metric_col2:
        currencies = list(metrics["total_by_currency"].keys())

        if len(currencies) == 1:
            currency = currencies[0]
            total = metrics["total_by_currency"][currency]

            st.metric(
                f"Total recorded spending ({currency})",
                f"{total:,.2f}",
            )
        else:
            st.metric(
                "Currencies represented",
                len(currencies),
                help="Totals remain separate for each currency.",
            )

    metric_col3, metric_col4 = st.columns(2)

    with metric_col3:
        if len(currencies) == 1:
            currency = currencies[0]
            average = metrics["average_by_currency"][currency]

            st.metric(
                f"Average document value ({currency})",
                f"{average:,.2f}",
            )
        else:
            st.write("**Total by currency**")

            for currency, total in metrics["total_by_currency"].items():
                st.write(f"{currency}: {total:,.2f}")

    with metric_col4:
        if len(currencies) == 1:
            currency = currencies[0]
            category = metrics["top_category_by_currency"].get(currency)

            st.metric(
                "Highest-spending category",
                category or "N/A",
                help="Category with the highest recorded total in this currency.",
            )
        else:
            st.metric(
                "Most frequently recorded category",
                metrics["top_category"] or "N/A",
                help="Based on document count, not a comparison of different currencies.",
            )


    # ========================================================
    # MONTHLY SPENDING
    # ========================================================

    st.divider()
    st.subheader("Monthly Spending")

    st.caption(
        "View the number of receipts and total amount spent "
        "each month. Hover over a point to see both values."
    )

    time_data = spending_over_time(data)

    if not time_data.empty:

        currencies_in_chart = sorted(
            time_data["Currency"].dropna().unique()
        )

        for currency in currencies_in_chart:

            currency_data = (
                time_data[
                    time_data["Currency"] == currency
                ]
                .sort_values("Month")
                .copy()
            )

            fig = px.line(
                currency_data,
                x="Month",
                y="Total",
                markers=True,
                custom_data=["Documents"],
                title=f"Monthly Spending — {currency}",
                labels={
                    "Month": "Month",
                    "Total": f"Total Spent ({currency})",
                },
            )

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=8),
                hovertemplate=(
                    "<b>%{x|%B %Y}</b><br>"
                    f"Total spent: {currency} %{{y:,.2f}}<br>"
                    "Number of receipts: %{customdata[0]:,.0f}"
                    "<extra></extra>"
                ),
            )

            fig.update_layout(
                height=420,
                hovermode="closest",
                margin=dict(l=20, r=20, t=65, b=20),
                xaxis=dict(
                    title="Month",
                    tickformat="%b %Y",
                    dtick="M1",
                    tickangle=-35,
                ),
                yaxis=dict(
                    title=f"Total spent ({currency})",
                    tickformat=",.2f",
                    separatethousands=True,
                    rangemode="tozero",
                ),
                showlegend=False,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"monthly_spending_{currency}",
            )

    else:
        st.info(
            "No dated documents are available for the selected filters. "
            "Add valid document dates to see monthly spending."
        )



    # ========================================================
    # CATEGORY DONUT AND MERCHANT BAR
    # ========================================================

    chart_col1, chart_col2 = st.columns(2)

    # --------------------------------------------------------
    # SPENDING BY CATEGORY — DONUT CHART
    # --------------------------------------------------------

    with chart_col1:

        st.subheader("🍩 Spending by Category")

        category_data = spending_by_category(data)

        if category_data.empty:
            st.info("No category spending data is available.")
        else:
            currencies_in_chart = sorted(
                category_data["Currency"]
                .dropna()
                .unique()
            )

            for currency in currencies_in_chart:

                currency_data = category_data.loc[
                    category_data["Currency"] == currency
                ].copy()

                # A donut chart is not meaningful when every
                # category has zero recorded spending.
                currency_data = currency_data.loc[
                    currency_data["Total"] > 0
                ]

                if currency_data.empty:
                    st.info(
                        f"No positive spending totals are available "
                        f"for {currency}."
                    )
                    continue

                fig = px.pie(
                    currency_data,
                    names="Category",
                    values="Total",
                    color="Category",
                    hole=0.55,
                    title=f"{currency} Spending by Category",
                    hover_data=["Documents", "Percentage"],
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )

                fig.update_traces(
                    textposition="inside",
                    textinfo="label+percent",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        f"Total: {currency} %{{value:,.2f}}<br>"
                        "Share: %{percent}<br>"
                        "<extra></extra>"
                    ),
                )

                fig.update_layout(
                    height=450,
                    margin=dict(l=15, r=15, t=65, b=15),
                    showlegend=True,
                    legend_title_text="Category",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"category_donut_{currency}",
                )

    # --------------------------------------------------------
    # SPENDING BY MERCHANT — HORIZONTAL BAR CHART
    # --------------------------------------------------------

    with chart_col2:

        st.subheader("🏪 Spending by Merchant")

        merchant_data = spending_by_merchant(data, top_n=10)

        if merchant_data.empty:
            st.info("No merchant spending data is available.")
        else:
            currencies_in_chart = sorted(
                merchant_data["Currency"]
                .dropna()
                .unique()
            )

            for currency in currencies_in_chart:

                currency_data = merchant_data.loc[
                    merchant_data["Currency"] == currency
                ].copy()

                # Plotly displays horizontal bars from bottom
                # to top, so ascending order puts the largest
                # merchant totals at the top.
                currency_data = currency_data.sort_values(
                    "Total",
                    ascending=True,
                )

                fig = px.bar(
                    currency_data,
                    x="Total",
                    y="Merchant",
                    orientation="h",
                    title=f"{currency} — Top 10 Merchants",
                    custom_data=["Documents", "Average"],
                    color="Merchant",
                    color_discrete_sequence=px.colors.qualitative.Safe,
                    labels={
                        "Total": f"Total ({currency})",
                        "Merchant": "Merchant",
                    },
                )

                fig.update_traces(
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        f"Total: {currency} %{{x:,.2f}}<br>"
                        "Documents: %{customdata[0]:,.0f}<br>"
                        f"Average document: {currency} "
                        "%{customdata[1]:,.2f}"
                        "<extra></extra>"
                    ),
                )

                fig.update_layout(
                    height=450,
                    margin=dict(l=15, r=15, t=65, b=15),
                    showlegend=False,
                    xaxis_title=f"Recorded spending ({currency})",
                    yaxis_title="Merchant",
                    xaxis_tickformat=",.2f",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"merchant_bar_{currency}",
                )
    # ========================================================
    # CATEGORY OVER TIME
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Category Spending Over Time"
    )

    category_time_data = (
        spending_by_category_over_time(
            data
        )
    )

    if not category_time_data.empty:

        currencies_in_chart = (
            category_time_data[
                "Currency"
            ]
            .dropna()
            .unique()
        )

        for currency in currencies_in_chart:

            currency_data = (
                category_time_data[
                    category_time_data[
                        "Currency"
                    ]
                    == currency
                ]
            )

            fig = px.bar(
                currency_data,
                x="Month",
                y="Total",
                color="Category",
                title=(
                    f"{currency} "
                    "Category Spending by Month"
                ),
                color_discrete_sequence=(
                    px.colors.qualitative.Vivid
                ),
            )

            fig.update_layout(
                barmode="stack",
                height=450,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    else:

        st.info(
            "There is not enough dated data to display "
            "category spending over time."
        )

    # ========================================================
    # DOCUMENT DETAILS
    # ========================================================

    st.divider()

    st.subheader(
        "🔎 View Document"
    )


    document_ids = sorted(
        data["ID"].dropna().tolist(),
        key=int,
    )

    # Create a readable name for each document
    document_labels = {}

    for _, row in data.iterrows():

        document_id = row["ID"]

        merchant = (
            str(row["Merchant"]).strip()
            if pd.notna(row["Merchant"])
            and str(row["Merchant"]).strip()
            else "Unknown Merchant"
        )

        document_date = (
            row["Date"].strftime("%d %b %Y")
            if pd.notna(row["Date"])
            else "No Date"
        )

        currency = (
            str(row["Currency"]).strip()
            if pd.notna(row["Currency"])
            else ""
        )

        total = (
            float(row["Total"])
            if pd.notna(row["Total"])
            else 0.0
        )

        document_labels[document_id] = (
            f"#{document_id} | "
            f"{merchant} | "
            f"{document_date} | "
            f"{currency} {total:,.2f}"
        )

    selected_document_id = st.selectbox(
        "Select a document",
        options=document_ids,
        format_func=lambda x:
            document_labels.get(
                x,
                f"Document #{x}",
            ),
    )

    document = get_document(
        selected_document_id
    )

    if document:

        info_col1, info_col2 = (
            st.columns(2)
        )

        with info_col1:

            st.markdown(
                f"**Document Type:** "
                f"{document.document_type}"
            )

            st.markdown(
                f"**Category:** "
                f"{document.category.name}"
            )

            st.markdown(
                f"**Merchant:** "
                f"{document.merchant or 'N/A'}"
            )

            st.markdown(
                f"**Date:** "
                f"{document.document_date or 'N/A'}"
            )

            st.markdown(
                f"**Time:** "
                f"{document.document_time or 'N/A'}"
            )

        with info_col2:

            st.markdown(
                f"**Currency:** "
                f"{document.currency or 'N/A'}"
            )

            st.markdown(
                f"**Subtotal:** "
                f"{document.subtotal or 0}"
            )

            st.markdown(
                f"**Tax:** "
                f"{document.tax or 0}"
            )

            st.markdown(
                f"**Total:** "
                f"{document.total or 0}"
            )

        if document.summary:

            st.markdown(
                f"**Summary:** "
                f"{document.summary}"
            )

        # ====================================================
        # CATEGORY DETAILS
        # ====================================================

        if document.details:

            st.markdown(
                "### Category-Specific Details"
            )

            detail_rows = [
                {
                    "Field": detail.field_name,
                    "Value": detail.field_value,
                }
                for detail in document.details
            ]

            st.dataframe(
                pd.DataFrame(
                    detail_rows
                ),
                use_container_width=True,
                hide_index=True,
            )

        # ====================================================
        # LINE ITEMS
        # ====================================================

        if document.items:

            st.markdown(
                "### Line Items"
            )

            item_rows = [
                {
                    "Description": item.description,
                    "Quantity": float(
                        item.quantity or 0
                    ),
                    "Unit Price": float(
                        item.unit_price or 0
                    ),
                    "Total": float(
                        item.total or 0
                    ),
                }
                for item in document.items
            ]

            st.dataframe(
                pd.DataFrame(
                    item_rows
                ),
                use_container_width=True,
                hide_index=True,
            )