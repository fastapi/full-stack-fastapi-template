import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Document, DocumentWorkflowInstance, Workflow, WorkflowAction, 
    WorkflowCreate, WorkflowRead, WorkflowUpdate, 
    WorkflowStep, WorkflowStepCreate, WorkflowStepRead
)

router = APIRouter()

@router.post("/", response_model=WorkflowRead)
def create_workflow(
    *, session: SessionDep, current_user: CurrentUser, workflow_in: WorkflowCreate
) -> Any:
    """
    Create new workflow.
    """
    workflow = Workflow.model_validate(workflow_in)
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow

@router.get("/", response_model=list[WorkflowRead])
def read_workflows(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve workflows.
    """
    statement = select(Workflow).offset(skip).limit(limit)
    workflows = session.exec(statement).all()
    return workflows

@router.post("/{id}/steps", response_model=WorkflowStepRead)
def create_workflow_step(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, step_in: WorkflowStepCreate
) -> Any:
    """
    Add a step to a workflow.
    """
    workflow = session.get(Workflow, id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    step = WorkflowStep.model_validate(step_in, update={"workflow_id": id})
    session.add(step)
    session.commit()
    session.refresh(step)
    return step

@router.post("/instances/{id}/approve", response_model=DocumentWorkflowInstance)
def approve_workflow_step(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Approve current step of a workflow instance.
    """
    instance = session.get(DocumentWorkflowInstance, id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
        
    if instance.status != "in_progress":
        raise HTTPException(status_code=400, detail="Workflow is not in progress")
        
    current_step = session.get(WorkflowStep, instance.current_step_id)
    if not current_step:
        raise HTTPException(status_code=404, detail="Current step not found")
        
    # Check permissions (mocked: check if user has role)
    # if current_step.approver_role and current_step.approver_role not in current_user.roles:
    #     raise HTTPException(status_code=403, detail="Not authorized to approve this step")
        
    # Record action
    action = WorkflowAction(
        workflow_instance_id=id,
        step_id=current_step.id,
        actor_id=current_user.id,
        action="approve"
    )
    session.add(action)
    
    # Find next step
    next_step = session.exec(
        select(WorkflowStep)
        .where(WorkflowStep.workflow_id == instance.workflow_id)
        .where(WorkflowStep.order > current_step.order)
        .order_by(WorkflowStep.order)
    ).first()
    
    if next_step:
        instance.current_step_id = next_step.id
    else:
        instance.status = "approved"
        instance.completed_at = datetime.utcnow()
        instance.current_step_id = None
        
        # Update document status
        document = session.get(Document, instance.document_id)
        if document:
            document.status = "Approved"
            session.add(document)
            
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance

@router.post("/instances/{id}/reject", response_model=DocumentWorkflowInstance)
def reject_workflow_step(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Reject current step of a workflow instance.
    """
    instance = session.get(DocumentWorkflowInstance, id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
        
    if instance.status != "in_progress":
        raise HTTPException(status_code=400, detail="Workflow is not in progress")
        
    current_step = session.get(WorkflowStep, instance.current_step_id)
    
    # Record action
    action = WorkflowAction(
        workflow_instance_id=id,
        step_id=current_step.id if current_step else None, # Should exist
        actor_id=current_user.id,
        action="reject"
    )
    session.add(action)
    
    # Mark as rejected
    instance.status = "rejected"
    instance.completed_at = datetime.utcnow()
    
    # Update document status
    document = session.get(Document, instance.document_id)
    if document:
        document.status = "Rejected"
        session.add(document)
        
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance
