from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from ...models import (
    MarketAnalysis, MarketAnalysisCreate, MarketAnalysisUpdate,
    AgentPerformance, AgentPerformanceCreate, AgentPerformanceUpdate,
    FinancialReport, FinancialReportCreate, FinancialReportUpdate,
    DashboardMetrics, DashboardMetricsCreate, DashboardMetricsUpdate
)
from ...services.analytics import AnalyticsService
from ..deps import get_current_user, get_analytics_service
from ...models import User

router = APIRouter()

# Endpoints para Análisis de Mercado
@router.post("/market-analysis", response_model=MarketAnalysis)
async def create_market_analysis(
    analysis_data: MarketAnalysisCreate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Crear un nuevo análisis de mercado"""
    if current_user.role not in ["ceo", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear análisis de mercado")
    
    return await analytics_service.create_market_analysis(analysis_data)

@router.put("/market-analysis/{analysis_id}", response_model=MarketAnalysis)
async def update_market_analysis(
    analysis_id: UUID,
    analysis_data: MarketAnalysisUpdate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Actualizar un análisis de mercado"""
    if current_user.role not in ["ceo", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar análisis de mercado")
    
    analysis = await analytics_service.update_market_analysis(analysis_id, analysis_data)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    return analysis

@router.get("/market-analysis", response_model=List[MarketAnalysis])
async def get_market_analysis(
    location: str,
    property_type: str,
    period: str,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Obtener análisis de mercado por ubicación y tipo de propiedad"""
    if current_user.role not in ["ceo", "manager", "supervisor", "agent"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver análisis de mercado")
    
    return await analytics_service.get_market_analysis(location, property_type, period)

# Endpoints para Rendimiento de Agentes
@router.post("/agent-performance", response_model=AgentPerformance)
async def create_agent_performance(
    performance_data: AgentPerformanceCreate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Crear un nuevo registro de rendimiento de agente"""
    if current_user.role not in ["manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear registros de rendimiento")
    
    return await analytics_service.create_agent_performance(performance_data)

@router.put("/agent-performance/{performance_id}", response_model=AgentPerformance)
async def update_agent_performance(
    performance_id: UUID,
    performance_data: AgentPerformanceUpdate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Actualizar el rendimiento de un agente"""
    if current_user.role not in ["manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar registros de rendimiento")
    
    performance = await analytics_service.update_agent_performance(performance_id, performance_data)
    if not performance:
        raise HTTPException(status_code=404, detail="Registro de rendimiento no encontrado")
    
    return performance

@router.get("/agent-performance/{agent_id}", response_model=List[AgentPerformance])
async def get_agent_performance(
    agent_id: UUID,
    period: str,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Obtener el rendimiento de un agente"""
    if current_user.role not in ["ceo", "manager", "supervisor"] and str(current_user.id) != str(agent_id):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este registro de rendimiento")
    
    return await analytics_service.get_agent_performance(agent_id, period)

# Endpoints para Reportes Financieros
@router.post("/financial-reports", response_model=FinancialReport)
async def create_financial_report(
    report_data: FinancialReportCreate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Crear un nuevo reporte financiero"""
    if current_user.role not in ["ceo", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear reportes financieros")
    
    return await analytics_service.create_financial_report(report_data)

@router.put("/financial-reports/{report_id}", response_model=FinancialReport)
async def update_financial_report(
    report_id: UUID,
    report_data: FinancialReportUpdate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Actualizar un reporte financiero"""
    if current_user.role not in ["ceo", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar reportes financieros")
    
    report = await analytics_service.update_financial_report(report_id, report_data)
    if not report:
        raise HTTPException(status_code=404, detail="Reporte financiero no encontrado")
    
    return report

@router.get("/financial-reports", response_model=List[FinancialReport])
async def get_financial_reports(
    report_type: str,
    period: str,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Obtener reportes financieros por tipo y período"""
    if current_user.role not in ["ceo", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver reportes financieros")
    
    return await analytics_service.get_financial_reports(report_type, period)

# Endpoints para Métricas del Dashboard
@router.post("/dashboard-metrics", response_model=DashboardMetrics)
async def create_dashboard_metrics(
    metrics_data: DashboardMetricsCreate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Crear nuevas métricas para el dashboard"""
    if current_user.role not in ["ceo", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear métricas del dashboard")
    
    return await analytics_service.create_dashboard_metrics(metrics_data)

@router.put("/dashboard-metrics/{metrics_id}", response_model=DashboardMetrics)
async def update_dashboard_metrics(
    metrics_id: UUID,
    metrics_data: DashboardMetricsUpdate,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Actualizar métricas del dashboard"""
    if current_user.role not in ["ceo", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar métricas del dashboard")
    
    metrics = await analytics_service.update_dashboard_metrics(metrics_id, metrics_data)
    if not metrics:
        raise HTTPException(status_code=404, detail="Métricas no encontradas")
    
    return metrics

@router.get("/dashboard-metrics", response_model=Optional[DashboardMetrics])
async def get_dashboard_metrics(
    dashboard_type: str,
    period: str,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Obtener métricas del dashboard"""
    if current_user.role not in ["ceo", "manager", "supervisor", "agent"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver métricas del dashboard")
    
    return await analytics_service.get_dashboard_metrics(dashboard_type, period) 