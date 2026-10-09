# database.py

import os
import json
import hashlib

from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
    selectinload,
)

from document_templates import DOCUMENT_TEMPLATES


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not configured in the .env file."
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base = declarative_base()


# ============================================================
# DUPLICATE EXCEPTION
# ============================================================

class DuplicateDocumentError(Exception):

    def __init__(self, existing_document_id):

        self.existing_document_id = (
            existing_document_id
        )

        super().__init__(
            f"Duplicate document already exists "
            f"as record #{existing_document_id}."
        )


# ============================================================
# CATEGORY TABLE
# ============================================================

class Category(Base):

    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True,
    )

    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    documents = relationship(
        "Document",
        back_populates="category",
    )


# ============================================================
# MAIN DOCUMENT TABLE
# ============================================================

class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
    )

    category_id = Column(
        Integer,
        ForeignKey(
            "categories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    document_type = Column(
        String(100),
        nullable=False,
        default="document",
    )

    merchant = Column(
        String(255),
        nullable=True,
        index=True,
    )

    document_date = Column(
        Date,
        nullable=True,
        index=True,
    )

    document_time = Column(
        Time,
        nullable=True,
        index=True,
    )

    currency = Column(
        String(10),
        nullable=True,
        index=True,
    )

    subtotal = Column(
        Numeric(14, 2),
        nullable=True,
    )

    tax = Column(
        Numeric(14, 2),
        nullable=True,
    )

    total = Column(
        Numeric(14, 2),
        nullable=True,
    )

    summary = Column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Exact duplicate fingerprint
    # --------------------------------------------------------

    duplicate_hash = Column(
        String(64),
        unique=True,
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    category = relationship(
        "Category",
        back_populates="documents",
    )

    details = relationship(
        "DocumentDetail",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    items = relationship(
        "DocumentItem",
        back_populates="document",
        cascade="all, delete-orphan",
    )


# ============================================================
# CATEGORY-SPECIFIC DETAILS
# ============================================================

class DocumentDetail(Base):

    __tablename__ = "document_details"

    id = Column(
        Integer,
        primary_key=True,
    )

    document_id = Column(
        Integer,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    field_name = Column(
        String(150),
        nullable=False,
    )

    field_value = Column(
        Text,
        nullable=True,
    )

    field_type = Column(
        String(30),
        nullable=False,
        default="text",
    )

    document = relationship(
        "Document",
        back_populates="details",
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "field_name",
            name="uq_document_detail_field",
        ),
    )


# ============================================================
# DOCUMENT LINE ITEMS
# ============================================================

class DocumentItem(Base):

    __tablename__ = "document_items"

    id = Column(
        Integer,
        primary_key=True,
    )

    document_id = Column(
        Integer,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    description = Column(
        String(255),
        nullable=False,
    )

    quantity = Column(
        Numeric(12, 3),
        nullable=True,
    )

    unit_price = Column(
        Numeric(14, 2),
        nullable=True,
    )

    total = Column(
        Numeric(14, 2),
        nullable=True,
    )

    document = relationship(
        "Document",
        back_populates="items",
    )


# ============================================================
# DATABASE INITIALISATION
# ============================================================

def _seed_categories():

    session = SessionLocal()

    try:

        for code, template in DOCUMENT_TEMPLATES.items():

            existing = (
                session.query(Category)
                .filter(
                    Category.code == code
                )
                .first()
            )

            if existing:
                continue

            category = Category(
                code=code,
                name=template.get(
                    "label",
                    code.title(),
                ),
                description=template.get(
                    "description",
                    f"{template.get('label', code.title())} documents",
                ),
            )

            session.add(category)

        session.commit()

    finally:

        session.close()


def init_database():

    Base.metadata.create_all(
        engine
    )

    _seed_categories()


# ============================================================
# NORMALISATION
# ============================================================

def _normalise_value(value):

    if value is None:
        return ""

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value).strip().casefold()


# ============================================================
# CREATE EXACT DOCUMENT FINGERPRINT
# ============================================================

def create_document_hash(data):

    # Exact duplicate detection requires
    # both date and time.

    document_date = data.get(
        "document_date"
    )

    document_time = data.get(
        "document_time"
    )

    if not document_date or not document_time:
        return None

    details = data.get(
        "details"
    ) or {}

    items = data.get(
        "items"
    ) or []

    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    normalised_details = {
        str(key): _normalise_value(value)
        for key, value in sorted(
            details.items()
        )
        if value is not None
    }

    # --------------------------------------------------------
    # LINE ITEMS
    # --------------------------------------------------------

    normalised_items = []

    for item in items:

        if not isinstance(
            item,
            dict,
        ):
            continue

        description = item.get(
            "description"
        )

        if not description:
            continue

        normalised_items.append(
            {
                "description": _normalise_value(
                    description
                ),
                "quantity": _normalise_value(
                    item.get("quantity")
                ),
                "unit_price": _normalise_value(
                    item.get("unit_price")
                ),
                "total": _normalise_value(
                    item.get("total")
                ),
            }
        )

    # Item order should not matter.
    normalised_items.sort(
        key=lambda item: json.dumps(
            item,
            sort_keys=True,
        )
    )

    # --------------------------------------------------------
    # DUPLICATE PAYLOAD
    # --------------------------------------------------------

    duplicate_payload = {

        "category": _normalise_value(
            data.get("category")
        ),

        "document_type": _normalise_value(
            data.get("document_type")
        ),

        "merchant": _normalise_value(
            data.get("merchant")
        ),

        "document_date": _normalise_value(
            document_date
        ),

        "document_time": _normalise_value(
            document_time
        ),

        "currency": _normalise_value(
            data.get("currency")
        ),

        "subtotal": _normalise_value(
            data.get("subtotal")
        ),

        "tax": _normalise_value(
            data.get("tax")
        ),

        "total": _normalise_value(
            data.get("total")
        ),

        "details": normalised_details,

        "items": normalised_items,
    }

    payload = json.dumps(
        duplicate_payload,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


# ============================================================
# FIND DUPLICATE DOCUMENT
# ============================================================

def find_duplicate_document(data):

    duplicate_hash = create_document_hash(
        data
    )

    if duplicate_hash is None:
        return None

    session = SessionLocal()

    try:

        return (
            session.query(Document)
            .filter(
                Document.duplicate_hash
                == duplicate_hash
            )
            .first()
        )

    finally:

        session.close()


# ============================================================
# SAVE DOCUMENT
# ============================================================

def save_document(data):

    session = SessionLocal()

    try:

        category_code = (
            data.get("category")
            or "general"
        )

        category = (
            session.query(Category)
            .filter(
                Category.code
                == category_code
            )
            .first()
        )

        if category is None:

            category = (
                session.query(Category)
                .filter(
                    Category.code
                    == "general"
                )
                .first()
            )

        if category is None:

            raise ValueError(
                f"Unknown document category: "
                f"{category_code}"
            )

        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        duplicate_hash = (
            create_document_hash(
                data
            )
        )

        if duplicate_hash:

            existing_document = (
                session.query(Document)
                .filter(
                    Document.duplicate_hash
                    == duplicate_hash
                )
                .first()
            )

            if existing_document:

                raise DuplicateDocumentError(
                    existing_document.id
                )

        # ----------------------------------------------------
        # MAIN DOCUMENT
        # ----------------------------------------------------

        document = Document(

            category_id=category.id,

            document_type=data.get(
                "document_type",
                "document",
            ),

            merchant=data.get(
                "merchant"
            ),

            document_date=data.get(
                "document_date"
            ),

            document_time=data.get(
                "document_time"
            ),

            currency=data.get(
                "currency"
            ),

            subtotal=data.get(
                "subtotal"
            ),

            tax=data.get(
                "tax"
            ),

            total=data.get(
                "total"
            ),

            summary=data.get(
                "summary"
            ),

            duplicate_hash=duplicate_hash,
        )

        session.add(
            document
        )

        session.flush()

        # ----------------------------------------------------
        # CATEGORY DETAILS
        # ----------------------------------------------------

        details = data.get(
            "details"
        ) or {}

        for field_name, field_value in details.items():

            if field_value is None:
                continue

            if isinstance(
                field_value,
                bool,
            ):
                field_type = "boolean"

            elif isinstance(
                field_value,
                (int, float),
            ):
                field_type = "number"

            else:
                field_type = "text"

            session.add(
                DocumentDetail(
                    document_id=document.id,
                    field_name=str(
                        field_name
                    ),
                    field_value=str(
                        field_value
                    ),
                    field_type=field_type,
                )
            )

        # ----------------------------------------------------
        # LINE ITEMS
        # ----------------------------------------------------

        items = data.get(
            "items"
        ) or []

        for item in items:

            if not isinstance(
                item,
                dict,
            ):
                continue

            description = item.get(
                "description"
            )

            if not description:
                continue

            session.add(
                DocumentItem(
                    document_id=document.id,
                    description=str(
                        description
                    ),
                    quantity=item.get(
                        "quantity"
                    ),
                    unit_price=item.get(
                        "unit_price"
                    ),
                    total=item.get(
                        "total"
                    ),
                )
            )

        session.commit()

        return document.id

    except Exception:

        session.rollback()
        raise

    finally:

        session.close()


# ============================================================
# GET DOCUMENTS
# ============================================================

def get_documents(
    categories=None,
    months=None,
    currencies=None,
    merchants=None,
    document_types=None,
    start_date=None,
    end_date=None,
):

    session = SessionLocal()

    try:

        query = (
            session.query(Document)
            .options(
                selectinload(
                    Document.category
                ),
                selectinload(
                    Document.details
                ),
                selectinload(
                    Document.items
                ),
            )
        )

        if categories:

            query = (
                query
                .join(Document.category)
                .filter(
                    Category.code.in_(
                        categories
                    )
                )
            )

        if months:

            month_expression = func.to_char(
                Document.document_date,
                "YYYY-MM",
            )

            query = query.filter(
                month_expression.in_(
                    months
                )
            )

        if currencies:

            query = query.filter(
                Document.currency.in_(
                    currencies
                )
            )

        if merchants:

            query = query.filter(
                Document.merchant.in_(
                    merchants
                )
            )

        if document_types:

            query = query.filter(
                Document.document_type.in_(
                    document_types
                )
            )

        if start_date:

            query = query.filter(
                Document.document_date
                >= start_date
            )

        if end_date:

            query = query.filter(
                Document.document_date
                <= end_date
            )

        return (
            query
            .order_by(
                Document.document_date.desc(),
                Document.document_time.desc(),
                Document.id.desc(),
            )
            .all()
        )

    finally:

        session.close()


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

def get_document(document_id):

    session = SessionLocal()

    try:

        return (
            session.query(Document)
            .options(
                selectinload(
                    Document.category
                ),
                selectinload(
                    Document.details
                ),
                selectinload(
                    Document.items
                ),
            )
            .filter(
                Document.id
                == document_id
            )
            .first()
        )

    finally:

        session.close()


# ============================================================
# FILTER OPTIONS
# ============================================================

def get_filter_options():

    session = SessionLocal()

    try:

        categories = (
            session.query(
                Category.code,
                Category.name,
            )
            .order_by(
                Category.name
            )
            .all()
        )

        merchants = (
            session.query(
                Document.merchant
            )
            .filter(
                Document.merchant.isnot(None),
                Document.merchant != "",
            )
            .distinct()
            .order_by(
                Document.merchant
            )
            .all()
        )

        currencies = (
            session.query(
                Document.currency
            )
            .filter(
                Document.currency.isnot(None),
                Document.currency != "",
            )
            .distinct()
            .order_by(
                Document.currency
            )
            .all()
        )

        document_types = (
            session.query(
                Document.document_type
            )
            .filter(
                Document.document_type.isnot(None),
                Document.document_type != "",
            )
            .distinct()
            .order_by(
                Document.document_type
            )
            .all()
        )

        month_expression = func.to_char(
            Document.document_date,
            "YYYY-MM",
        )

        months = (
            session.query(
                month_expression
            )
            .filter(
                Document.document_date.isnot(None)
            )
            .distinct()
            .all()
        )

        return {

            "categories": [
                {
                    "code": code,
                    "name": name,
                }
                for code, name in categories
            ],

            "merchants": [
                merchant
                for (
                    merchant,
                ) in merchants
            ],

            "currencies": [
                currency
                for (
                    currency,
                ) in currencies
            ],

            "document_types": [
                document_type
                for (
                    document_type,
                ) in document_types
            ],

            "months": sorted(
                [
                    month
                    for (
                        month,
                    ) in months
                    if month
                ],
                reverse=True,
            ),
        }

    finally:

        session.close()


# ============================================================
# LEGACY CLEANUP
# ============================================================

def drop_legacy_tables():

    legacy_tables = [
        "document_items",
        "document_details",
        "documents",
        "categories",
        "receipts",
    ]

    with engine.begin() as connection:

        for table_name in legacy_tables:

            connection.exec_driver_sql(
                f'DROP TABLE IF EXISTS '
                f'"{table_name}" CASCADE'
            )


# ============================================================
# RESET DATABASE
# ============================================================

def reset_database():

    Base.metadata.drop_all(
        engine
    )

    Base.metadata.create_all(
        engine
    )

    _seed_categories()


# ============================================================
# LEGACY COMPATIBILITY
# ============================================================

def save_receipt(data):

    return save_document(data)


def get_receipts():

    return get_documents()