import asyncio
import json
import pytest
import aio_pika
from unittest.mock import patch, AsyncMock
from sqlalchemy import text

from worker import process_message
from app.models import Notification
from config import settings

@pytest.mark.asyncio
async def test_worker_full_integration():
    queue_name = "test_notifications_queue"
    payload = {
        "user_id": 777,
        "title": "Integration Success",
        "content": "Message via RabbitMQ",
        "email": "bot@test.com"
    }

    # Мокаем отправку почты, чтобы тест не зависел от интернета
    with patch("worker.send_email", new_callable=AsyncMock) as mock_mail:
        
        # Подключаемся к RabbitMQ
        amqp_url = (
            f"amqp://{settings.RABBITMQ_USER}:"
            f"{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}/"
        )
        print("Connecting to RabbitMQ: ", amqp_url)
        connection = await aio_pika.connect_robust(amqp_url)
        
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, auto_delete=True)

            # Запускаем обработчик
            await queue.consume(process_message)

            # Отправляем сообщение
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(payload).encode()),
                routing_key=queue_name
            )

            # Ждем обработки
            await asyncio.sleep(1)

        from worker import SessionLocal
        # ПРОВЕРКА БД
        db = SessionLocal()
        # Ищем запись, которую только что создал воркер
        result = db.query(Notification).filter_by(user_id=777).first()
        
        assert result is not None
        assert result.title == "Integration Success"
        db.close()

        # ПРОВЕРКА ВЫЗОВА ПОЧТЫ
        mock_mail.assert_called_once_with("bot@test.com", "Integration Success", "Message via RabbitMQ")