from datetime import datetime
from typing import List, Optional
from ..core.nhost import NhostClient
from ..models import (
    CreditRequest, CreditRequestCreate, CreditRequestUpdate,
    Loan, LoanCreate, LoanUpdate,
    Payment, PaymentCreate, PaymentUpdate,
    Guarantee, GuaranteeCreate, GuaranteeUpdate
)

class CreditService:
    def __init__(self, nhost_client: NhostClient):
        self.nhost = nhost_client

    async def create_credit_request(self, request: CreditRequestCreate) -> CreditRequest:
        query = """
        mutation CreateCreditRequest($request: credit_requests_insert_input!) {
            insert_credit_requests_one(object: $request) {
                id
                client_id
                amount
                currency
                purpose
                term_months
                interest_rate
                monthly_payment
                status
                credit_score
                income
                employment_status
                employment_years
                documents
                notes
                created_at
                updated_at
                approved_by
                approved_at
                rejected_by
                rejected_at
                rejection_reason
            }
        }
        """
        variables = {"request": request.dict()}
        result = await self.nhost.graphql(query, variables)
        return CreditRequest(**result["insert_credit_requests_one"])

    async def update_credit_request(self, request_id: str, update: CreditRequestUpdate) -> CreditRequest:
        query = """
        mutation UpdateCreditRequest($id: uuid!, $update: credit_requests_set_input!) {
            update_credit_requests_by_pk(pk_columns: {id: $id}, _set: $update) {
                id
                client_id
                amount
                currency
                purpose
                term_months
                interest_rate
                monthly_payment
                status
                credit_score
                income
                employment_status
                employment_years
                documents
                notes
                created_at
                updated_at
                approved_by
                approved_at
                rejected_by
                rejected_at
                rejection_reason
            }
        }
        """
        variables = {
            "id": request_id,
            "update": update.dict(exclude_unset=True)
        }
        result = await self.nhost.graphql(query, variables)
        return CreditRequest(**result["update_credit_requests_by_pk"])

    async def get_credit_request(self, request_id: str) -> CreditRequest:
        query = """
        query GetCreditRequest($id: uuid!) {
            credit_requests_by_pk(id: $id) {
                id
                client_id
                amount
                currency
                purpose
                term_months
                interest_rate
                monthly_payment
                status
                credit_score
                income
                employment_status
                employment_years
                documents
                notes
                created_at
                updated_at
                approved_by
                approved_at
                rejected_by
                rejected_at
                rejection_reason
            }
        }
        """
        variables = {"id": request_id}
        result = await self.nhost.graphql(query, variables)
        return CreditRequest(**result["credit_requests_by_pk"])

    async def create_loan(self, loan: LoanCreate) -> Loan:
        query = """
        mutation CreateLoan($loan: loans_insert_input!) {
            insert_loans_one(object: $loan) {
                id
                credit_request_id
                client_id
                amount
                currency
                term_months
                interest_rate
                monthly_payment
                start_date
                end_date
                status
                payment_day
                payment_method
                bank_account
                documents
                notes
                created_at
                updated_at
                created_by
                total_paid
                remaining_balance
                next_payment_date
                last_payment_date
                delinquency_days
            }
        }
        """
        variables = {"loan": loan.dict()}
        result = await self.nhost.graphql(query, variables)
        return Loan(**result["insert_loans_one"])

    async def update_loan(self, loan_id: str, update: LoanUpdate) -> Loan:
        query = """
        mutation UpdateLoan($id: uuid!, $update: loans_set_input!) {
            update_loans_by_pk(pk_columns: {id: $id}, _set: $update) {
                id
                credit_request_id
                client_id
                amount
                currency
                term_months
                interest_rate
                monthly_payment
                start_date
                end_date
                status
                payment_day
                payment_method
                bank_account
                documents
                notes
                created_at
                updated_at
                created_by
                total_paid
                remaining_balance
                next_payment_date
                last_payment_date
                delinquency_days
            }
        }
        """
        variables = {
            "id": loan_id,
            "update": update.dict(exclude_unset=True)
        }
        result = await self.nhost.graphql(query, variables)
        return Loan(**result["update_loans_by_pk"])

    async def create_payment(self, payment: PaymentCreate) -> Payment:
        query = """
        mutation CreatePayment($payment: payments_insert_input!) {
            insert_payments_one(object: $payment) {
                id
                loan_id
                amount
                currency
                payment_date
                payment_method
                reference_number
                status
                notes
                created_at
                updated_at
                created_by
                processed_by
                processed_at
            }
        }
        """
        variables = {"payment": payment.dict()}
        result = await self.nhost.graphql(query, variables)
        return Payment(**result["insert_payments_one"])

    async def create_guarantee(self, guarantee: GuaranteeCreate) -> Guarantee:
        query = """
        mutation CreateGuarantee($guarantee: guarantees_insert_input!) {
            insert_guarantees_one(object: $guarantee) {
                id
                loan_id
                type
                value
                currency
                description
                documents
                status
                notes
                created_at
                updated_at
                created_by
                verified_by
                verified_at
                verification_notes
            }
        }
        """
        variables = {"guarantee": guarantee.dict()}
        result = await self.nhost.graphql(query, variables)
        return Guarantee(**result["insert_guarantees_one"])

    async def get_loan_payments(self, loan_id: str) -> List[Payment]:
        query = """
        query GetLoanPayments($loan_id: uuid!) {
            payments(where: {loan_id: {_eq: $loan_id}}) {
                id
                loan_id
                amount
                currency
                payment_date
                payment_method
                reference_number
                status
                notes
                created_at
                updated_at
                created_by
                processed_by
                processed_at
            }
        }
        """
        variables = {"loan_id": loan_id}
        result = await self.nhost.graphql(query, variables)
        return [Payment(**payment) for payment in result["payments"]]

    async def get_loan_guarantees(self, loan_id: str) -> List[Guarantee]:
        query = """
        query GetLoanGuarantees($loan_id: uuid!) {
            guarantees(where: {loan_id: {_eq: $loan_id}}) {
                id
                loan_id
                type
                value
                currency
                description
                documents
                status
                notes
                created_at
                updated_at
                created_by
                verified_by
                verified_at
                verification_notes
            }
        }
        """
        variables = {"loan_id": loan_id}
        result = await self.nhost.graphql(query, variables)
        return [Guarantee(**guarantee) for guarantee in result["guarantees"]] 