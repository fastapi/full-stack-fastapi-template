import time
from typing import Dict

import kombu
from fastapi.testclient import TestClient

from app.core.config import settings


def test_celery_worker_test(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {"msg": "test"}
    retries = 1
    r = None
    while (retries + 1) > 0:
        try:
            r = client.post(
                f"{settings.API_V1_STR}/utils/test-celery/",
                json=data,
                headers=superuser_token_headers,
            )
        except kombu.exceptions.OperationalError:
            # This can happen right when the stack starts,
            # give celery a couple seconds
            time.sleep(5)
            retries -= 1
            continue
        break

    assert r
    response = r.json()
    assert response["msg"] == "Word received"
