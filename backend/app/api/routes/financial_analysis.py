from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ...services.financial_analysis import FinancialAnalysisService
from ...models import (
    CreditScore, CreditScoreCreate, CreditScoreUpdate,
    CreditHistory, CreditHistoryCreate, CreditHistoryUpdate,
    FinancialReport, FinancialReportCreate, FinancialReportUpdate,
    RiskAnalysis, RiskAnalysisCreate, RiskAnalysisUpdate
)
from ..deps import get_financial_analysis_service, get_current_user
from ...core.auth import RoleGuard

router = APIRouter()

# Credit Score Endpoints
@router.post("/credit-scores", response_model=CreditScore)
async def create_credit_score(
    score: CreditScoreCreate,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Create a new credit score"""
    return await financial_service.create_credit_score(score)

@router.get("/credit-scores/{client_id}", response_model=CreditScore)
async def get_client_credit_score(
    client_id: str,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Get the latest credit score for a client"""
    score = await financial_service.get_client_credit_score(client_id)
    if not score:
        raise HTTPException(status_code=404, detail="Credit score not found")
    return score

@router.post("/credit-scores/{client_id}/calculate", response_model=Dict[str, Any])
async def calculate_credit_score(
    client_id: str,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Calculate a new credit score for a client"""
    return await financial_service.calculate_credit_score(client_id)

# Credit History Endpoints
@router.post("/credit-histories", response_model=CreditHistory)
async def create_credit_history(
    history: CreditHistoryCreate,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Create a new credit history entry"""
    return await financial_service.create_credit_history(history)

# Financial Report Endpoints
@router.post("/financial-reports", response_model=FinancialReport)
async def create_financial_report(
    report: FinancialReportCreate,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Create a new financial report"""
    return await financial_service.create_financial_report(report)

# Risk Analysis Endpoints
@router.post("/risk-analyses", response_model=RiskAnalysis)
async def create_risk_analysis(
    analysis: RiskAnalysisCreate,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Create a new risk analysis"""
    return await financial_service.create_risk_analysis(analysis)

@router.get("/loans/{loan_id}/risk-analysis", response_model=RiskAnalysis)
async def get_loan_risk_analysis(
    loan_id: str,
    financial_service: FinancialAnalysisService = Depends(get_financial_analysis_service),
    current_user = Depends(get_current_user)
):
    """Get the latest risk analysis for a loan"""
    analysis = await financial_service.get_loan_risk_analysis(loan_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Risk analysis not found")
    return analysis 