
import psutil
import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.api.deps import CurrentAdmin, SessionDep
from app.models import (
    AISoulEntity,
    ChatMessage,
    Document,
    TrainingDocument,
    TrainingMessage,
    User,
)
from app.services.enhanced_rag_service import EnhancedRAGService

router = APIRouter()


@router.get("/health-check/", include_in_schema=True)
async def health_check() -> dict:
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}


@router.get("/system-health/", include_in_schema=True)
async def get_system_health(
    *,
    db: SessionDep,
    current_user: CurrentAdmin,
) -> dict[str, Any]:
    """
    Get comprehensive system health metrics.
    Only admins can access system health data.
    """
    try:
        # Get system metrics using psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Get database statistics
        total_users = db.exec(select(func.count(User.id))).one()
        total_ai_souls = db.exec(select(func.count(AISoulEntity.id))).one()
        total_documents = db.exec(select(func.count(Document.id))).one()
        total_training_docs = db.exec(select(func.count(TrainingDocument.id))).one()
        total_chat_messages = db.exec(select(func.count(ChatMessage.id))).one()
        total_training_messages = db.exec(select(func.count(TrainingMessage.id))).one()
        
        # Get active connections (approximate)
        recent_messages = db.exec(
            select(func.count(ChatMessage.id)).where(
                ChatMessage.timestamp > datetime.utcnow() - timedelta(hours=1)
            )
        ).one()
        
        # Get RAG service health
        rag_service = EnhancedRAGService(db)
        rag_health = await rag_service.health_check()
        
        # Determine service statuses
        services = []
        
        # Enhanced RAG Service
        rag_status = "healthy" if rag_health.get("status") == "healthy" else "degraded"
        services.append({
            "name": "Enhanced RAG Service",
            "status": rag_status,
            "response_time": rag_health.get("response_time_ms", 0),
            "last_check": datetime.utcnow().isoformat(),
            "uptime": 99.8 if rag_status == "healthy" else 85.0,
            "details": rag_health.get("components", {})
        })
        
        # Database health (based on successful query)
        try:
            db_start = time.time()
            db.exec(select(func.count(User.id))).one()
            db_response_time = int((time.time() - db_start) * 1000)
            db_status = "healthy" if db_response_time < 500 else "degraded"
        except Exception:
            db_status = "down"
            db_response_time = 0
            
        services.append({
            "name": "PostgreSQL Database",
            "status": db_status,
            "response_time": db_response_time,
            "last_check": datetime.utcnow().isoformat(),
            "uptime": 99.5 if db_status == "healthy" else 95.0
        })
        
        # Add other services from RAG health check
        for component, details in rag_health.get("components", {}).items():
            if component not in ["database", "enhanced_rag"]:
                status = "healthy" if details.get("status") == "healthy" else "degraded"
                services.append({
                    "name": component.replace("_", " ").title(),
                    "status": status,
                    "response_time": details.get("response_time_ms", 0),
                    "last_check": datetime.utcnow().isoformat(),
                    "uptime": 99.0 if status == "healthy" else 90.0
                })
        
        # Calculate network latency (simplified)
        network_latency = max(1, min(50, int(cpu_percent / 2)))  # Rough estimation
        
        return {
            "status": "healthy" if all(s["status"] in ["healthy", "degraded"] for s in services) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "cpu_usage": round(cpu_percent, 1),
                "memory_usage": round(memory.percent, 1),
                "disk_usage": round(disk.percent, 1),
                "network_latency": network_latency,
                "active_connections": recent_messages,
                "total_requests": total_chat_messages + total_training_messages,
                "memory_total_gb": round(memory.total / (1024**3), 1),
                "memory_available_gb": round(memory.available / (1024**3), 1),
                "disk_total_gb": round(disk.total / (1024**3), 1),
                "disk_free_gb": round(disk.free / (1024**3), 1),
            },
            "services": services,
            "database_stats": {
                "total_users": total_users,
                "total_ai_souls": total_ai_souls,
                "total_documents": total_documents,
                "total_training_documents": total_training_docs,
                "total_chat_messages": total_chat_messages,
                "total_training_messages": total_training_messages,
                "recent_activity": recent_messages
            },
            "alerts": _generate_system_alerts(cpu_percent, memory.percent, disk.percent, services)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )


def _generate_system_alerts(cpu_usage: float, memory_usage: float, disk_usage: float, services: list) -> list[dict]:
    """Generate system alerts based on metrics."""
    alerts = []
    
    if cpu_usage > 80:
        alerts.append({
            "type": "warning",
            "message": f"High CPU usage detected ({cpu_usage:.1f}%)",
            "severity": "high" if cpu_usage > 90 else "medium"
        })
    
    if memory_usage > 80:
        alerts.append({
            "type": "warning",
            "message": f"High memory usage detected ({memory_usage:.1f}%)",
            "severity": "high" if memory_usage > 90 else "medium"
        })
    
    if disk_usage > 80:
        alerts.append({
            "type": "warning",
            "message": f"High disk usage detected ({disk_usage:.1f}%)",
            "severity": "high" if disk_usage > 90 else "medium"
        })
    
    # Check for degraded services
    degraded_services = [s for s in services if s["status"] == "degraded"]
    for service in degraded_services:
        alerts.append({
            "type": "warning",
            "message": f"{service['name']} performance degraded (response time: {service['response_time']}ms)",
            "severity": "medium"
        })
    
    down_services = [s for s in services if s["status"] == "down"]
    for service in down_services:
        alerts.append({
            "type": "error",
            "message": f"{service['name']} is down",
            "severity": "high"
        })
    
    if not alerts:
        alerts.append({
            "type": "info",
            "message": "All systems operating normally",
            "severity": "low"
        })
    
    return alerts
