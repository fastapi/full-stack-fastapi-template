from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from ..core.nhost import NhostClient
from ..models import MortgageLoan, MortgageLoanCreate, MortgageLoanUpdate
from ..models import InvestmentLoan, InvestmentLoanCreate, InvestmentLoanUpdate

class LoanService:
    def __init__(self, nhost_client: NhostClient):
        self.nhost = nhost_client

    # Mortgage Loans
    async def create_mortgage_loan(self, loan: MortgageLoanCreate, user_id: str) -> MortgageLoan:
        query = """
        mutation CreateMortgageLoan($loan: mortgage_loans_insert_input!) {
            insert_mortgage_loans_one(object: $loan) {
                id
                property_id
                loan_amount
                interest_rate
                term_years
                ltv_ratio
                monthly_payment
                insurance_required
                insurance_provider
                insurance_policy_number
                insurance_coverage
                appraisal_value
                appraisal_date
                appraisal_company
                legal_documents
                status
                created_at
                updated_at
                created_by
                approved_by
                approval_date
            }
        }
        """
        variables = {
            "loan": {
                **loan.dict(),
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        result = await self.nhost.graphql(query, variables)
        return MortgageLoan(**result["insert_mortgage_loans_one"])

    async def update_mortgage_loan(self, loan_id: str, loan: MortgageLoanUpdate) -> MortgageLoan:
        query = """
        mutation UpdateMortgageLoan($id: uuid!, $loan: mortgage_loans_set_input!) {
            update_mortgage_loans_by_pk(pk_columns: {id: $id}, _set: $loan) {
                id
                property_id
                loan_amount
                interest_rate
                term_years
                ltv_ratio
                monthly_payment
                insurance_required
                insurance_provider
                insurance_policy_number
                insurance_coverage
                appraisal_value
                appraisal_date
                appraisal_company
                legal_documents
                status
                created_at
                updated_at
                created_by
                approved_by
                approval_date
            }
        }
        """
        variables = {
            "id": loan_id,
            "loan": {
                **loan.dict(exclude_unset=True),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        result = await self.nhost.graphql(query, variables)
        return MortgageLoan(**result["update_mortgage_loans_by_pk"])

    async def get_mortgage_loan(self, loan_id: str) -> MortgageLoan:
        query = """
        query GetMortgageLoan($id: uuid!) {
            mortgage_loans_by_pk(id: $id) {
                id
                property_id
                loan_amount
                interest_rate
                term_years
                ltv_ratio
                monthly_payment
                insurance_required
                insurance_provider
                insurance_policy_number
                insurance_coverage
                appraisal_value
                appraisal_date
                appraisal_company
                legal_documents
                status
                created_at
                updated_at
                created_by
                approved_by
                approval_date
            }
        }
        """
        result = await self.nhost.graphql(query, {"id": loan_id})
        return MortgageLoan(**result["mortgage_loans_by_pk"])

    # Investment Loans
    async def create_investment_loan(self, loan: InvestmentLoanCreate, user_id: str) -> InvestmentLoan:
        query = """
        mutation CreateInvestmentLoan($loan: investment_loans_insert_input!) {
            insert_investment_loans_one(object: $loan) {
                id
                project_id
                loan_amount
                interest_rate
                term_years
                expected_roi
                business_plan
                collateral_type
                collateral_value
                collateral_documents
                risk_assessment
                status
                created_at
                updated_at
                created_by
                approved_by
                approval_date
            }
        }
        """
        variables = {
            "loan": {
                **loan.dict(),
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        result = await self.nhost.graphql(query, variables)
        return InvestmentLoan(**result["insert_investment_loans_one"])

    async def update_investment_loan(self, loan_id: str, loan: InvestmentLoanUpdate) -> InvestmentLoan:
        query = """
        mutation UpdateInvestmentLoan($id: uuid!, $loan: investment_loans_set_input!) {
            update_investment_loans_by_pk(pk_columns: {id: $id}, _set: $loan) {
                id
                project_id
                loan_amount
                interest_rate
                term_years
                expected_roi
                business_plan
                collateral_type
                collateral_value
                collateral_documents
                risk_assessment
                status
                created_at
                updated_at
                created_by
                approved_by
                approval_date
            }
        }
        """
        variables = {
            "id": loan_id,
            "loan": {
                **loan.dict(exclude_unset=True),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        result = await self.nhost.graphql(query, variables)
        return InvestmentLoan(**result["update_investment_loans_by_pk"])

    async def get_investment_loan(self, loan_id: str) -> InvestmentLoan:
        query = """
        query GetInvestmentLoan($id: uuid!) {
            investment_loans_by_pk(id: $id) {
                id
                project_id
                loan_amount
                interest_rate
                term_years
                expected_roi
                business_plan
                collateral_type
                collateral_value
                collateral_documents
                risk_assessment
                status
                created_at
                updated_at
                created_by
                approved_by
                approval_date
            }
        }
        """
        result = await self.nhost.graphql(query, {"id": loan_id})
        return InvestmentLoan(**result["investment_loans_by_pk"])

    # Common Methods
    async def calculate_ltv_ratio(self, property_value: Decimal, loan_amount: Decimal) -> Decimal:
        """Calculate Loan to Value ratio"""
        return (loan_amount / property_value) * 100

    async def calculate_monthly_payment(
        self, loan_amount: Decimal, interest_rate: Decimal, term_years: int
    ) -> Decimal:
        """Calculate monthly mortgage payment"""
        monthly_rate = interest_rate / 12 / 100
        num_payments = term_years * 12
        return loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)

    async def assess_risk(
        self,
        credit_score: int,
        income: Decimal,
        debt_to_income: Decimal,
        ltv_ratio: Decimal,
        property_value: Decimal
    ) -> Dict[str, Any]:
        """Assess risk for mortgage loan"""
        risk_score = 0
        risk_factors = []

        # Credit Score Assessment
        if credit_score < 580:
            risk_score += 3
            risk_factors.append("Poor credit score")
        elif credit_score < 670:
            risk_score += 2
            risk_factors.append("Fair credit score")
        elif credit_score < 740:
            risk_score += 1
            risk_factors.append("Good credit score")

        # LTV Ratio Assessment
        if ltv_ratio > 80:
            risk_score += 2
            risk_factors.append("High LTV ratio")
        elif ltv_ratio > 70:
            risk_score += 1
            risk_factors.append("Moderate LTV ratio")

        # Debt to Income Assessment
        if debt_to_income > 43:
            risk_score += 3
            risk_factors.append("High debt-to-income ratio")
        elif debt_to_income > 36:
            risk_score += 2
            risk_factors.append("Moderate debt-to-income ratio")

        # Property Value Assessment
        if property_value < 100000:
            risk_score += 1
            risk_factors.append("Low property value")

        return {
            "risk_score": risk_score,
            "risk_level": "high" if risk_score > 5 else "medium" if risk_score > 2 else "low",
            "risk_factors": risk_factors,
            "recommendation": "reject" if risk_score > 7 else "review" if risk_score > 4 else "approve"
        } 