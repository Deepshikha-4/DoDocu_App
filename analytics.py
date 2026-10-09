
# analytics.py

import pandas as pd


# ============================================================
# SHARED COLUMN DEFINITIONS
# ============================================================

DOCUMENT_COLUMNS = [
    "ID",
    "Date",
    "Time",
    "Merchant",
    "Category",
    "Category Code",
    "Currency",
    "Subtotal",
    "Tax",
    "Total",
    "Type",
]

CATEGORY_COLUMNS = [
    "Currency",
    "Category",
    "Total",
    "Percentage",
    "Documents",
]

MERCHANT_COLUMNS = [
    "Currency",
    "Merchant",
    "Total",
    "Documents",
    "Average",
]


MONTHLY_COLUMNS = [
    "Currency",
    "Month",
    "Total",
    "Documents",
]

DAILY_COLUMNS = [
    "Currency",
    "Date",
    "Total",
    "Documents",
    "Average",
]

CATEGORY_MONTHLY_COLUMNS = [
    "Currency",
    "Month",
    "Category",
    "Total",
    "Documents",
]


# ============================================================
# EMPTY DATAFRAMES
# ============================================================

def _empty_frame(columns):
    """Return an empty DataFrame with the expected columns."""
    return pd.DataFrame(columns=columns)


# ============================================================
# DATA VALIDATION AND NORMALISATION
# ============================================================

def _valid_data(data):
    """Check whether the DataFrame has the required fields."""
    return (
        isinstance(data, pd.DataFrame)
        and not data.empty
        and "Total" in data.columns
        and "Currency" in data.columns
    )


def _normalise_data(data):
    """Return a normalised copy of the input DataFrame."""

    if not isinstance(data, pd.DataFrame):
        return pd.DataFrame()

    result = data.copy()

    # Ensure the dimensions used in grouping always exist.
    defaults = {
        "Currency": "Unknown",
        "Category": "Unknown",
        "Merchant": "Unknown",
        "Type": "Unknown",
    }

    for column, default in defaults.items():

        if column not in result.columns:
            result[column] = default

        result[column] = (
            result[column]
            .fillna(default)
            .astype(str)
            .str.strip()
            .replace("", default)
        )

    result["Currency"] = result["Currency"].str.upper()

    # Normalise numeric fields.
    for column in ["Total", "Subtotal", "Tax"]:

        if column not in result.columns:
            result[column] = 0.0

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        ).fillna(0.0)

    # Normalise dates when present.
    if "Date" in result.columns:
        result["Date"] = pd.to_datetime(
            result["Date"],
            errors="coerce",
        )

    return result


def _prepare_dated_data(data):
    """Return normalised records that have valid document dates."""

    result = _normalise_data(data)

    if result.empty or "Date" not in result.columns:
        return pd.DataFrame()

    result = result.dropna(subset=["Date"]).copy()

    return result


def _group_sum(data, group_columns, value_column="Total"):
    """Aggregate numeric values by the requested dimensions."""

    if not _valid_data(data):
        return pd.DataFrame()

    result = _normalise_data(data)

    required = group_columns + [value_column]

    if any(column not in result.columns for column in required):
        return pd.DataFrame()

    return (
        result.groupby(
            group_columns,
            dropna=False,
            observed=True,
        )[value_column]
        .sum()
        .reset_index()
    )


# ============================================================
# DATABASE DOCUMENTS TO DATAFRAME
# ============================================================

