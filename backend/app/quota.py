from datetime import datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import get_settings
from .models import DailyAiUsage, User


QUOTA_LOCK_ID = 26101475


def daily_quota_status(db: Session, user: User) -> dict[str, Any]:
    settings = get_settings()
    today = datetime.now(timezone.utc).date()
    user_used = db.scalar(
        select(DailyAiUsage.request_count).where(
            DailyAiUsage.usage_date == today,
            DailyAiUsage.user_email == user.email,
        )
    ) or 0
    global_used = db.scalar(
        select(func.coalesce(func.sum(DailyAiUsage.request_count), 0)).where(
            DailyAiUsage.usage_date == today
        )
    ) or 0
    user_limit = max(settings.ai_daily_user_quota, 0)
    global_limit = max(settings.ai_daily_global_quota, 0)
    reset_at = datetime.combine(today + timedelta(days=1), time.min, tzinfo=timezone.utc)
    return {
        "user_limit": user_limit,
        "user_used": int(user_used),
        "user_remaining": max(user_limit - int(user_used), 0),
        "global_limit": global_limit,
        "global_used": int(global_used),
        "global_remaining": max(global_limit - int(global_used), 0),
        "available": int(user_used) < user_limit and int(global_used) < global_limit,
        "reset_at": reset_at.isoformat().replace("+00:00", "Z"),
    }


def consume_daily_ai_quota(db: Session, user: User) -> dict[str, Any]:
    """Atomically reserve one model-assisted request across app instances."""
    db.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"), {"lock_id": QUOTA_LOCK_ID})
    status = daily_quota_status(db, user)
    if not status["available"]:
        db.commit()
        return {**status, "allowed": False}

    today = datetime.now(timezone.utc).date()
    row = db.scalar(
        select(DailyAiUsage).where(
            DailyAiUsage.usage_date == today,
            DailyAiUsage.user_email == user.email,
        )
    )
    if row:
        row.request_count += 1
    else:
        db.add(DailyAiUsage(usage_date=today, user_email=user.email, request_count=1))
    db.commit()
    return {**daily_quota_status(db, user), "allowed": True}
