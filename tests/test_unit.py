import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from worker import process_message

test_data = [
    ("valid_data", {"user_id": 1, "title": "Ok", "content": "All good", "email": "a@b.com"}),
    ("missing_email", {"user_id": 1, "title": "No Email", "content": "Forgot email"}),
    ("missing_user_id", {"title": "No User", "content": "Forgot ID", "email": "a@b.com"}),
    ("invalid_json", "это не json вовсе"),
    ("empty_dict", {}),
]

@pytest.mark.parametrize("name, payload", test_data)
@pytest.mark.asyncio
async def test_should_not_crash(name, payload):
    mock_msg = MagicMock()
    if isinstance(payload, dict):
        mock_msg.body = json.dumps(payload).encode()
    else:
        mock_msg.body = str(payload).encode()

    # Настройка контекстного менеджера RabbitMQ
    cms_mock = MagicMock()
    cms_mock.__aenter__ = AsyncMock(return_value=None)
    cms_mock.__aexit__ = AsyncMock(return_value=None)
    mock_msg.process = MagicMock(return_value=cms_mock)

    with patch("worker.SessionLocal") as mock_db, \
        patch("worker.send_email", new_callable=AsyncMock):
        
        await process_message(mock_msg)