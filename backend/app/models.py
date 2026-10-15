from datetime import date, datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(60), index=True)
    title: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(180))
    assigned_customer_ids: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    industry: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(100))
    province: Mapped[str] = mapped_column(String(20))
    segment: Mapped[str] = mapped_column(String(60))
    account_owner: Mapped[str] = mapped_column(String(120))
    since: Mapped[date] = mapped_column(Date)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    health_score: Mapped[int] = mapped_column(Integer)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="customer")
    service_cases: Mapped[list["ServiceCase"]] = relationship(back_populates="customer")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    order_date: Mapped[date] = mapped_column(Date)
    promised_date: Mapped[date] = mapped_column(Date)
    shipped_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    warehouse: Mapped[str] = mapped_column(String(80))
    item_summary: Mapped[str] = mapped_column(String(240))

    customer: Mapped[Customer] = relationship(back_populates="orders")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    issued_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    status: Mapped[str] = mapped_column(String(40))

    customer: Mapped[Customer] = relationship(back_populates="invoices")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), index=True)
    product_name: Mapped[str] = mapped_column(String(180))
    category: Mapped[str] = mapped_column(String(100))
    warehouse: Mapped[str] = mapped_column(String(80))
    on_hand: Mapped[int] = mapped_column(Integer)
    allocated: Mapped[int] = mapped_column(Integer)
    reorder_point: Mapped[int] = mapped_column(Integer)
    lead_time_days: Mapped[int] = mapped_column(Integer)


class ServiceCase(Base):
    __tablename__ = "service_cases"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    opened_date: Mapped[date] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(40))
    issue_type: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(Text)

    customer: Mapped[Customer] = relationship(back_populates="service_cases")


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    effective_date: Mapped[date] = mapped_column(Date)
    renewal_date: Mapped[date] = mapped_column(Date)
    payment_terms_days: Mapped[int] = mapped_column(Integer)
    delivery_target_days: Mapped[int] = mapped_column(Integer)
    annual_value: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    notes: Mapped[str] = mapped_column(Text)

    customer: Mapped[Customer] = relationship(back_populates="contracts")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    title: Mapped[str] = mapped_column(String(220))
    document_type: Mapped[str] = mapped_column(String(80))
    version: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="current")
    effective_date: Mapped[date] = mapped_column(Date)
    allowed_roles: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(String(120))

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    section: Mapped[str] = mapped_column(String(180))
    page: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(), nullable=True)

    document: Mapped[Document] = relationship(back_populates="chunks")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    user_email: Mapped[str] = mapped_column(String(160), index=True)
    user_role: Mapped[str] = mapped_column(String(60))
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    request_summary: Mapped[str] = mapped_column(Text)
    tools_used: Mapped[str] = mapped_column(Text, default="")
    sources_used: Mapped[str] = mapped_column(Text, default="")
    outcome: Mapped[str] = mapped_column(String(60))
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    mode: Mapped[str] = mapped_column(String(40), default="deterministic")


class DailyAiUsage(Base):
    __tablename__ = "daily_ai_usage"
    __table_args__ = (UniqueConstraint("usage_date", "user_email", name="uq_daily_ai_usage_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usage_date: Mapped[date] = mapped_column(Date, index=True)
    user_email: Mapped[str] = mapped_column(String(160), index=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
