import io
from datetime import date

import pandas as pd
import streamlit as st
from PIL import Image

from database import init_database, save_receipt, get_receipts
from gemini_service import extract_document


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="DoDocu",
    page_icon="🦤",
    layout="wide"
)

init_database()


# --------------------------------------------------
# BRANDING
# --------------------------------------------------

st.title("🦤 DoDocu")

st.markdown(
    "### Making paper clutter as extinct as the Dodo."
)

st.caption("Snap. Extract. Extinct.")


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "📷 Scan Document",
        "📊 Records & Analytics"
    ]
)


# ==================================================
# PAGE 1 — SCAN
# ==================================================

if page == "📷 Scan Document":

    st.header("Scan a Document")

    uploaded_file = st.file_uploader(
        "Upload a receipt, invoice or document",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        col1, col2 = st.columns(2)

        # ------------------------------------------
        # IMAGE
        # ------------------------------------------

        with col1:

            st.subheader("Uploaded Document")

            st.image(
                image,
                use_container_width=True
            )

        # ------------------------------------------
        # AI EXTRACTION
        # ------------------------------------------

        with col2:

            st.subheader("AI Extraction")

            if st.button(
                "✨ Extract with DoDocu",
                type="primary"
            ):

                with st.spinner(
                    "DoDocu is reading your document..."
                ):

                    try:

                        # Convert image to bytes
                        image_bytes = io.BytesIO()

                        save_format = (
                            image.format
                            if image.format in ["JPEG", "PNG"]
                            else "JPEG"
                        )

                        if save_format == "JPEG" and image.mode in (
                            "RGBA",
                            "P"
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
                            "Document extracted successfully."
                        )

                    except Exception as e:

                        st.error(
                            f"Extraction failed: {e}"
                        )


# ==================================================
# HUMAN REVIEW
# ==================================================

if page == "📷 Scan Document":

    if "extracted" in st.session_state:

        data = st.session_state["extracted"]

        st.divider()

        st.header("👤 Review Extracted Information")

        st.info(
            "AI-generated information should be reviewed "
            "and corrected before saving."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            document_type = st.text_input(
                "Document Type",
                value=data.get("document_type") or ""
            )

            category = st.text_input(
                "Category",
                value=data.get("category") or ""
            )

            merchant = st.text_input(
                "Merchant",
                value=data.get("merchant") or ""
            )

        with col2:

            receipt_date = st.text_input(
                "Date",
                value=data.get("receipt_date") or ""
            )

            currency = st.text_input(
                "Currency",
                value=data.get("currency") or ""
            )

        with col3:

            subtotal = st.number_input(
                "Subtotal",
                value=float(data.get("subtotal") or 0)
            )

            tax = st.number_input(
                "Tax",
                value=float(data.get("tax") or 0)
            )

            total = st.number_input(
                "Total",
                value=float(data.get("total") or 0)
            )

        summary = st.text_area(
            "Summary",
            value=data.get("summary") or ""
        )

        # ------------------------------------------
        # SAVE
        # ------------------------------------------

        if st.button(
            "💾 Save to DoDocu",
            type="primary"
        ):

            try:

                parsed_date = None

                if receipt_date:
                    parsed_date = date.fromisoformat(
                        receipt_date
                    )

                final_data = {
                    "document_type": document_type,
                    "category": category,
                    "merchant": merchant,
                    "receipt_date": parsed_date,
                    "currency": currency,
                    "subtotal": subtotal,
                    "tax": tax,
                    "total": total,
                    "summary": summary,
                }

                record_id = save_receipt(
                    final_data
                )

                st.success(
                    f"Document saved successfully! "
                    f"Record ID: {record_id}"
                )

                del st.session_state["extracted"]

            except Exception as e:

                st.error(
                    f"Could not save record: {e}"
                )


# ==================================================
# PAGE 2 — RECORDS
# ==================================================

if page == "📊 Records & Analytics":

    st.header("📊 Records & Analytics")

    records = get_receipts()

    if not records:

        st.info(
            "No documents have been saved yet."
        )

    else:

        data = pd.DataFrame([
            {
                "ID": r.id,
                "Date": r.receipt_date,
                "Merchant": r.merchant,
                "Category": r.category,
                "Currency": r.currency,
                "Total": r.total,
                "Type": r.document_type,
            }
            for r in records
        ])

        # ------------------------------------------
        # METRICS
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Documents",
                len(data)
            )

        with col2:
            st.metric(
                "Total Spending",
                f"{data['Total'].sum():,.2f}"
            )

        with col3:
            st.metric(
                "Average Document",
                f"{data['Total'].mean():,.2f}"
            )

        st.divider()

        # ------------------------------------------
        # RECORDS
        # ------------------------------------------

        st.subheader("Saved Records")

        st.dataframe(
            data,
            use_container_width=True,
            hide_index=True
        )

        # ------------------------------------------
        # CATEGORY ANALYTICS
        # ------------------------------------------

        st.subheader("Spending by Category")

        category_data = (
            data.groupby("Category")["Total"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_data)