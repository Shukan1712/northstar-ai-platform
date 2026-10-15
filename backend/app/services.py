import re
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from .config import get_settings
from .models import AuditEvent, Contract, Customer, Document, DocumentChunk, InventoryItem, Invoice, Order, ServiceCase, User


DEMO_TODAY = date(2026, 10, 5)
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def money(value: Decimal | int | float) -> float:
    return round(float(value), 2)


def permitted_customer_ids(user: User) -> list[str] | None:
    if user.role == "account_manager":
        return [item for item in user.assigned_customer_ids.split(",") if item]
    return None


def can_view_customer(user: User, customer_id: str) -> bool:
    allowed = permitted_customer_ids(user)
    return allowed is None or customer_id in allowed


def assert_customer_access(user: User, customer_id: str) -> None:
    if not can_view_customer(user, customer_id):
        raise HTTPException(status_code=403, detail="This customer is outside your assigned account scope")


def customer_query(user: User):
    query = select(Customer)
    allowed = permitted_customer_ids(user)
    if allowed is not None:
        query = query.where(Customer.id.in_(allowed))
    return query


def attention_item(
    *,
    alert_type: str,
    severity: str,
    title: str,
    detail: str,
    record_id: str,
    context: str,
    next_action: str,
    target_page: str = "insight",
    customer_id: str | None = None,
    suggested_question: str | None = None,
) -> dict[str, Any]:
    if suggested_question is None:
        if alert_type in {"customer_collections", "collections", "cash_exposure"}:
            suggested_question = f"Review invoice risk related to {record_id}. What requires attention and what should happen next?"
        elif alert_type in {"customer_delivery", "fulfilment", "service_level", "service_escalation"}:
            suggested_question = f"Review the delivery or service exception related to {record_id}. What requires attention and what should happen next?"
        elif alert_type == "inventory":
            suggested_question = f"Review inventory risk for SKU {record_id}. What requires attention and what should Operations do next?"
        elif alert_type in {"customer_renewal", "commercial_renewal", "enterprise_risk"}:
            suggested_question = f"Prepare an evidence-backed account risk briefing related to {record_id}."
        else:
            suggested_question = f"Explain the governed business issue related to {record_id}."
    return {
        "type": alert_type,
        "severity": severity,
        "title": title,
        "detail": detail,
        "record_id": record_id,
        "context": context,
        "next_action": next_action,
        "target_page": target_page,
        "customer_id": customer_id,
        "suggested_question": suggested_question,
    }


