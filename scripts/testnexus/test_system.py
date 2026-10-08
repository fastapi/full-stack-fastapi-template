"""Verify the live frontend/API/database path against a disposable deployment."""
import os
import uuid

import httpx


def test_live_application_item_lifecycle():
    """Authenticate over HTTP, persist an item, read it, and remove our own data."""
    with httpx.Client(base_url=os.environ['TESTNEXUS_BASE_URL'], timeout=20) as client:
        response = client.get('/api/v1/utils/health-check/')
        assert response.status_code == 200
        assert response.json() is True
        frontend = client.get('/')
        assert frontend.status_code == 200
        assert '<html' in frontend.text.lower()
        login = client.post('/api/v1/login/access-token', data={
            'username': os.environ['FIRST_SUPERUSER'],
            'password': os.environ['FIRST_SUPERUSER_PASSWORD'],
        })
        assert login.status_code == 200
        headers = {'Authorization': 'Bearer ' + login.json()['access_token']}
        title = 'TestNexus ' + uuid.uuid4().hex
        created = client.post('/api/v1/items/', headers=headers, json={
            'title': title, 'description': 'Disposable system verification',
        })
        assert created.status_code == 200
        item_id = created.json()['id']
        try:
            read = client.get('/api/v1/items/' + item_id, headers=headers)
            assert read.status_code == 200
            assert read.json()['title'] == title
        finally:
            deleted = client.delete('/api/v1/items/' + item_id, headers=headers)
            assert deleted.status_code == 200
        assert client.get('/api/v1/items/' + item_id, headers=headers).status_code == 404