def documents_to_dataframe(documents):
    """Convert database document objects into an analytics DataFrame."""

    rows = []

    for document in documents:

        category_object = getattr(document, "category", None)

        category = (
            getattr(category_object, "name", None)
            or "Unknown"
        )

        category_code = (
            getattr(category_object, "code", None)
            or "unknown"
        )

        document_date = getattr(
            document,
            "document_date",
            None,
        )

        document_time = getattr(
            document,
            "document_time",
            None,
        )

        rows.append(
            {
                "ID": getattr(document, "id", None),
                "Date": document_date,
                "Time": document_time,
                "Merchant": (
                    getattr(document, "merchant", None)
                    or "Unknown"
                ),
                "Category": category,
                "Category Code": category_code,
                "Currency": (
                    getattr(document, "currency", None)
                    or "Unknown"
                ),
                "Subtotal": getattr(document, "subtotal", 0) or 0,
                "Tax": getattr(document, "tax", 0) or 0,
                "Total": getattr(document, "total", 0) or 0,
                "Type": (
                    getattr(document, "document_type", None)
                    or "Unknown"
                ),
            }
        )

    if not rows:
        return _empty_frame(DOCUMENT_COLUMNS)

    data = pd.DataFrame(rows, columns=DOCUMENT_COLUMNS)

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
    )

    # Keep the time field suitable for display.
    # The database may return datetime.time objects.
    data["Time"] = data["Time"].map(
        lambda value: (
            value.strftime("%H:%M:%S")
            if hasattr(value, "strftime")
            else value
        )
    )

    for column in ["Total", "Subtotal", "Tax"]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        ).fillna(0.0)

    for column in ["Merchant", "Category", "Type"]:
        data[column] = (
            data[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
        )

    data["Category Code"] = (
        data["Category Code"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
    )

    data["Currency"] = (
        data["Currency"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .str.upper()
    )

    return data


# ============================================================
# BASIC DASHBOARD METRICS
# ============================================================

def calculate_metrics(data):
    """
    Calculate document and spending metrics.

    Monetary totals are kept separate by currency.
    The overall top category is based on document count.
    """

    empty_result = {
        "documents": 0,
        "total_by_currency": {},
        "average_by_currency": {},
        "top_category": None,
        "top_category_by_currency": {},
        "documents_by_currency": {},
        "average_documents_per_day": {},
        "largest_document_by_currency": {},
        "dated_documents": 0,
        "undated_documents": 0,
    }

    if not _valid_data(data):
        return empty_result

    result = _normalise_data(data)

    if result.empty:
        return empty_result

    total_by_currency = (
        result.groupby("Currency")["Total"]
        .sum()
        .to_dict()
    )

    average_by_currency = (
        result.groupby("Currency")["Total"]
        .mean()
        .to_dict()
    )

    documents_by_currency = (
        result.groupby("Currency")
        .size()
        .to_dict()
    )

    category_counts = (
        result.groupby("Category", dropna=False)
        .size()
        .sort_values(ascending=False)
    )

    top_category = (
        category_counts.index[0]
        if not category_counts.empty
        else None
    )

    # Find the highest-spending category separately
    # for each currency.
    category_totals = (
        result.groupby(
            ["Currency", "Category"],
            dropna=False,
        )["Total"]
        .sum()
        .reset_index()
    )

    top_category_by_currency = {}

    if not category_totals.empty:

        top_rows = category_totals.loc[
            category_totals.groupby("Currency")["Total"].idxmax()
        ]

        top_category_by_currency = dict(
            zip(
                top_rows["Currency"],
                top_rows["Category"],
            )
        )

    dated = _prepare_dated_data(result)

    if not dated.empty:

        dated["Day"] = dated["Date"].dt.date

        daily_counts = (
            dated.groupby(["Currency", "Day"])
            .size()
            .groupby("Currency")
            .mean()
            .to_dict()
        )

        dated_documents = len(dated)

    else:
        daily_counts = {}
        dated_documents = 0

    largest_document_by_currency = (
        result.groupby("Currency")["Total"]
        .max()
        .to_dict()
    )

    return {
        "documents": len(result),
        "total_by_currency": total_by_currency,
        "average_by_currency": average_by_currency,
        "top_category": top_category,
        "top_category_by_currency": top_category_by_currency,
        "documents_by_currency": documents_by_currency,
        "average_documents_per_day": daily_counts,
        "largest_document_by_currency": largest_document_by_currency,
        "dated_documents": dated_documents,
        "undated_documents": len(result) - dated_documents,
    }


# ============================================================
# SPENDING BY CATEGORY
# ============================================================

def spending_by_category(data):
    """Return spending totals and percentages by currency and category."""

    if not _valid_data(data):
        return _empty_frame(CATEGORY_COLUMNS)

    result = _normalise_data(data)

    result = (
        result.groupby(
            ["Currency", "Category"],
            dropna=False,
            observed=True,
        )
        .agg(
            Total=("Total", "sum"),
            Documents=("Total", "size"),
        )
        .reset_index()
    )

    currency_totals = (
        result.groupby("Currency")["Total"]
        .transform("sum")
    )

    result["Percentage"] = (
        result["Total"]
        .div(currency_totals.where(currency_totals != 0))
        .mul(100)
        .fillna(0.0)
    )

    return (
        result.sort_values(
            ["Currency", "Total"],
            ascending=[True, False],
        )
        .reset_index(drop=True)
    )


# ============================================================
# SPENDING BY MERCHANT
# ============================================================

def spending_by_merchant(data, top_n=10):
    """Rank merchants by spending separately for each currency."""

    if not _valid_data(data):
        return _empty_frame(MERCHANT_COLUMNS)

    if not isinstance(top_n, int) or top_n < 1:
        raise ValueError("top_n must be a positive integer.")

    result = _normalise_data(data)

    result = (
        result.groupby(
            ["Currency", "Merchant"],
            dropna=False,
            observed=True,
        )
        .agg(
            Total=("Total", "sum"),
            Documents=("Total", "size"),
            Average=("Total", "mean"),
        )
        .reset_index()
    )

    result = result.sort_values(
        ["Currency", "Total", "Merchant"],
        ascending=[True, False, True],
    )

    result = (
        result.groupby(
            "Currency",
            group_keys=False,
            observed=True,
        )
        .head(top_n)
    )

    return result.reset_index(drop=True)


# ============================================================
# MONTHLY SPENDING
# ============================================================


def spending_over_time(data):
    """Calculate monthly total spending and receipt counts."""

    result = _prepare_dated_data(data)

    if result.empty:
        return _empty_frame(MONTHLY_COLUMNS)

    result["Month"] = (
        result["Date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    result = (
        result.groupby(
            ["Currency", "Month"],
            dropna=False,
            observed=True,
        )
        .agg(
            Total=("Total", "sum"),
            Documents=("ID", "count"),
        )
        .reset_index()
        .sort_values(
            ["Currency", "Month"],
            ascending=[True, True],
        )
    )

    return (
        result.reindex(columns=MONTHLY_COLUMNS)
        .reset_index(drop=True)
    )


# ============================================================
# DAILY SPENDING
# ============================================================

def spending_by_day(data):
    """Aggregate spending by date and currency."""

    result = _prepare_dated_data(data)

    if result.empty:
        return _empty_frame(DAILY_COLUMNS)

    result["Date"] = result["Date"].dt.normalize()

    result = (
        result.groupby(
            ["Currency", "Date"],
            dropna=False,
            observed=True,
        )
        .agg(
            Total=("Total", "sum"),
            Documents=("Total", "size"),
            Average=("Total", "mean"),
        )
        .reset_index()
        .sort_values(["Currency", "Date"])
    )

    return result.reindex(columns=DAILY_COLUMNS).reset_index(drop=True)


# ============================================================
# INDIVIDUAL DOCUMENT SPENDING
# ============================================================

def spending_by_document(data):
    """Return transaction-level records without aggregation."""

    columns = [
        "ID",
        "Date",
        "Time",
        "Merchant",
        "Category",
        "Currency",
        "Total",
        "Type",
    ]

    if not isinstance(data, pd.DataFrame) or data.empty:
        return _empty_frame(columns)

    result = _normalise_data(data)

    for column in columns:

        if column not in result.columns:
            result[column] = pd.NA

    result = result[columns].copy()

    sort_columns = [
        column
        for column in ["Date", "Time", "ID"]
        if column in result.columns
    ]

    if sort_columns:
        result = result.sort_values(
            sort_columns,
            ascending=False,
            na_position="last",
        )

    return result.reset_index(drop=True)


# ============================================================
# CATEGORY SPENDING OVER TIME
# ============================================================

def spending_by_category_over_time(data):
    """Calculate monthly spending by category and currency."""

    result = _prepare_dated_data(data)

    if result.empty:
        return _empty_frame(CATEGORY_MONTHLY_COLUMNS)

    result["Month"] = (
        result["Date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    result = (
        result.groupby(
            ["Currency", "Month", "Category"],
            dropna=False,
            observed=True,
        )
        .agg(
            Total=("Total", "sum"),
            Documents=("Total", "size"),
        )
        .reset_index()
        .sort_values(
            ["Currency", "Month", "Total"],
            ascending=[True, True, False],
        )
    )

    return (
        result.reindex(columns=CATEGORY_MONTHLY_COLUMNS)
        .reset_index(drop=True)
    )


# ============================================================
# DOCUMENT COUNT BY CATEGORY
# ============================================================

def documents_by_category(data):
    """Count records by category and currency."""

    columns = [
        "Currency",
        "Category",
        "Documents",
        "Total",
    ]

    if not _valid_data(data):
        return _empty_frame(columns)

    result = _normalise_data(data)

    result = (
        result.groupby(
            ["Currency", "Category"],
            dropna=False,
            observed=True,
        )
        .agg(
            Documents=("Total", "size"),
            Total=("Total", "sum"),
        )
        .reset_index()
        .sort_values(
            ["Currency", "Documents"],
            ascending=[True, False],
        )
    )

    return result.reset_index(drop=True)