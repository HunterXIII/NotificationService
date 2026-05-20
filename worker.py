import asyncio
import json
import os
import time
import uuid

import aio_pika
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from app.database import SessionLocal
from app.models import Notification
from app.observability.context import correlation_id_var
from app.observability.logging import get_logger, setup_logging
from config import settings
from email_notification import send_email

setup_logging(service_name="notification-worker")
logger = get_logger(__name__)

WORKER_MESSAGES_TOTAL = Counter(
    "worker_messages_total",
    "Total processed messages by result",
    ["result"],
)
WORKER_MESSAGE_PROCESSING_SECONDS = Histogram(
    "worker_message_processing_seconds",
    "Message processing duration in seconds",
)
WORKER_MESSAGES_IN_PROGRESS = Gauge(
    "worker_messages_in_progress",
    "Current number of messages being processed",
)
WORKER_DB_OPERATIONS_TOTAL = Counter(
    "worker_db_operations_total",
    "Database write operations by result",
    ["result"],
)
WORKER_EMAIL_SEND_TOTAL = Counter(
    "worker_email_send_total",
    "Email send attempts by result",
    ["result"],
)
WORKER_METRICS_PORT = int(os.getenv("WORKER_METRICS_PORT", "9108"))


def _extract_correlation_id(message: aio_pika.IncomingMessage, data: dict | None) -> str:
    if message.headers and message.headers.get("correlation_id"):
        return str(message.headers["correlation_id"])
    if data and data.get("correlation_id"):
        return str(data["correlation_id"])
    return str(uuid.uuid4())


async def process_message(message: aio_pika.IncomingMessage):
    started_at = time.perf_counter()
    result = "success"
    WORKER_MESSAGES_IN_PROGRESS.inc()
    try:
        async with message.process():
            data = None
            try:
                data = json.loads(message.body)
            except (json.JSONDecodeError, TypeError):
                result = "invalid_json"
                correlation_id = _extract_correlation_id(message, None)
                token = correlation_id_var.set(correlation_id)
                try:
                    logger.error(
                        "invalid_json",
                        body=message.body.decode(errors="replace"),
                    )
                finally:
                    correlation_id_var.reset(token)
                return

            correlation_id = _extract_correlation_id(message, data)
            token = correlation_id_var.set(correlation_id)
            try:
                required_fields = ["user_id", "title", "content", "email"]
                missing = [field for field in required_fields if field not in data]

                if missing:
                    result = "validation_error"
                    logger.error("missing_fields", missing=missing, data=data)
                    return

                db = SessionLocal()
                try:
                    notification = Notification(
                        user_id=data["user_id"],
                        title=data["title"],
                        content=data["content"],
                    )

                    db.add(notification)
                    db.commit()
                    WORKER_DB_OPERATIONS_TOTAL.labels(result="success").inc()
                    logger.info("notification_saved", user_id=data["user_id"])

                except Exception as e:
                    result = "db_error"
                    db.rollback()
                    WORKER_DB_OPERATIONS_TOTAL.labels(result="error").inc()
                    logger.exception("database_error", error=str(e))
                    raise

                finally:
                    db.close()

                try:
                    await send_email(
                        data["email"],
                        data["title"],
                        data["content"],
                    )
                    WORKER_EMAIL_SEND_TOTAL.labels(result="success").inc()
                    logger.info("email_sent", email=data["email"])
                except Exception as e:
                    result = "email_error"
                    WORKER_EMAIL_SEND_TOTAL.labels(result="error").inc()
                    logger.error("email_send_failed", email=data["email"], error=str(e))

                logger.info("message_processed")
            finally:
                correlation_id_var.reset(token)
    finally:
        WORKER_MESSAGE_PROCESSING_SECONDS.observe(time.perf_counter() - started_at)
        WORKER_MESSAGES_TOTAL.labels(result=result).inc()
        WORKER_MESSAGES_IN_PROGRESS.dec()


async def main():
    start_http_server(WORKER_METRICS_PORT, addr="0.0.0.0")
    logger.info("metrics_server_started", port=WORKER_METRICS_PORT)

    amqp_url = (
        f"amqp://{settings.RABBITMQ_USER}:"
        f"{settings.RABBITMQ_PASSWORD}@"
        f"{settings.RABBITMQ_HOST}/"
    )
    logger.info("connecting_rabbitmq", host=settings.RABBITMQ_HOST)
    connection = await aio_pika.connect_robust(amqp_url)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue("notifications", durable=True)
        logger.info("consumer_started", queue="notifications")

        await queue.consume(process_message)

        await asyncio.Future()


if __name__ == "__main__":
    logger.info("worker_starting")
    asyncio.run(main())
