from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/client", tags=["Client Dashboard"])

class PropertyMetrics(BaseModel):
    id: str
    title: str
    type: str
    location: str
    price: float
    currency: str
    transaction_type: str  # "venta" or "alquiler"
    status: str
    listing_date: str
    views: int
    favorites: int
    monthly_income: Optional[float] = None
    agent: dict

class CreditMetrics(BaseModel):
    id: str
    type: str
    amount: float
    currency: str
    status: str
    monthly_payment: float
    remaining_balance: float
    next_payment_date: str
    term: int
    interest_rate: float

class InvestmentMetrics(BaseModel):
    id: str
    type: str
    amount: float
    currency: str
    roi: float
    status: str
    start_date: str
    end_date: Optional[str] = None
    monthly_return: float

class ClientDashboardMetrics(BaseModel):
    total_property_value: float
    monthly_rental_income: float
    total_credits: float
    total_investments: float
    net_worth: float
    portfolio_growth: float

class ClientDashboardResponse(BaseModel):
    metrics: ClientDashboardMetrics
    properties: List[PropertyMetrics]
    credits: List[CreditMetrics]
    investments: List[InvestmentMetrics]
    recent_activity: List[dict]

# Datos de ejemplo - En producción vendrían de la base de datos
SAMPLE_PROPERTIES = [
    {
        "id": "1",
        "title": "Apartamento El Poblado",
        "type": "Apartamento",
        "location": "El Poblado, Medellín",
        "price": 650000000,
        "currency": "COP",
        "transaction_type": "alquiler",
        "status": "alquilado",
        "listing_date": "2024-01-15T00:00:00Z",
        "views": 245,
        "favorites": 12,
        "monthly_income": 3200000,
        "agent": {
            "name": "Ana López",
            "phone": "+57 316 682 7239",
            "email": "ana@geniusindustries.org"
        }
    },
    {
        "id": "2",
        "title": "Casa Zona Rosa",
        "type": "Casa",
        "location": "Zona Rosa, Bogotá",
        "price": 850000000,
        "currency": "COP",
        "transaction_type": "venta",
        "status": "vendido",
        "listing_date": "2023-12-10T00:00:00Z",
        "views": 412,
        "favorites": 28,
        "monthly_income": None,
        "agent": {
            "name": "Carlos Martínez",
            "phone": "+57 316 682 7239",
            "email": "carlos@geniusindustries.org"
        }
    }
]

SAMPLE_CREDITS = [
    {
        "id": "1",
        "type": "Hipotecario",
        "amount": 420000000,
        "currency": "COP",
        "status": "aprobado",
        "monthly_payment": 2850000,
        "remaining_balance": 385000000,
        "next_payment_date": "2024-02-15T00:00:00Z",
        "term": 180,
        "interest_rate": 1.2
    },
    {
        "id": "2",
        "type": "Personal",
        "amount": 50000000,
        "currency": "COP",
        "status": "pagado",
        "monthly_payment": 0,
        "remaining_balance": 0,
        "next_payment_date": "-",
        "term": 36,
        "interest_rate": 2.5
    }
]

SAMPLE_INVESTMENTS = [
    {
        "id": "1",
        "type": "Fondo Inmobiliario",
        "amount": 100000000,
        "currency": "COP",
        "roi": 8.5,
        "status": "activo",
        "start_date": "2023-06-01T00:00:00Z",
        "end_date": None,
        "monthly_return": 708333
    },
    {
        "id": "2",
        "type": "Trading Tradicional",
        "amount": 25000000,
        "currency": "COP",
        "roi": 12.3,
        "status": "activo",
        "start_date": "2023-09-15T00:00:00Z",
        "end_date": None,
        "monthly_return": 256250
    }
]

