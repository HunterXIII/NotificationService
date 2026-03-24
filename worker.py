import asyncio
import json
import aio_pika
from app.models import Notification
from app.database import SessionLocal
from email_notification import send_email
from config import settings

async def process_message(message: aio_pika.IncomingMessage):
    '''
        Example: 
        {
            "user_id": 1,
            "title": "Создан проект", 
            "content": 'Проект "TaskManager" успешно создан'
            
            "email": "volkraftroman@gmail.com" ?? 
        }
    '''


    async with message.process():

        data = json.loads(message.body)

        db = SessionLocal()

        try:
            notification = Notification(
                user_id=data["user_id"],
                title=data["title"],
                content=data["content"]
            )

            db.add(notification)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        await send_email(
            data["email"],
            data["title"],
            data["content"]
        )

        print("Notification saved:", data)


async def main():
    amqp_url = (
        f"amqp://{settings.RABBITMQ_USER}:"
        f"{settings.RABBITMQ_PASSWORD}@"
        f"{settings.RABBITMQ_HOST}/"
    )
    connection = await aio_pika.connect_robust(amqp_url)  # соединение с RabbitMQ
    
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(
            "notifications", durable=True
        )
        print("Starting consuming")

        
        await queue.consume(process_message) 

        await asyncio.Future()


if __name__ == "__main__":
    print("Starting queue worker")
    asyncio.run(main())