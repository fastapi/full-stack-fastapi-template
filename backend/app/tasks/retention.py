import uuid
from datetime import datetime, timedelta
from sqlmodel import Session, select

from app.core.db import engine
from app.models import Document, RetentionPolicy, AuditLog
from app.services.file_storage import storage_service

async def evaluate_retention_policies():
    """
    Daily job to evaluate retention policies and mark documents for archival/disposal.
    """
    with Session(engine) as session:
        # Get all documents with retention policies
        statement = select(Document).where(Document.retention_policy_id.isnot(None))
        documents = session.exec(statement).all()
        
        for document in documents:
            policy = session.get(RetentionPolicy, document.retention_policy_id)
            if not policy:
                continue
                
            # Calculate expiry date
            expiry_date = document.created_at + timedelta(days=policy.duration_days)
            
            if datetime.utcnow() >= expiry_date:
                # Execute policy action
                if policy.action == "archive":
                    await archive_document(session, document)
                elif policy.action == "delete":
                    await dispose_document(session, document)
                    
async def archive_document(session: Session, document: Document):
    """
    Archive a document (move to Archived status).
    In production, this would move files to cold storage (S3 Glacier, etc.)
    """
    if document.status == "Archived":
        return
        
    document.status = "Archived"
    session.add(document)
    
    # Log action
    audit = AuditLog(
        document_id=document.id,
        user_id=document.owner_id,  # System action, use owner
        action="archive",
        details=f"Document archived by retention policy"
    )
    session.add(audit)
    session.commit()
    
    print(f"Archived document {document.id}")

async def dispose_document(session: Session, document: Document):
    """
    Securely dispose of a document (GDPR-compliant deletion).
    Marks document as Disposed and deletes file content.
    """
    if document.status == "Disposed":
        return
        
    # Delete all version files
    for version in document.versions:
        storage_service.delete_file(version.file_path)
        
    document.status = "Disposed"
    session.add(document)
    
    # Log action
    audit = AuditLog(
        document_id=document.id,
        user_id=document.owner_id,
        action="dispose",
        details=f"Document disposed by retention policy"
    )
    session.add(audit)
    session.commit()
    
    print(f"Disposed document {document.id}")
