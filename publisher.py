import asyncio
import json
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

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
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

    await publish_notification({"user_id": 4, "title": "Проверка уведомления", "content": 'Проверка как отправляется уведомление', "email": "volkraftroman@gmail.com"})

    print("Message sent")


if __name__ == "__main__":
    asyncio.run(main())