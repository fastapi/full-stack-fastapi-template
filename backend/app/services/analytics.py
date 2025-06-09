from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from nhost import NhostClient
from ..models import (
    MarketAnalysis, MarketAnalysisCreate, MarketAnalysisUpdate,
    AgentPerformance, AgentPerformanceCreate, AgentPerformanceUpdate,
    FinancialReport, FinancialReportCreate, FinancialReportUpdate,
    DashboardMetrics, DashboardMetricsCreate, DashboardMetricsUpdate
)

class AnalyticsService:
    def __init__(self, nhost: NhostClient):
        self.nhost = nhost

    # Análisis de Mercado
    async def create_market_analysis(self, analysis_data: MarketAnalysisCreate) -> MarketAnalysis:
        """Crear un nuevo análisis de mercado"""
        query = """
        mutation CreateMarketAnalysis($analysis: market_analysis_insert_input!) {
            insert_market_analysis_one(object: $analysis) {
                id
                property_type
                location
                period
                start_date
                end_date
                metrics
                insights
                recommendations
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {"analysis": analysis_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return MarketAnalysis(**result["data"]["insert_market_analysis_one"])

    async def update_market_analysis(self, analysis_id: UUID, analysis_data: MarketAnalysisUpdate) -> Optional[MarketAnalysis]:
        """Actualizar un análisis de mercado"""
        query = """
        mutation UpdateMarketAnalysis($id: uuid!, $analysis: market_analysis_set_input!) {
            update_market_analysis_by_pk(pk_columns: {id: $id}, _set: $analysis) {
                id
                property_type
                location
                period
                start_date
                end_date
                metrics
                insights
                recommendations
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {
            "id": str(analysis_id),
            "analysis": {k: v for k, v in analysis_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        analysis_data = result["data"]["update_market_analysis_by_pk"]
        return MarketAnalysis(**analysis_data) if analysis_data else None

    async def get_market_analysis(self, location: str, property_type: str, period: str) -> List[MarketAnalysis]:
        """Obtener análisis de mercado por ubicación y tipo de propiedad"""
        query = """
        query GetMarketAnalysis($location: String!, $property_type: String!, $period: String!) {
            market_analysis(
                where: {
                    location: {_eq: $location},
                    property_type: {_eq: $property_type},
                    period: {_eq: $period}
                }
            ) {
                id
                property_type
                location
                period
                start_date
                end_date
                metrics
                insights
                recommendations
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {
            "location": location,
            "property_type": property_type,
            "period": period
        }
        result = await self.nhost.graphql.request(query, variables)
        return [MarketAnalysis(**analysis) for analysis in result["data"]["market_analysis"]]

    # Rendimiento de Agentes
    async def create_agent_performance(self, performance_data: AgentPerformanceCreate) -> AgentPerformance:
        """Crear un nuevo registro de rendimiento de agente"""
        query = """
        mutation CreateAgentPerformance($performance: agent_performance_insert_input!) {
            insert_agent_performance_one(object: $performance) {
                id
                agent_id
                period
                start_date
                end_date
                metrics
                goals
                achievements
                created_at
                updated_at
            }
        }
        """
        variables = {"performance": performance_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return AgentPerformance(**result["data"]["insert_agent_performance_one"])

    async def update_agent_performance(self, performance_id: UUID, performance_data: AgentPerformanceUpdate) -> Optional[AgentPerformance]:
        """Actualizar el rendimiento de un agente"""
        query = """
        mutation UpdateAgentPerformance($id: uuid!, $performance: agent_performance_set_input!) {
            update_agent_performance_by_pk(pk_columns: {id: $id}, _set: $performance) {
                id
                agent_id
                period
                start_date
                end_date
                metrics
                goals
                achievements
                created_at
                updated_at
            }
        }
        """
        variables = {
            "id": str(performance_id),
            "performance": {k: v for k, v in performance_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        performance_data = result["data"]["update_agent_performance_by_pk"]
        return AgentPerformance(**performance_data) if performance_data else None

    async def get_agent_performance(self, agent_id: UUID, period: str) -> List[AgentPerformance]:
        """Obtener el rendimiento de un agente"""
        query = """
        query GetAgentPerformance($agent_id: uuid!, $period: String!) {
            agent_performance(
                where: {
                    agent_id: {_eq: $agent_id},
                    period: {_eq: $period}
                }
            ) {
                id
                agent_id
                period
                start_date
                end_date
                metrics
                goals
                achievements
                created_at
                updated_at
            }
        }
        """
        variables = {
            "agent_id": str(agent_id),
            "period": period
        }
        result = await self.nhost.graphql.request(query, variables)
        return [AgentPerformance(**performance) for performance in result["data"]["agent_performance"]]

    # Reportes Financieros
    async def create_financial_report(self, report_data: FinancialReportCreate) -> FinancialReport:
        """Crear un nuevo reporte financiero"""
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
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {"report": report_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return FinancialReport(**result["data"]["insert_financial_reports_one"])

    async def update_financial_report(self, report_id: UUID, report_data: FinancialReportUpdate) -> Optional[FinancialReport]:
        """Actualizar un reporte financiero"""
        query = """
        mutation UpdateFinancialReport($id: uuid!, $report: financial_reports_set_input!) {
            update_financial_reports_by_pk(pk_columns: {id: $id}, _set: $report) {
                id
                report_type
                period
                start_date
                end_date
                data
                summary
                analysis
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {
            "id": str(report_id),
            "report": {k: v for k, v in report_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        report_data = result["data"]["update_financial_reports_by_pk"]
        return FinancialReport(**report_data) if report_data else None

    async def get_financial_reports(self, report_type: str, period: str) -> List[FinancialReport]:
        """Obtener reportes financieros por tipo y período"""
        query = """
        query GetFinancialReports($report_type: String!, $period: String!) {
            financial_reports(
                where: {
                    report_type: {_eq: $report_type},
                    period: {_eq: $period}
                }
            ) {
                id
                report_type
                period
                start_date
                end_date
                data
                summary
                analysis
                created_at
                updated_at
                created_by
            }
        }
        """
        variables = {
            "report_type": report_type,
            "period": period
        }
        result = await self.nhost.graphql.request(query, variables)
        return [FinancialReport(**report) for report in result["data"]["financial_reports"]]

    # Métricas del Dashboard
    async def create_dashboard_metrics(self, metrics_data: DashboardMetricsCreate) -> DashboardMetrics:
        """Crear nuevas métricas para el dashboard"""
        query = """
        mutation CreateDashboardMetrics($metrics: dashboard_metrics_insert_input!) {
            insert_dashboard_metrics_one(object: $metrics) {
                id
                dashboard_type
                period
                start_date
                end_date
                metrics
                trends
                alerts
                created_at
                updated_at
                last_updated
            }
        }
        """
        variables = {"metrics": metrics_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return DashboardMetrics(**result["data"]["insert_dashboard_metrics_one"])

    async def update_dashboard_metrics(self, metrics_id: UUID, metrics_data: DashboardMetricsUpdate) -> Optional[DashboardMetrics]:
        """Actualizar métricas del dashboard"""
        query = """
        mutation UpdateDashboardMetrics($id: uuid!, $metrics: dashboard_metrics_set_input!) {
            update_dashboard_metrics_by_pk(pk_columns: {id: $id}, _set: $metrics) {
                id
                dashboard_type
                period
                start_date
                end_date
                metrics
                trends
                alerts
                created_at
                updated_at
                last_updated
            }
        }
        """
        variables = {
            "id": str(metrics_id),
            "metrics": {k: v for k, v in metrics_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        metrics_data = result["data"]["update_dashboard_metrics_by_pk"]
        return DashboardMetrics(**metrics_data) if metrics_data else None

    async def get_dashboard_metrics(self, dashboard_type: str, period: str) -> Optional[DashboardMetrics]:
        """Obtener métricas del dashboard"""
        query = """
        query GetDashboardMetrics($dashboard_type: String!, $period: String!) {
            dashboard_metrics(
                where: {
                    dashboard_type: {_eq: $dashboard_type},
                    period: {_eq: $period}
                },
                order_by: {last_updated: desc},
                limit: 1
            ) {
                id
                dashboard_type
                period
                start_date
                end_date
                metrics
                trends
                alerts
                created_at
                updated_at
                last_updated
            }
        }
        """
        variables = {
            "dashboard_type": dashboard_type,
            "period": period
        }
        result = await self.nhost.graphql.request(query, variables)
        metrics = result["data"]["dashboard_metrics"]
        return DashboardMetrics(**metrics[0]) if metrics else None 