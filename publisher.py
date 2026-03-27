import asyncio
import json
import os
import aio_pika

async def publish_notification(data: dict):

    '''
        Example: 
        {
            "user_id": 1,
            "title": "Создан проект", 
            "content": 'Проект "TaskManager" успешно создан'
            
            "email": "volkraftroman@gmail.com" ??
        }
    '''

    amqp_url = (
        f"amqp://{os.getenv("RABBITMQ_USER")}:"
        f"{os.getenv("RABBITMQ_PASSWORD")}@"
        f"{os.getenv("RABBITMQ_HOST")}/"
    )
    connection = await aio_pika.connect_robust(
        amqp_url
    )

    async with connection:

        channel = await connection.channel()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(data).encode()
            ),
            routing_key="notifications"
        )


async def main():

    await publish_notification({"user_id": 5, "title": "Смена пароля", "content": 'Был изменён пароль', "email": "volkraftroman@gmail.com"})

    print("Message sent")


if __name__ == "__main__":
    asyncio.run(main())