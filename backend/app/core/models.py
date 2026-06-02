from datetime import datetime, timezone

from sqlalchemy import Column, DateTime

from app.core.database import Base


def _utcnow() -> datetime:
    """替代已弃用的 datetime.utcnow()"""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """统一时间戳基类"""

    created_at = Column(DateTime, default=_utcnow, nullable=False, comment="创建时间")
    updated_at = Column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False, comment="更新时间"
    )
