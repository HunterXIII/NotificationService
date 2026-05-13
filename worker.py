import asyncio
import json
import aio_pika
from app.models import Notification
from app.database import SessionLocal
from email_notification import send_email
from config import settings

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body)
        except (json.JSONDecodeError, TypeError):
            print(f"!!! Error: Received invalid JSON: {message.body}")
            return
        
        required_fields = ["user_id", "title", "content", "email"]
        missing = [field for field in required_fields if field not in data]
        
        if missing:
            print(f"!!! Error: Missing fields {missing} in message: {data}")
            return

        db = SessionLocal()
        try:
            notification = Notification(
                user_id=data["user_id"],
                title=data["title"],
                content=data["content"]
            )

            db.add(notification)
            db.commit()
            print(f"Notification saved to DB for user {data['user_id']}")

        except Exception as e:
            db.rollback()
            print(f"!!! Database error: {e}")
            raise 

        finally:
            db.close()

        try:
            await send_email(
                data["email"],
                data["title"],
                data["content"]
            )
            print(f"Email sent to: {data['email']}")
        except Exception as e:
            print(f"Email sending failed: {e}")

        print("Message processed")


async def main():
    amqp_url = (
        f"amqp://{settings.RABBITMQ_USER}:"
        f"{settings.RABBITMQ_PASSWORD}@"
        f"{settings.RABBITMQ_HOST}/"
    )
    print("Connecting to RabbitMQ: ", amqp_url)
    connection = await aio_pika.connect_robust(amqp_url) 
    
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