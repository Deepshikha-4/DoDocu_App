# analytics.py

import pandas as pd


def documents_to_dataframe(documents):
    """Convert database documents into a pandas DataFrame."""

    rows = []

    for document in documents:
        rows.append({
            "ID": document.id,
            "Date": document.document_date,
            "Merchant": document.merchant,
            "Category": document.category,
            "Currency": document.currency,
            "Subtotal": float(document.subtotal or 0),
            "Tax": float(document.tax or 0),
            "Total": float(document.total or 0),
            "Type": document.document_type,
        })

    return pd.DataFrame(rows)

def calculate_metrics(data):
    """Calculate basic document metrics."""
    if data.empty:
        return {
            "documents": 0,
            "average": 0,
        }
    return {
        "documents": len(data),
        "average": data["Total"].mean(),
    }

def spending_by_category(data):
    """Return spending grouped by category and currency."""
    if data.empty:
        return pd.DataFrame()
    return (
        data.groupby(
            ["Currency", "Category"],
            dropna=False
        )["Total"]
        .sum()
        .reset_index()
    )


def spending_by_merchant(data):
    """Return spending grouped by merchant and currency."""

    if data.empty:
        return pd.DataFrame()

    return (
        data.groupby(
            ["Currency", "Merchant"],
            dropna=False
        )["Total"]
        .sum()
        .reset_index()
        .sort_values(
            "Total",
            ascending=False
        )
    )


def spending_over_time(data):
    """Return monthly spending grouped by currency."""

    if data.empty:
        return pd.DataFrame()

    result = data.copy()

    result["Date"] = pd.to_datetime(
        result["Date"],
        errors="coerce"
    )

    result = result.dropna(subset=["Date"])

    if result.empty:
        return pd.DataFrame()

    result["Month"] = (
        result["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        result.groupby(
            ["Currency", "Month"],
            dropna=False
        )["Total"]
        .sum()
        .reset_index()
    )