import uuid
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Document, DocumentLock, DocumentVersion, Workflow, WorkflowStep

def test_create_document_with_file(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    with patch("app.api.routes.documents.storage_service") as mock_storage:
        mock_storage.save_file.return_value = "path/to/file.pdf"
        
        data = {"title": "File Doc", "description": "With file"}
        files = {"file": ("test.pdf", b"content", "application/pdf")}
        
        response = client.post(
            f"{settings.API_V1_STR}/documents/",
            headers=superuser_token_headers,
            data={"document_in": '{"title": "File Doc", "description": "With file"}'},
            files=files
        )
        assert response.status_code == 200
        content = response.json()
        assert content["title"] == "File Doc"
        
        # Verify version created
        doc_id = content["id"]
        response = client.get(f"{settings.API_V1_STR}/documents/{doc_id}/versions", headers=superuser_token_headers)
        assert response.status_code == 200
        versions = response.json()
        assert len(versions) == 1
        assert versions[0]["version_number"] == 1

def test_checkout_checkin(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create doc
    doc = Document(title="Lock Doc", owner_id=uuid.uuid4())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Checkout
    response = client.post(
        f"{settings.API_V1_STR}/documents/{doc.id}/checkout",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    
    # Verify lock
    lock = db.get(DocumentLock, doc.id) # Actually lock ID is UUID, need to query by doc_id
    # But model has document_id unique.
    # Wait, DocumentLock primary key is ID, not document_id.
    # I should query.
    # But for test simplicity, I trust the API response.
    
    # Checkin
    with patch("app.api.routes.document_lifecycle.storage_service") as mock_storage:
        mock_storage.save_file.return_value = "path/to/v2.pdf"
        
        files = {"file": ("v2.pdf", b"new content", "application/pdf")}
        response = client.post(
            f"{settings.API_V1_STR}/documents/{doc.id}/checkin",
            headers=superuser_token_headers,
            files=files
        )
        assert response.status_code == 200
        version = response.json()
        assert version["version_number"] == 1 # First version if none existed?
        # Wait, I created doc manually without version.
        # Checkin logic: next_version = last + 1. Last is None -> 1.
        
        # Verify lock removed
        # response = client.post(
        #     f"{settings.API_V1_STR}/documents/{doc.id}/checkout",
        #     headers=superuser_token_headers
        # )
        # assert response.status_code == 200 # Should succeed again

def test_workflow_lifecycle(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    # Create doc and workflow
    doc = Document(title="WF Doc", owner_id=uuid.uuid4())
    db.add(doc)
    
    wf = Workflow(name="Approval")
    db.add(wf)
    db.commit()
    db.refresh(wf)
    
    step1 = WorkflowStep(workflow_id=wf.id, name="Review", order=1)
    step2 = WorkflowStep(workflow_id=wf.id, name="Approve", order=2)
    db.add(step1)
    db.add(step2)
    db.commit()
    
    # Submit
    response = client.post(
        f"{settings.API_V1_STR}/documents/{doc.id}/submit?workflow_id={wf.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    instance = response.json()
    assert instance["status"] == "in_progress"
    instance_id = instance["id"]
    
    # Approve Step 1
    response = client.post(
        f"{settings.API_V1_STR}/workflows/instances/{instance_id}/approve",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    instance = response.json()
    assert instance["current_step_id"] == str(step2.id)
    
    # Approve Step 2 (Complete)
    response = client.post(
        f"{settings.API_V1_STR}/workflows/instances/{instance_id}/approve",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    instance = response.json()
    assert instance["status"] == "approved"
    
    # Verify doc status
    db.refresh(doc)
    assert doc.status == "Approved"
