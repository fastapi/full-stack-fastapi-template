from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from decimal import Decimal

from ....core.auth import get_current_user
from ....models import (
    MortgageLoan, MortgageLoanCreate, MortgageLoanUpdate,
    InvestmentLoan, InvestmentLoanCreate, InvestmentLoanUpdate
)
from ....services.loans import LoanService
from ....core.nhost import get_nhost_client
from app.api.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/loans", tags=["loans"])

# Mortgage Loan Endpoints
@router.post("/mortgage", response_model=MortgageLoan)
async def create_mortgage_loan(
    loan: MortgageLoanCreate,
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Create a new mortgage loan application"""
    if not current_user.get("role") in ["admin", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized to create mortgage loans")
    
    # Calculate LTV ratio
    ltv_ratio = await loan_service.calculate_ltv_ratio(
        property_value=loan.appraisal_value,
        loan_amount=loan.loan_amount
    )
    
    # Calculate monthly payment
    monthly_payment = await loan_service.calculate_monthly_payment(
        loan_amount=loan.loan_amount,
        interest_rate=loan.interest_rate,
        term_years=loan.term_years
    )
    
    # Create loan with calculated values
    loan_data = loan.dict()
    loan_data.update({
        "ltv_ratio": ltv_ratio,
        "monthly_payment": monthly_payment
    })
    
    return await loan_service.create_mortgage_loan(
        loan=MortgageLoanCreate(**loan_data),
        user_id=current_user["id"]
    )

@router.get("/mortgage/{loan_id}", response_model=MortgageLoan)
async def get_mortgage_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Get mortgage loan details"""
    return await loan_service.get_mortgage_loan(loan_id)

@router.put("/mortgage/{loan_id}", response_model=MortgageLoan)
async def update_mortgage_loan(
    loan_id: str,
    loan: MortgageLoanUpdate,
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Update mortgage loan details"""
    if not current_user.get("role") in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to update mortgage loans")
    
    return await loan_service.update_mortgage_loan(loan_id, loan)

# Investment Loan Endpoints
@router.post("/investment", response_model=InvestmentLoan)
async def create_investment_loan(
    loan: InvestmentLoanCreate,
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Create a new investment loan application"""
    if not current_user.get("role") in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to create investment loans")
    
    return await loan_service.create_investment_loan(
        loan=loan,
        user_id=current_user["id"]
    )

@router.get("/investment/{loan_id}", response_model=InvestmentLoan)
async def get_investment_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Get investment loan details"""
    return await loan_service.get_investment_loan(loan_id)

@router.put("/investment/{loan_id}", response_model=InvestmentLoan)
async def update_investment_loan(
    loan_id: str,
    loan: InvestmentLoanUpdate,
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Update investment loan details"""
    if not current_user.get("role") in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to update investment loans")
    
    return await loan_service.update_investment_loan(loan_id, loan)

# Risk Assessment Endpoint
@router.post("/assess-risk")
async def assess_loan_risk(
    credit_score: int = Query(..., ge=300, le=850),
    income: Decimal = Query(..., gt=0),
    debt_to_income: Decimal = Query(..., ge=0),
    ltv_ratio: Decimal = Query(..., ge=0, le=100),
    property_value: Decimal = Query(..., gt=0),
    current_user: dict = Depends(get_current_user),
    loan_service: LoanService = Depends(lambda: LoanService(get_nhost_client()))
):
    """Assess risk for a loan application"""
    if not current_user.get("role") in ["admin", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized to assess loan risk")
    
    return await loan_service.assess_risk(
        credit_score=credit_score,
        income=income,
        debt_to_income=debt_to_income,
        ltv_ratio=ltv_ratio,
        property_value=property_value
    )

@router.get("/")
async def get_loans(current_user: CurrentUser, session: SessionDep):
    """Obtener préstamos"""
    return {
        "message": "Loans endpoint",
        "user": current_user,
        "loans": []
    }

@router.post("/")
async def create_loan(current_user: CurrentUser, session: SessionDep):
    """Crear préstamo"""
    return {
        "message": "Create loan - Coming soon",
        "user": current_user
    } 