import os
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Optional configuration, e.g., task serialization, timezone
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
)

# Auto-discover tasks in app.tasks
celery_app.autodiscover_tasks(["app"])
