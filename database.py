import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set.")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_type = Column(String(50))
    category = Column(String(100))
    merchant = Column(String(255))
    receipt_date = Column(Date)
    currency = Column(String(10))
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_database():
    Base.metadata.create_all(engine)

def save_receipt(data):
    session = SessionLocal()
    try:
        receipt = Receipt(
            document_type=data.get("document_type"),
            category=data.get("category"),
            merchant=data.get("merchant"),
            receipt_date=data.get("receipt_date"),
            currency=data.get("currency"),
            subtotal=data.get("subtotal", 0),
            tax=data.get("tax", 0),
            total=data.get("total", 0),
            summary=data.get("summary"),
        )
        session.add(receipt)
        session.commit()
        return receipt.id
    finally:
        session.close()

def get_receipts():
    session = SessionLocal()
    try:
        return session.query(Receipt).order_by(
            Receipt.receipt_date.desc()
        ).all()
    finally:
        session.close()