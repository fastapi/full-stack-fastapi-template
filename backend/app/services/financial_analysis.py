from datetime import datetime
from typing import List, Dict, Any, Optional
from ..core.nhost import NhostClient
from ..models import (
    CreditScore, CreditScoreCreate, CreditScoreUpdate,
    CreditHistory, CreditHistoryCreate, CreditHistoryUpdate,
    FinancialReport, FinancialReportCreate, FinancialReportUpdate,
    RiskAnalysis, RiskAnalysisCreate, RiskAnalysisUpdate
)

class FinancialAnalysisService:
    def __init__(self, nhost_client: NhostClient):
        self.nhost = nhost_client

    async def create_credit_score(self, score: CreditScoreCreate) -> CreditScore:
        query = """
        mutation CreateCreditScore($score: credit_scores_insert_input!) {
            insert_credit_scores_one(object: $score) {
                id
                client_id
                score
                factors
                risk_level
                last_updated
                valid_until
                notes
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {"score": score.dict()}
        result = await self.nhost.graphql(query, variables)
        return CreditScore(**result["insert_credit_scores_one"])

    async def update_credit_score(self, score_id: str, update: CreditScoreUpdate) -> CreditScore:
        query = """
        mutation UpdateCreditScore($id: uuid!, $update: credit_scores_set_input!) {
            update_credit_scores_by_pk(pk_columns: {id: $id}, _set: $update) {
                id
                client_id
                score
                factors
                risk_level
                last_updated
                valid_until
                notes
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {
            "id": score_id,
            "update": update.dict(exclude_unset=True)
        }
        result = await self.nhost.graphql(query, variables)
        return CreditScore(**result["update_credit_scores_by_pk"])

    async def get_client_credit_score(self, client_id: str) -> CreditScore:
        query = """
        query GetClientCreditScore($client_id: uuid!) {
            credit_scores(where: {client_id: {_eq: $client_id}}, order_by: {last_updated: desc}, limit: 1) {
                id
                client_id
                score
                factors
                risk_level
                last_updated
                valid_until
                notes
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {"client_id": client_id}
        result = await self.nhost.graphql(query, variables)
        return CreditScore(**result["credit_scores"][0]) if result["credit_scores"] else None

    async def create_credit_history(self, history: CreditHistoryCreate) -> CreditHistory:
        query = """
        mutation CreateCreditHistory($history: credit_histories_insert_input!) {
            insert_credit_histories_one(object: $history) {
                id
                client_id
                loan_id
                payment_status
                delinquency_days
                payment_history
                credit_utilization
                credit_limit
                notes
                created_at
                updated_at
            }
        }
        """
        variables = {"history": history.dict()}
        result = await self.nhost.graphql(query, variables)
        return CreditHistory(**result["insert_credit_histories_one"])

    async def create_financial_report(self, report: FinancialReportCreate) -> FinancialReport:
        query = """
        mutation CreateFinancialReport($report: financial_reports_insert_input!) {
            insert_financial_reports_one(object: $report) {
                id
                report_type
                period
                start_date
                end_date
                data
                summary
                analysis
                recommendations
                notes
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {"report": report.dict()}
        result = await self.nhost.graphql(query, variables)
        return FinancialReport(**result["insert_financial_reports_one"])

    async def create_risk_analysis(self, analysis: RiskAnalysisCreate) -> RiskAnalysis:
        query = """
        mutation CreateRiskAnalysis($analysis: risk_analyses_insert_input!) {
            insert_risk_analyses_one(object: $analysis) {
                id
                loan_id
                risk_score
                risk_factors
                risk_level
                mitigation_measures
                monitoring_plan
                notes
                created_at
                updated_at
                created_by
                last_reviewed
                reviewed_by
            }
        }
        """
        variables = {"analysis": analysis.dict()}
        result = await self.nhost.graphql(query, variables)
        return RiskAnalysis(**result["insert_risk_analyses_one"])

    async def get_loan_risk_analysis(self, loan_id: str) -> RiskAnalysis:
        query = """
        query GetLoanRiskAnalysis($loan_id: uuid!) {
            risk_analyses(where: {loan_id: {_eq: $loan_id}}, order_by: {created_at: desc}, limit: 1) {
                id
                loan_id
                risk_score
                risk_factors
                risk_level
                mitigation_measures
                monitoring_plan
                notes
                created_at
                updated_at
                created_by
                last_reviewed
                reviewed_by
            }
        }
        """
        variables = {"loan_id": loan_id}
        result = await self.nhost.graphql(query, variables)
        return RiskAnalysis(**result["risk_analyses"][0]) if result["risk_analyses"] else None

    async def calculate_credit_score(self, client_id: str) -> Dict[str, Any]:
        # Implementar lógica de cálculo de score crediticio
        # Este es un ejemplo simplificado
        query = """
        query GetClientData($client_id: uuid!) {
            credit_histories(where: {client_id: {_eq: $client_id}}) {
                payment_status
                delinquency_days
                payment_history
                credit_utilization
            }
            loans(where: {client_id: {_eq: $client_id}}) {
                status
                total_paid
                remaining_balance
                delinquency_days
            }
        }
        """
        variables = {"client_id": client_id}
        result = await self.nhost.graphql(query, variables)
        
        # Lógica de cálculo (ejemplo)
        score = 700  # Score base
        factors = {
            "payment_history": 0.0,
            "credit_utilization": 0.0,
            "delinquency": 0.0
        }
        
        # Ajustar score basado en historial de pagos
        for history in result["credit_histories"]:
            if history["payment_status"] == "on_time":
                factors["payment_history"] += 0.1
            elif history["delinquency_days"] > 0:
                factors["delinquency"] -= 0.05 * min(history["delinquency_days"] / 30, 1)
            
            if history["credit_utilization"] < 0.3:
                factors["credit_utilization"] += 0.1
            elif history["credit_utilization"] > 0.7:
                factors["credit_utilization"] -= 0.1
        
        # Calcular score final
        final_score = score + sum(factors.values()) * 100
        final_score = max(300, min(850, final_score))  # Limitar entre 300 y 850
        
        # Determinar nivel de riesgo
        risk_level = "low"
        if final_score < 580:
            risk_level = "high"
        elif final_score < 670:
            risk_level = "medium"
        
        return {
            "score": int(final_score),
            "factors": factors,
            "risk_level": risk_level
        } 