@router.get("/dashboard", response_model=ClientDashboardResponse)
async def get_client_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener dashboard completo del cliente con métricas y datos
    """
    try:
        # En producción, estos datos vendrían de la base de datos filtrados por current_user.id
        properties = SAMPLE_PROPERTIES
        credits = SAMPLE_CREDITS
        investments = SAMPLE_INVESTMENTS
        
        # Calcular métricas
        total_property_value = sum(prop["price"] for prop in properties)
        monthly_rental_income = sum(
            prop.get("monthly_income", 0) for prop in properties 
            if prop["transaction_type"] == "alquiler" and prop["status"] == "alquilado"
        )
        total_credits = sum(credit["remaining_balance"] for credit in credits)
        total_investments = sum(inv["amount"] for inv in investments)
        net_worth = total_property_value + total_investments - total_credits
        
        metrics = ClientDashboardMetrics(
            total_property_value=total_property_value,
            monthly_rental_income=monthly_rental_income,
            total_credits=total_credits,
            total_investments=total_investments,
            net_worth=net_worth,
            portfolio_growth=12.5  # Ejemplo: crecimiento del 12.5%
        )
        
        # Actividad reciente (ejemplo)
        recent_activity = [
            {
                "id": "1",
                "type": "rental_payment",
                "description": "Pago de alquiler recibido",
                "property": "Apartamento El Poblado",
                "amount": 3200000,
                "currency": "COP",
                "date": (datetime.now() - timedelta(days=2)).isoformat(),
                "status": "completed"
            },
            {
                "id": "2",
                "type": "investment_return",
                "description": "Retorno de inversión",
                "investment": "Fondo Inmobiliario",
                "amount": 708333,
                "currency": "COP",
                "date": (datetime.now() - timedelta(weeks=1)).isoformat(),
                "status": "completed"
            },
            {
                "id": "3",
                "type": "credit_payment",
                "description": "Pago de crédito hipotecario",
                "credit": "Hipotecario",
                "amount": -2850000,
                "currency": "COP",
                "date": (datetime.now() - timedelta(weeks=2)).isoformat(),
                "status": "completed"
            }
        ]
        
        return ClientDashboardResponse(
            metrics=metrics,
            properties=[PropertyMetrics(**prop) for prop in properties],
            credits=[CreditMetrics(**credit) for credit in credits],
            investments=[InvestmentMetrics(**inv) for inv in investments],
            recent_activity=recent_activity
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener dashboard del cliente: {str(e)}"
        )

@router.get("/properties")
async def get_client_properties(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener propiedades del cliente
    """
    try:
        # En producción, filtrar por current_user.id
        properties = SAMPLE_PROPERTIES
        return {"properties": properties}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener propiedades: {str(e)}"
        )

@router.get("/credits")
async def get_client_credits(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener créditos del cliente
    """
    try:
        # En producción, filtrar por current_user.id
        credits = SAMPLE_CREDITS
        return {"credits": credits}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener créditos: {str(e)}"
        )

@router.get("/investments")
async def get_client_investments(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener inversiones del cliente
    """
    try:
        # En producción, filtrar por current_user.id
        investments = SAMPLE_INVESTMENTS
        return {"investments": investments}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inversiones: {str(e)}"
        )

@router.get("/metrics")
async def get_client_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener métricas financieras del cliente
    """
    try:
        # Calcular métricas basadas en los datos del usuario
        properties = SAMPLE_PROPERTIES
        credits = SAMPLE_CREDITS
        investments = SAMPLE_INVESTMENTS
        
        total_property_value = sum(prop["price"] for prop in properties)
        monthly_rental_income = sum(
            prop.get("monthly_income", 0) for prop in properties 
            if prop["transaction_type"] == "alquiler" and prop["status"] == "alquilado"
        )
        total_credits = sum(credit["remaining_balance"] for credit in credits)
        total_investments = sum(inv["amount"] for inv in investments)
        net_worth = total_property_value + total_investments - total_credits
        
        metrics = {
            "total_property_value": total_property_value,
            "monthly_rental_income": monthly_rental_income,
            "total_credits": total_credits,
            "total_investments": total_investments,
            "net_worth": net_worth,
            "portfolio_growth": 12.5,
            "annual_rental_income": monthly_rental_income * 12,
            "annual_investment_returns": sum(inv["monthly_return"] * 12 for inv in investments),
            "annual_credit_payments": sum(
                credit["monthly_payment"] * 12 for credit in credits 
                if credit["status"] == "aprobado"
            )
        }
        
        return {"metrics": metrics}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular métricas: {str(e)}"
        ) 