# database.py

import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    inspect,
    text,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# === MODELS === #
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    document_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    merchant = Column(String(255))
    document_date = Column(Date)
    currency = Column(String(10))
    subtotal = Column(Numeric(12, 2))
    tax = Column(Numeric(12, 2))
    total = Column(Numeric(12, 2))
    summary = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    details = relationship(
        "DocumentDetail",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    items = relationship(
        "DocumentItem",
        back_populates="document",
        cascade="all, delete-orphan"
    )

class DocumentDetail(Base):
    __tablename__ = "document_details"
    id = Column(Integer, primary_key=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False
    )
    field_name = Column(
        String(100),
        nullable=False
    )
    field_value = Column(Text)
    document = relationship(
        "Document",
        back_populates="details"
    )

class DocumentItem(Base):
    __tablename__ = "document_items"
    id = Column(Integer, primary_key=True)
    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False
    )
    description = Column(String(500))
    quantity = Column(Numeric(12, 2))
    unit_price = Column(Numeric(12, 2))
    total = Column(Numeric(12, 2))
    document = relationship(
        "Document",
        back_populates="items"
    )

# === DATABASE INITIALIZATION === #
def init_database():
    """Create the DoDocu database tables if they do not exist."""
    Base.metadata.create_all(engine)

# ===SAVE DOCUMENT === #
def save_document(data):
    """
    Save a complete structured document.
    Expected data structure:

    {
        "document_type": "...",
        "category": "...",
        "merchant": "...",
        "document_date": date,
        "currency": "...",
        "subtotal": 0,
        "tax": 0,
        "total": 0,
        "summary": "...",
        "details": {...},
        "items": [...]
    }
    """
    session = SessionLocal()

    try:
        document = Document(
            document_type=data.get("document_type"),
            category=data.get("category"),
            merchant=data.get("merchant"),
            document_date=data.get("document_date"),
            currency=data.get("currency"),
            subtotal=data.get("subtotal"),
            tax=data.get("tax"),
            total=data.get("total"),
            summary=data.get("summary"),
        )

        session.add(document)

        # Save category-specific details
        details = data.get("details", {})

        for field_name, field_value in details.items():
            if field_value is None:
                continue
            detail = DocumentDetail(
                field_name=str(field_name),
                field_value=str(field_value),
            )
            document.details.append(detail)

        # Save line items
        items = data.get("items", [])
        for item in items:
            document_item = DocumentItem(
                description=item.get("description"),
                quantity=item.get("quantity"),
                unit_price=item.get("unit_price"),
                total=item.get("total"),
            )
            document.items.append(document_item)
        session.commit()
        return document.id
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

# === GET DOCUMENTS === #
def get_documents():
    """Return saved documents with their details and items."""

    session = SessionLocal()

    try:
        return (
            session.query(Document)
            .order_by(Document.created_at.desc())
            .all()
        )

    finally:
        session.close()

# === GET SINGLE DOCUMENT === #

def get_document(document_id):
    """Return one document by ID."""

    session = SessionLocal()

    try:
        return (
            session.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    finally:
        session.close()

# === OPTIONAL BACKWARD COMPATIBILITY === #
def save_receipt(data):
    """
    Compatibility wrapper for older DoDocu code.

    Allows older calls to save_receipt() to continue working
    while the application moves to save_document().
    """

    return save_document({
        "document_type": data.get("document_type", "receipt"),
        "category": data.get("category", "general"),
        "merchant": data.get("merchant"),
        "document_date": data.get("receipt_date"),
        "currency": data.get("currency"),
        "subtotal": data.get("subtotal"),
        "tax": data.get("tax"),
        "total": data.get("total"),
        "summary": data.get("summary"),
        "details": {},
        "items": [],
    })


def get_receipts():
    """
    Compatibility wrapper.

    New code should use get_documents().
    """

    return get_documents()