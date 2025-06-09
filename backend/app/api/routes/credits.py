from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...services.credits import CreditService
from ...models import (
    CreditRequest, CreditRequestCreate, CreditRequestUpdate,
    Loan, LoanCreate, LoanUpdate,
    Payment, PaymentCreate, PaymentUpdate,
    Guarantee, GuaranteeCreate, GuaranteeUpdate
)
from ..deps import get_credit_service, get_current_user
from ...core.auth import RoleGuard

router = APIRouter()

# Credit Request Endpoints
@router.post("/credit-requests", response_model=CreditRequest)
async def create_credit_request(
    request: CreditRequestCreate,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Create a new credit request"""
    return await credit_service.create_credit_request(request)

@router.put("/credit-requests/{request_id}", response_model=CreditRequest)
async def update_credit_request(
    request_id: str,
    update: CreditRequestUpdate,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Update a credit request"""
    return await credit_service.update_credit_request(request_id, update)

@router.get("/credit-requests/{request_id}", response_model=CreditRequest)
async def get_credit_request(
    request_id: str,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Get a credit request by ID"""
    return await credit_service.get_credit_request(request_id)

# Loan Endpoints
@router.post("/loans", response_model=Loan)
async def create_loan(
    loan: LoanCreate,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Create a new loan"""
    return await credit_service.create_loan(loan)

@router.put("/loans/{loan_id}", response_model=Loan)
async def update_loan(
    loan_id: str,
    update: LoanUpdate,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Update a loan"""
    return await credit_service.update_loan(loan_id, update)

# Payment Endpoints
@router.post("/payments", response_model=Payment)
async def create_payment(
    payment: PaymentCreate,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Create a new payment"""
    return await credit_service.create_payment(payment)

@router.get("/loans/{loan_id}/payments", response_model=List[Payment])
async def get_loan_payments(
    loan_id: str,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Get all payments for a loan"""
    return await credit_service.get_loan_payments(loan_id)

# Guarantee Endpoints
@router.post("/guarantees", response_model=Guarantee)
async def create_guarantee(
    guarantee: GuaranteeCreate,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Create a new guarantee"""
    return await credit_service.create_guarantee(guarantee)

@router.get("/loans/{loan_id}/guarantees", response_model=List[Guarantee])
async def get_loan_guarantees(
    loan_id: str,
    credit_service: CreditService = Depends(get_credit_service),
    current_user = Depends(get_current_user)
):
    """Get all guarantees for a loan"""
    return await credit_service.get_loan_guarantees(loan_id) 