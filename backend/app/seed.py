from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Contract,
    Customer,
    Document,
    DocumentChunk,
    InventoryItem,
    Invoice,
    Order,
    ServiceCase,
    User,
)
from .security import hash_password


def seed_database(db: Session) -> None:
    if db.scalar(select(User.id).limit(1)):
        return

    users = [
        User(
            email="alex@northstar.demo",
            name="Alex Morgan",
            role="account_manager",
            title="Senior Account Manager",
            password_hash=hash_password("demo123", "northstar-alex"),
            assigned_customer_ids="CUST-1001,CUST-1003,CUST-1005",
        ),
        User(
            email="priya@northstar.demo",
            name="Priya Shah",
            role="finance_analyst",
            title="Finance Analyst",
            password_hash=hash_password("demo123", "northstar-priya"),
            assigned_customer_ids="",
        ),
        User(
            email="marcus@northstar.demo",
            name="Marcus Chen",
            role="operations_manager",
            title="Distribution Operations Manager",
            password_hash=hash_password("demo123", "northstar-marcus"),
            assigned_customer_ids="",
        ),
        User(
            email="jordan@northstar.demo",
            name="Jordan Lee",
            role="executive",
            title="VP, Commercial Operations",
            password_hash=hash_password("demo123", "northstar-jordan"),
            assigned_customer_ids="",
        ),
        User(
            email="taylor@northstar.demo",
            name="Taylor Brooks",
            role="ai_administrator",
            title="AI Platform Administrator",
            password_hash=hash_password("demo123", "northstar-taylor"),
            assigned_customer_ids="",
        ),
    ]

    customers = [
        Customer(id="CUST-1001", name="Horizon Construction", industry="Commercial construction", city="Burnaby", province="BC", segment="Strategic", account_owner="Alex Morgan", since=date(2021, 3, 18), credit_limit=Decimal("175000"), health_score=72),
        Customer(id="CUST-1002", name="Pacific Forge Works", industry="Metal fabrication", city="Surrey", province="BC", segment="Enterprise", account_owner="Dana Wilson", since=date(2019, 9, 2), credit_limit=Decimal("260000"), health_score=88),
        Customer(id="CUST-1003", name="Cedar Facilities Group", industry="Facilities management", city="Vancouver", province="BC", segment="Growth", account_owner="Alex Morgan", since=date(2023, 1, 12), credit_limit=Decimal("90000"), health_score=81),
        Customer(id="CUST-1004", name="Summit Electrical Services", industry="Commercial electrical", city="Calgary", province="AB", segment="Mid-market", account_owner="Dana Wilson", since=date(2020, 6, 29), credit_limit=Decimal("120000"), health_score=64),
        Customer(id="CUST-1005", name="Bluewater Mechanical", industry="Mechanical services", city="Richmond", province="BC", segment="Growth", account_owner="Alex Morgan", since=date(2024, 2, 8), credit_limit=Decimal("70000"), health_score=91),
    ]

    orders = [
        Order(id="ORD-84217", customer_id="CUST-1001", order_date=date(2026, 9, 20), promised_date=date(2026, 9, 26), shipped_date=None, status="Delayed", total=Decimal("38740"), warehouse="Vancouver DC", item_summary="Fall protection kits and site safety supplies"),
        Order(id="ORD-84103", customer_id="CUST-1001", order_date=date(2026, 9, 8), promised_date=date(2026, 9, 13), shipped_date=date(2026, 9, 13), status="Delivered", total=Decimal("19425"), warehouse="Vancouver DC", item_summary="Cordless tools and replacement batteries"),
        Order(id="ORD-83892", customer_id="CUST-1001", order_date=date(2026, 8, 18), promised_date=date(2026, 8, 25), shipped_date=date(2026, 8, 27), status="Delivered late", total=Decimal("26110"), warehouse="Vancouver DC", item_summary="Abrasives, anchors, and cutting equipment"),
        Order(id="ORD-84244", customer_id="CUST-1002", order_date=date(2026, 9, 23), promised_date=date(2026, 10, 2), shipped_date=date(2026, 9, 30), status="Delivered", total=Decimal("72880"), warehouse="Calgary DC", item_summary="Welding consumables and respiratory protection"),
        Order(id="ORD-84261", customer_id="CUST-1003", order_date=date(2026, 9, 27), promised_date=date(2026, 10, 4), shipped_date=None, status="Processing", total=Decimal("13420"), warehouse="Vancouver DC", item_summary="Building maintenance and janitorial equipment"),
        Order(id="ORD-84088", customer_id="CUST-1004", order_date=date(2026, 9, 4), promised_date=date(2026, 9, 12), shipped_date=None, status="Backordered", total=Decimal("44830"), warehouse="Calgary DC", item_summary="Electrical testers and arc-flash PPE"),
        Order(id="ORD-84275", customer_id="CUST-1005", order_date=date(2026, 9, 29), promised_date=date(2026, 10, 5), shipped_date=date(2026, 10, 3), status="Delivered", total=Decimal("9950"), warehouse="Vancouver DC", item_summary="Pump service tools and gasket kits"),
        Order(id="ORD-83970", customer_id="CUST-1005", order_date=date(2026, 8, 28), promised_date=date(2026, 9, 4), shipped_date=date(2026, 9, 4), status="Delivered", total=Decimal("11780"), warehouse="Vancouver DC", item_summary="Valves, gauges, and maintenance supplies"),
    ]

    invoices = [
        Invoice(id="INV-61042", customer_id="CUST-1001", issued_date=date(2026, 8, 27), due_date=date(2026, 9, 26), amount=Decimal("26110"), paid_amount=Decimal("0"), status="Overdue"),
        Invoice(id="INV-61218", customer_id="CUST-1001", issued_date=date(2026, 9, 13), due_date=date(2026, 10, 13), amount=Decimal("19425"), paid_amount=Decimal("5000"), status="Open"),
        Invoice(id="INV-60901", customer_id="CUST-1002", issued_date=date(2026, 8, 10), due_date=date(2026, 9, 9), amount=Decimal("48100"), paid_amount=Decimal("48100"), status="Paid"),
        Invoice(id="INV-61281", customer_id="CUST-1002", issued_date=date(2026, 9, 30), due_date=date(2026, 10, 30), amount=Decimal("72880"), paid_amount=Decimal("0"), status="Open"),
        Invoice(id="INV-61124", customer_id="CUST-1003", issued_date=date(2026, 9, 3), due_date=date(2026, 10, 3), amount=Decimal("8290"), paid_amount=Decimal("8290"), status="Paid"),
        Invoice(id="INV-61002", customer_id="CUST-1004", issued_date=date(2026, 8, 21), due_date=date(2026, 9, 20), amount=Decimal("31850"), paid_amount=Decimal("10000"), status="Overdue"),
        Invoice(id="INV-61260", customer_id="CUST-1005", issued_date=date(2026, 9, 25), due_date=date(2026, 10, 25), amount=Decimal("11780"), paid_amount=Decimal("0"), status="Open"),
    ]

    inventory = [
        InventoryItem(sku="SAFE-FALL-220", product_name="ProGuard Fall Protection Kit", category="Safety", warehouse="Vancouver DC", on_hand=14, allocated=12, reorder_point=18, lead_time_days=16),
        InventoryItem(sku="TOOL-BATT-18V", product_name="18V High-Capacity Battery", category="Power tools", warehouse="Vancouver DC", on_hand=42, allocated=31, reorder_point=20, lead_time_days=8),
        InventoryItem(sku="ELEC-ARC-40", product_name="Arc-Flash PPE Kit 40 cal", category="Electrical safety", warehouse="Calgary DC", on_hand=7, allocated=11, reorder_point=12, lead_time_days=24),
        InventoryItem(sku="WELD-RESP-P100", product_name="P100 Welding Respirator", category="Respiratory", warehouse="Calgary DC", on_hand=66, allocated=22, reorder_point=28, lead_time_days=12),
        InventoryItem(sku="MAINT-PUMP-KIT", product_name="Industrial Pump Service Kit", category="Maintenance", warehouse="Vancouver DC", on_hand=23, allocated=8, reorder_point=10, lead_time_days=10),
        InventoryItem(sku="ABRA-CUT-125", product_name="125 mm Cutting Disc Case", category="Abrasives", warehouse="Vancouver DC", on_hand=102, allocated=74, reorder_point=40, lead_time_days=6),
    ]

    cases = [
        ServiceCase(id="CASE-1907", customer_id="CUST-1001", opened_date=date(2026, 9, 28), priority="High", status="Open", issue_type="Delivery", summary="Fall protection order has not shipped and the customer has an active project mobilization deadline."),
        ServiceCase(id="CASE-1872", customer_id="CUST-1001", opened_date=date(2026, 8, 27), priority="Medium", status="Resolved", issue_type="Late delivery", summary="Abrasives shipment arrived two days after the requested site delivery window."),
        ServiceCase(id="CASE-1914", customer_id="CUST-1004", opened_date=date(2026, 9, 30), priority="High", status="Escalated", issue_type="Backorder", summary="Arc-flash kits are below available stock and an alternate delivery plan is required."),
        ServiceCase(id="CASE-1888", customer_id="CUST-1003", opened_date=date(2026, 9, 11), priority="Low", status="Resolved", issue_type="Product information", summary="Customer requested updated maintenance documentation for a floor-care unit."),
    ]

    contracts = [
        Contract(id="CON-3011", customer_id="CUST-1001", effective_date=date(2026, 1, 1), renewal_date=date(2026, 12, 15), payment_terms_days=30, delivery_target_days=5, annual_value=Decimal("420000"), notes="Strategic account. Critical safety-product orders require same-day escalation when projected late."),
        Contract(id="CON-2984", customer_id="CUST-1002", effective_date=date(2025, 11, 1), renewal_date=date(2026, 10, 31), payment_terms_days=30, delivery_target_days=7, annual_value=Decimal("690000"), notes="Enterprise pricing schedule and quarterly usage review."),
        Contract(id="CON-3155", customer_id="CUST-1003", effective_date=date(2026, 4, 1), renewal_date=date(2027, 3, 31), payment_terms_days=30, delivery_target_days=6, annual_value=Decimal("185000"), notes="Growth account with sustainability reporting requirement."),
        Contract(id="CON-3049", customer_id="CUST-1004", effective_date=date(2026, 2, 1), renewal_date=date(2027, 1, 31), payment_terms_days=30, delivery_target_days=7, annual_value=Decimal("310000"), notes="Calgary service region with substitute-product approval required for safety equipment."),
        Contract(id="CON-3220", customer_id="CUST-1005", effective_date=date(2026, 7, 1), renewal_date=date(2027, 6, 30), payment_terms_days=30, delivery_target_days=6, annual_value=Decimal("142000"), notes="New growth account with monthly service review."),
    ]

    documents = [
        Document(id="DOC-100", title="Purchasing Approval Policy", document_type="Policy", version="3.2", status="current", effective_date=date(2026, 1, 15), allowed_roles="account_manager,finance_analyst,operations_manager,executive,ai_administrator", owner="Finance Operations"),
        Document(id="DOC-101", title="Customer Credit and Collections Standard", document_type="Policy", version="2.4", status="current", effective_date=date(2026, 4, 1), allowed_roles="finance_analyst,executive,ai_administrator", owner="Corporate Finance"),
        Document(id="DOC-102", title="Delivery Exception Escalation Guide", document_type="Procedure", version="4.0", status="current", effective_date=date(2026, 6, 10), allowed_roles="account_manager,operations_manager,executive,ai_administrator", owner="Distribution Operations"),
        Document(id="DOC-103", title="Responsible AI Use Standard", document_type="Standard", version="1.1", status="current", effective_date=date(2026, 8, 1), allowed_roles="account_manager,finance_analyst,operations_manager,executive,ai_administrator", owner="Technology Risk"),
        Document(id="DOC-104", title="Purchasing Approval Policy", document_type="Policy", version="2.9", status="superseded", effective_date=date(2025, 2, 1), allowed_roles="account_manager,finance_analyst,operations_manager,executive,ai_administrator", owner="Finance Operations"),
    ]

    chunks = [
        DocumentChunk(document_id="DOC-100", section="Approval thresholds", page=3, content="Purchases up to $10,000 require a department manager. Purchases above $10,000 and up to $25,000 require a director. Purchases above $25,000 require a vice-president and Finance review."),
        DocumentChunk(document_id="DOC-100", section="Emergency purchases", page=4, content="Emergency purchases may proceed only when safety or operational continuity is at immediate risk. The requester must document the reason and obtain retrospective approval within one business day."),
        DocumentChunk(document_id="DOC-101", section="Past-due account handling", page=5, content="Invoices more than 30 days past due require account-manager notification. New discretionary orders may be held when exposure exceeds the approved credit limit or collection risk is high."),
        DocumentChunk(document_id="DOC-101", section="Customer communication", page=6, content="Collection discussions must use verified invoice balances and documented commitments. Employees must not disclose another customer's financial information."),
        DocumentChunk(document_id="DOC-102", section="Critical product delays", page=2, content="A delay involving safety equipment or a contractual milestone must be escalated the same business day to Distribution Operations and the account owner."),
        DocumentChunk(document_id="DOC-102", section="Customer notification", page=3, content="The account owner must receive a confirmed recovery plan before promising a revised date. Where no confirmed date exists, the customer must be told that timing remains under investigation."),
        DocumentChunk(document_id="DOC-103", section="Permitted use", page=2, content="AI may summarize, retrieve, compare, and recommend using approved information. Phase 1 systems must not change business records or execute financial transactions."),
        DocumentChunk(document_id="DOC-103", section="Evidence and human oversight", page=4, content="Material business claims require traceable evidence. Users must review recommendations before acting, and the system must state important limitations or missing information."),
        DocumentChunk(document_id="DOC-104", section="Approval thresholds", page=3, content="Superseded: Purchases above $20,000 require vice-president approval. This version must not be used for current decisions."),
    ]

    db.add_all(users + customers + orders + invoices + inventory + cases + contracts + documents)
    db.flush()
    db.add_all(chunks)
    db.commit()