def role_attention(
    db: Session,
    user: User,
    customers: list[Customer],
    orders: list[Order],
    invoices: list[Invoice],
    cases: list[ServiceCase],
    contracts: list[Contract],
    delivery_rate: float,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    customer_names = {customer.id: customer.name for customer in customers}

    if user.role == "account_manager":
        items = []
        for order in orders:
            if order.status in {"Delayed", "Backordered"}:
                items.append(attention_item(
                    alert_type="customer_delivery",
                    severity="critical" if "safety" in order.item_summary.lower() else "high",
                    title=f"Recovery plan needed for {order.id}",
                    detail=f"{customer_names[order.customer_id]} · {order.item_summary}",
                    record_id=order.id,
                    context="Customer commitment",
                    next_action="Confirm a recovery date before contacting the customer",
                    customer_id=order.customer_id,
                ))
        for invoice in invoices:
            if invoice.status == "Overdue":
                remaining = money(invoice.amount - invoice.paid_amount)
                items.append(attention_item(
                    alert_type="customer_collections",
                    severity="high" if remaining >= 25000 else "medium",
                    title=f"Payment conversation needed for {invoice.id}",
                    detail=f"{customer_names[invoice.customer_id]} · ${remaining:,.2f} overdue",
                    record_id=invoice.id,
                    context="Account relationship",
                    next_action="Align with Finance before the next customer conversation",
                    customer_id=invoice.customer_id,
                ))
        for contract in contracts:
            days = (contract.renewal_date - DEMO_TODAY).days
            if 0 <= days <= 90:
                items.append(attention_item(
                    alert_type="customer_renewal",
                    severity="medium",
                    title=f"Renewal preparation for {contract.id}",
                    detail=f"{customer_names[contract.customer_id]} · renews in {days} days",
                    record_id=contract.id,
                    context="Growth and retention",
                    next_action="Schedule a value review and renewal discovery",
                    target_page="accounts",
                    customer_id=contract.customer_id,
                ))
        profile = {
            "eyebrow": "Your action queue",
            "title": "Customer commitments",
            "summary": "Assigned-account risks that need customer ownership or coordination.",
            "count_label": "owned actions",
            "empty_title": "No customer commitments need attention",
        }
    elif user.role == "finance_analyst":
        items = []
        for invoice in invoices:
            remaining = money(invoice.amount - invoice.paid_amount)
            days_past_due = (DEMO_TODAY - invoice.due_date).days
            if invoice.status == "Overdue":
                items.append(attention_item(
                    alert_type="collections",
                    severity="high" if remaining >= 25000 or days_past_due >= 15 else "medium",
                    title=f"{invoice.id} is {days_past_due} days overdue",
                    detail=f"{customer_names[invoice.customer_id]} · ${remaining:,.2f} outstanding",
                    record_id=invoice.id,
                    context="Collections",
                    next_action="Verify the payment commitment and collection owner",
                    customer_id=invoice.customer_id,
                ))
            elif invoice.status == "Open" and remaining >= 50000:
                days_until_due = (invoice.due_date - DEMO_TODAY).days
                items.append(attention_item(
                    alert_type="cash_exposure",
                    severity="medium",
                    title=f"Large receivable due in {days_until_due} days",
                    detail=f"{customer_names[invoice.customer_id]} · ${remaining:,.2f} on {invoice.id}",
                    record_id=invoice.id,
                    context="Cash exposure",
                    next_action="Confirm invoice acceptance before the due date",
                    customer_id=invoice.customer_id,
                ))
        profile = {
            "eyebrow": "Finance worklist",
            "title": "Receivables follow-up",
            "summary": "Past-due balances and material upcoming cash exposure.",
            "count_label": "finance actions",
            "empty_title": "No receivables require follow-up",
        }
    elif user.role == "operations_manager":
        items = []
        for order in orders:
            if order.status in {"Delayed", "Backordered"}:
                days_late = max((DEMO_TODAY - order.promised_date).days, 0)
                items.append(attention_item(
                    alert_type="fulfilment",
                    severity="critical" if order.status == "Backordered" or days_late >= 7 else "high",
                    title=f"{order.id} needs a recovery plan",
                    detail=f"{order.warehouse} · {days_late} days beyond promise · {order.item_summary}",
                    record_id=order.id,
                    context="Fulfilment",
                    next_action="Assign supply, substitute, and confirmed ship-date owners",
                    customer_id=order.customer_id,
                ))
        inventory = db.scalars(select(InventoryItem).order_by(InventoryItem.warehouse, InventoryItem.sku)).all()
        for item in inventory:
            available = item.on_hand - item.allocated
            if available < 0 or item.on_hand <= item.reorder_point:
                items.append(attention_item(
                    alert_type="inventory",
                    severity="critical" if available < 0 else "high",
                    title=f"{item.sku} has {available} units available",
                    detail=f"{item.warehouse} · {item.on_hand} on hand, {item.allocated} allocated · {item.lead_time_days}-day lead time",
                    record_id=item.sku,
                    context="Inventory control",
                    next_action="Expedite, rebalance, or approve an alternate product",
                ))
        for case in cases:
            if case.status == "Escalated":
                items.append(attention_item(
                    alert_type="service_escalation",
                    severity="high",
                    title=f"Escalated service case {case.id}",
                    detail=f"{customer_names[case.customer_id]} · {case.summary}",
                    record_id=case.id,
                    context="Service recovery",
                    next_action="Name the incident owner and customer recovery path",
                    customer_id=case.customer_id,
                ))
        profile = {
            "eyebrow": "Operations control tower",
            "title": "Fulfilment and inventory",
            "summary": "Delivery, stock, and service exceptions requiring operational ownership.",
            "count_label": "operational actions",
            "empty_title": "No operational exceptions need attention",
        }
    elif user.role == "executive":
        items = []
        for customer in customers:
            customer_orders = [order for order in orders if order.customer_id == customer.id and order.status in {"Delayed", "Backordered"}]
            customer_overdue = sum((invoice.amount - invoice.paid_amount for invoice in invoices if invoice.customer_id == customer.id and invoice.status == "Overdue"), Decimal("0"))
            customer_cases = [case for case in cases if case.customer_id == customer.id and case.status in {"Open", "Escalated"}]
            signals = len(customer_orders) + (1 if customer_overdue else 0) + len(customer_cases)
            if signals >= 2:
                facts = []
                if customer_orders:
                    facts.append(f"{len(customer_orders)} delivery exception")
                if customer_overdue:
                    facts.append(f"${money(customer_overdue):,.0f} overdue")
                if customer_cases:
                    facts.append(f"{len(customer_cases)} open escalation")
                items.append(attention_item(
                    alert_type="enterprise_risk",
                    severity="critical" if signals >= 3 or customer.health_score < 70 else "high",
                    title=f"{customer.name}: cross-functional risk",
                    detail=" · ".join(facts),
                    record_id=customer.id,
                    context=f"{customer.segment} account · health {customer.health_score}",
                    next_action="Assign one accountable recovery owner across functions",
                    target_page="accounts",
                    customer_id=customer.id,
                ))
        for contract in contracts:
            days = (contract.renewal_date - DEMO_TODAY).days
            if 0 <= days <= 45:
                items.append(attention_item(
                    alert_type="commercial_renewal",
                    severity="high" if contract.annual_value >= 500000 else "medium",
                    title=f"${money(contract.annual_value):,.0f} renewal in {days} days",
                    detail=f"{customer_names[contract.customer_id]} · {contract.id}",
                    record_id=contract.id,
                    context="Revenue retention",
                    next_action="Confirm executive sponsor, value case, and negotiation plan",
                    target_page="accounts",
                    customer_id=contract.customer_id,
                ))
        if delivery_rate < 90:
            items.append(attention_item(
                alert_type="service_level",
                severity="medium",
                title=f"On-time delivery is {delivery_rate:.0f}%",
                detail="Portfolio service level is below the 90% management threshold.",
                record_id="KPI-OTD",
                context="Enterprise performance",
                next_action="Review the two largest drivers with Operations",
            ))
        profile = {
            "eyebrow": "Executive risk view",
            "title": "Enterprise risk signals",
            "summary": "Material cross-functional risks, service levels, and revenue-retention events.",
            "count_label": "leadership actions",
            "empty_title": "No material enterprise risks detected",
        }
    else:
        settings = get_settings()
        items = []
        indexed_chunks = db.scalar(select(func.count()).select_from(DocumentChunk).where(DocumentChunk.embedding.is_not(None))) or 0
        if not settings.ai_enabled:
            items.append(attention_item(
                alert_type="model_configuration",
                severity="high",
                title="Model-assisted answers are not configured",
                detail="Insight is operating in deterministic demo mode.",
                record_id="AI-MODE",
                context="Runtime configuration",
                next_action="Add the API key and chat model, then restart Northstar",
                target_page="governance",
            ))
        if not settings.embeddings_enabled:
            items.append(attention_item(
                alert_type="retrieval_configuration",
                severity="medium",
                title="Semantic retrieval is not configured",
                detail="Document search is currently using governed keyword matching.",
                record_id="AI-RAG",
                context="Retrieval control",
                next_action="Add the embedding model and restart Northstar",
                target_page="governance",
            ))
        elif indexed_chunks == 0:
            items.append(attention_item(
                alert_type="retrieval_index",
                severity="high",
                title="Semantic document index needs to be built",
                detail="An embedding model is configured, but no document chunks are indexed.",
                record_id="AI-INDEX",
                context="Retrieval control",
                next_action="Open Governance and build the pgvector index",
                target_page="governance",
            ))
        profile = {
            "eyebrow": "AI operations",
            "title": "Platform control health",
            "summary": "Configuration and retrieval controls that affect governed AI behavior.",
            "count_label": "control actions",
            "empty_title": "All monitored AI controls are healthy",
        }

    items.sort(key=lambda item: (SEVERITY_ORDER.get(item["severity"], 9), item["title"]))
    return profile, items


def list_customers(db: Session, user: User) -> list[dict[str, Any]]:
    customers = db.scalars(customer_query(user).order_by(Customer.name)).all()
    result = []
    for customer in customers:
        outstanding = sum((invoice.amount - invoice.paid_amount for invoice in customer.invoices if invoice.status != "Paid"), Decimal("0"))
        open_cases = sum(1 for case in customer.service_cases if case.status not in {"Resolved", "Closed"})
        result.append({
            "id": customer.id,
            "name": customer.name,
            "industry": customer.industry,
            "location": f"{customer.city}, {customer.province}",
            "segment": customer.segment,
            "account_owner": customer.account_owner,
            "health_score": customer.health_score,
            "outstanding_balance": money(outstanding),
            "open_cases": open_cases,
        })
    return result


def dashboard(db: Session, user: User) -> dict[str, Any]:
    customers = db.scalars(customer_query(user)).all()
    customer_ids = [customer.id for customer in customers]
    if not customer_ids:
        return {"kpis": {}, "exceptions": [], "revenue_trend": [], "portfolio": []}

    orders = db.scalars(select(Order).where(Order.customer_id.in_(customer_ids))).all()
    invoices = db.scalars(select(Invoice).where(Invoice.customer_id.in_(customer_ids))).all()
    cases = db.scalars(select(ServiceCase).where(ServiceCase.customer_id.in_(customer_ids))).all()
    contracts = db.scalars(select(Contract).where(Contract.customer_id.in_(customer_ids))).all()
    revenue = sum((order.total for order in orders if order.status in {"Delivered", "Delivered late"}), Decimal("0"))
    outstanding = sum((invoice.amount - invoice.paid_amount for invoice in invoices if invoice.status != "Paid"), Decimal("0"))
    completed = [order for order in orders if order.status in {"Delivered", "Delivered late"}]
    on_time = [order for order in completed if order.shipped_date and order.shipped_date <= order.promised_date]
    delivery_rate = round((len(on_time) / len(completed)) * 100, 1) if completed else 0
    open_cases = [case for case in cases if case.status not in {"Resolved", "Closed"}]

    attention, exceptions = role_attention(db, user, customers, orders, invoices, cases, contracts, delivery_rate)

    portfolio = []
    for customer in customers:
        portfolio.append({"name": customer.name, "score": customer.health_score, "segment": customer.segment, "id": customer.id})

    return {
        "kpis": {
            "recognized_revenue": money(revenue),
            "outstanding_balance": money(outstanding),
            "on_time_delivery": delivery_rate,
            "open_service_cases": len(open_cases),
            "active_customers": len(customers),
        },
        "attention": attention,
        "exceptions": exceptions[:8],
        "revenue_trend": [
            {"month": "May", "value": 112000},
            {"month": "Jun", "value": 128500},
            {"month": "Jul", "value": 119800},
            {"month": "Aug", "value": 141200},
            {"month": "Sep", "value": money(sum((order.total for order in orders if order.order_date.month == 9), Decimal("0")))},
        ],
        "portfolio": sorted(portfolio, key=lambda item: item["score"]),
        "scope_note": "Assigned accounts only" if user.role == "account_manager" else "All demo customers",
    }


def customer_briefing(db: Session, user: User, customer_id: str) -> dict[str, Any]:
    assert_customer_access(user, customer_id)
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = db.scalars(select(Order).where(Order.customer_id == customer_id).order_by(Order.order_date.desc())).all()
    invoices = db.scalars(select(Invoice).where(Invoice.customer_id == customer_id).order_by(Invoice.issued_date.desc())).all()
    cases = db.scalars(select(ServiceCase).where(ServiceCase.customer_id == customer_id).order_by(ServiceCase.opened_date.desc())).all()
    contracts = db.scalars(select(Contract).where(Contract.customer_id == customer_id).order_by(Contract.renewal_date)).all()
    outstanding = sum((invoice.amount - invoice.paid_amount for invoice in invoices if invoice.status != "Paid"), Decimal("0"))
    overdue = sum((invoice.amount - invoice.paid_amount for invoice in invoices if invoice.status == "Overdue"), Decimal("0"))
    delivered = [order for order in orders if order.shipped_date]
    on_time = [order for order in delivered if order.shipped_date <= order.promised_date]
    rate = round(len(on_time) / len(delivered) * 100, 1) if delivered else 0
    risks = []
    if overdue:
        risks.append(f"${money(overdue):,.2f} is overdue and should be discussed with Finance.")
    delayed = [order for order in orders if order.status in {"Delayed", "Backordered"}]
    if delayed:
        risks.append(f"{len(delayed)} active order requires delivery attention.")
    open_cases = [case for case in cases if case.status not in {"Resolved", "Closed"}]
    if open_cases:
        risks.append(f"{len(open_cases)} service case is open or escalated.")
    opportunities = []
    if customer.health_score >= 80:
        opportunities.append("Account health supports a proactive expansion or service-review conversation.")
    if contracts and (contracts[0].renewal_date - date(2026, 10, 5)).days <= 90:
        opportunities.append(f"Contract {contracts[0].id} renews on {contracts[0].renewal_date.isoformat()}.")
    if not opportunities:
        opportunities.append("Resolve current exceptions before proposing broader account expansion.")

    return {
        "customer": {"id": customer.id, "name": customer.name, "industry": customer.industry, "location": f"{customer.city}, {customer.province}", "segment": customer.segment, "owner": customer.account_owner, "since": customer.since.isoformat(), "health_score": customer.health_score},
        "metrics": {"outstanding_balance": money(outstanding), "overdue_balance": money(overdue), "on_time_delivery": rate, "recent_order_value": money(sum((order.total for order in orders), Decimal("0"))), "open_cases": len(open_cases)},
        "risks": risks or ["No material exception is present in the current synthetic records."],
        "opportunities": opportunities,
        "orders": [{"id": item.id, "date": item.order_date.isoformat(), "status": item.status, "total": money(item.total), "summary": item.item_summary, "promised_date": item.promised_date.isoformat()} for item in orders[:5]],
        "invoices": [{"id": item.id, "status": item.status, "amount": money(item.amount), "remaining": money(item.amount - item.paid_amount), "due_date": item.due_date.isoformat()} for item in invoices[:5]],
        "service_cases": [{"id": item.id, "priority": item.priority, "status": item.status, "summary": item.summary, "opened_date": item.opened_date.isoformat()} for item in cases[:5]],
        "contracts": [{"id": item.id, "renewal_date": item.renewal_date.isoformat(), "annual_value": money(item.annual_value), "delivery_target_days": item.delivery_target_days, "notes": item.notes} for item in contracts],
        "citations": [
            {"source_type": "customer", "source_id": customer.id, "label": "Customer master record"},
            *[{"source_type": "order", "source_id": item.id, "label": f"Order {item.id}"} for item in orders[:3]],
            *[{"source_type": "invoice", "source_id": item.id, "label": f"Invoice {item.id}"} for item in invoices[:2]],
            *[{"source_type": "contract", "source_id": item.id, "label": f"Contract {item.id}"} for item in contracts[:1]],
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def search_customers(db: Session, user: User, query: str) -> list[dict[str, Any]]:
    statement = customer_query(user).where(or_(Customer.name.ilike(f"%{query}%"), Customer.id.ilike(f"%{query}%"))).limit(10)
    return [{"id": item.id, "name": item.name, "industry": item.industry, "segment": item.segment} for item in db.scalars(statement)]


def get_recent_orders(db: Session, user: User, customer_id: str, limit: int = 5) -> list[dict[str, Any]]:
    assert_customer_access(user, customer_id)
    rows = db.scalars(select(Order).where(Order.customer_id == customer_id).order_by(Order.order_date.desc()).limit(min(max(limit, 1), 20))).all()
    return [{"id": row.id, "date": row.order_date.isoformat(), "promised_date": row.promised_date.isoformat(), "status": row.status, "total": money(row.total), "summary": row.item_summary} for row in rows]


def get_open_invoices(db: Session, user: User, customer_id: str | None = None) -> list[dict[str, Any]]:
    query = select(Invoice).where(Invoice.status != "Paid")
    if customer_id:
        assert_customer_access(user, customer_id)
        query = query.where(Invoice.customer_id == customer_id)
    else:
        allowed = permitted_customer_ids(user)
        if allowed is not None:
            query = query.where(Invoice.customer_id.in_(allowed))
    rows = db.scalars(query.order_by(Invoice.due_date).limit(30)).all()
    return [{"id": row.id, "customer_id": row.customer_id, "status": row.status, "due_date": row.due_date.isoformat(), "remaining": money(row.amount - row.paid_amount)} for row in rows]


def get_delivery_exceptions(db: Session, user: User, customer_id: str | None = None) -> list[dict[str, Any]]:
    query = select(Order).where(Order.status.in_(["Delayed", "Backordered", "Delivered late"]))
    if customer_id:
        assert_customer_access(user, customer_id)
        query = query.where(Order.customer_id == customer_id)
    else:
        allowed = permitted_customer_ids(user)
        if allowed is not None:
            query = query.where(Order.customer_id.in_(allowed))
    rows = db.scalars(query.order_by(Order.promised_date).limit(20)).all()
    return [{"id": row.id, "customer_id": row.customer_id, "status": row.status, "promised_date": row.promised_date.isoformat(), "summary": row.item_summary, "total": money(row.total)} for row in rows]


def get_inventory_status(db: Session, user: User, query: str = "") -> list[dict[str, Any]]:
    statement = select(InventoryItem)
    if query:
        statement = statement.where(or_(InventoryItem.product_name.ilike(f"%{query}%"), InventoryItem.sku.ilike(f"%{query}%"), InventoryItem.category.ilike(f"%{query}%")))
    rows = db.scalars(statement.order_by(InventoryItem.on_hand - InventoryItem.allocated).limit(20)).all()
    return [{"sku": row.sku, "product": row.product_name, "warehouse": row.warehouse, "available": row.on_hand - row.allocated, "reorder_point": row.reorder_point, "lead_time_days": row.lead_time_days, "risk": "high" if row.on_hand - row.allocated < row.reorder_point else "normal"} for row in rows]


def get_service_cases(db: Session, user: User, customer_id: str) -> list[dict[str, Any]]:
    assert_customer_access(user, customer_id)
    rows = db.scalars(select(ServiceCase).where(ServiceCase.customer_id == customer_id).order_by(ServiceCase.opened_date.desc()).limit(20)).all()
    return [{"id": row.id, "priority": row.priority, "status": row.status, "issue_type": row.issue_type, "summary": row.summary, "opened_date": row.opened_date.isoformat()} for row in rows]


def search_documents(db: Session, user: User, query: str, query_embedding: list[float] | None = None) -> list[dict[str, Any]]:
    roles = user.role
    base = select(DocumentChunk, Document).join(Document, Document.id == DocumentChunk.document_id).where(
        Document.status == "current", Document.allowed_roles.ilike(f"%{roles}%")
    )
    if query_embedding:
        base = base.where(DocumentChunk.embedding.is_not(None)).order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(5)
        rows = db.execute(base).all()
    else:
        words = [word for word in re.findall(r"[a-z0-9]+", query.lower()) if len(word) > 3]
        filters = [DocumentChunk.content.ilike(f"%{word}%") for word in words[:8]]
        if filters:
            base = base.where(or_(*filters))
        rows = db.execute(base.order_by(Document.effective_date.desc()).limit(8)).all()
    return [{"document_id": doc.id, "title": doc.title, "version": doc.version, "section": chunk.section, "page": chunk.page, "content": chunk.content, "effective_date": doc.effective_date.isoformat()} for chunk, doc in rows]


def get_business_metrics(db: Session, user: User) -> dict[str, Any]:
    return dashboard(db, user)["kpis"]


def audit(db: Session, user: User, event_type: str, request_summary: str, tools: list[str], sources: list[str], outcome: str, latency_ms: int, mode: str) -> None:
    db.add(AuditEvent(
        created_at=datetime.now(timezone.utc),
        user_email=user.email,
        user_role=user.role,
        event_type=event_type,
        request_summary=request_summary[:1200],
        tools_used=",".join(tools),
        sources_used=",".join(sources),
        outcome=outcome,
        latency_ms=latency_ms,
        mode=mode,
    ))
    db.commit()


def list_audit_events(db: Session, user: User) -> list[dict[str, Any]]:
    query = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100)
    if user.role != "ai_administrator":
        query = query.where(AuditEvent.user_email == user.email)
    rows = db.scalars(query).all()
    return [{"id": row.id, "created_at": row.created_at.isoformat(), "user_email": row.user_email, "role": row.user_role, "event_type": row.event_type, "request_summary": row.request_summary, "tools_used": [item for item in row.tools_used.split(",") if item], "sources_used": [item for item in row.sources_used.split(",") if item], "outcome": row.outcome, "latency_ms": row.latency_ms, "mode": row.mode} for row in rows]


def source_ids(result: Any) -> list[str]:
    found: list[str] = []
    if isinstance(result, list):
        for item in result:
            found.extend(source_ids(item))
    elif isinstance(result, dict):
        for key in ("id", "source_id", "document_id", "customer_id", "sku"):
            if key in result and str(result[key]) not in found:
                found.append(str(result[key]))
    return found[:30]
