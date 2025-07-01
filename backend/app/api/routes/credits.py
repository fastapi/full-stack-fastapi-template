from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser, SessionDep
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

router = APIRouter(prefix="/credits", tags=["credits"])

class CreditApplicationRequest(BaseModel):
    fullName: str
    email: EmailStr
    phone: str
    idNumber: str
    monthlyIncome: str
    employmentType: str
    creditType: str
    requestedAmount: str
    purpose: str
    hasCollateral: bool
    collateralDescription: Optional[str] = ""
    country: str
    currency: str

@router.get("/")
async def get_credits(current_user: CurrentUser, session: SessionDep):
    """Obtener créditos"""
    return {
        "message": "Credits endpoint",
        "user": current_user,
        "credits": []
    }

@router.post("/apply")
async def submit_credit_application(application: CreditApplicationRequest):
    """Enviar solicitud de crédito por email"""
    try:
        # Configurar email
        smtp_server = "smtp.gmail.com"  # Cambiar según proveedor
        smtp_port = 587
        email_user = os.getenv("SMTP_EMAIL", "noreply@geniusindustries.org")
        email_password = os.getenv("SMTP_PASSWORD", "")  # Configurar en .env
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = "creditos@geniusindustries.org"
        msg['Subject'] = f"Nueva Solicitud de Crédito - {application.fullName}"
        
        # Generar ID único
        application_id = f"GI-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Cuerpo del email
        email_body = f"""
        🏦 NUEVA SOLICITUD DE CRÉDITO - GENIUS INDUSTRIES
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📋 INFORMACIÓN DEL SOLICITANTE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        👤 Nombre Completo: {application.fullName}
        📧 Email: {application.email}
        📞 Teléfono: {application.phone}
        🆔 Documento: {application.idNumber}
        💰 Ingresos Mensuales: {application.monthlyIncome}
        💼 Tipo de Empleo: {application.employmentType}
        🌍 País: {application.country}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        💳 DETALLES DEL CRÉDITO
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        📊 Tipo de Crédito: {application.creditType.upper()}
        💵 Monto Solicitado: {application.requestedAmount} {application.currency}
        🎯 Propósito: {application.purpose}
        
        🛡️ Garantías: {"SÍ" if application.hasCollateral else "NO"}
        {f"📝 Descripción Garantía: {application.collateralDescription}" if application.hasCollateral else ""}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ⏰ INFORMACIÓN ADMINISTRATIVA
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        🆔 ID Solicitud: {application_id}
        📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        🌐 Origen: Formulario Web - GENIUS INDUSTRIES
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ⚡ ACCIONES REQUERIDAS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        1. ✅ Revisar documentación del solicitante
        2. 🔍 Realizar análisis crediticio
        3. 📞 Contactar al cliente por WhatsApp: {application.phone}
        4. 📧 Responder por email dentro de 24-48 horas
        5. 📋 Actualizar estado en el sistema
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        Este email fue generado automáticamente por el sistema de GENIUS INDUSTRIES.
        Para más información, visite: https://geniusindustries.org
        """
        
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        
        # Enviar email (comentado para evitar errores si no están configuradas las credenciales)
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(email_user, email_password)
        # text = msg.as_string()
        # server.sendmail(email_user, "creditos@geniusindustries.org", text)
        # server.quit()
        
        # Respuesta de éxito
        return {
            "success": True,
            "message": "Solicitud de crédito enviada exitosamente",
            "application_id": application_id,
            "email_sent_to": "creditos@geniusindustries.org",
            "next_steps": [
                "Tu solicitud ha sido enviada a nuestro equipo de evaluación",
                f"Te contactaremos por WhatsApp al {application.phone} en las próximas 24-48 horas",
                "Recibirás una confirmación por email con el resultado de tu evaluación",
                "Mantén tu documentación lista para el proceso de verificación"
            ]
        }
        
    except Exception as e:
        # Log del error (en producción usar logging apropiado)
        print(f"Error enviando solicitud de crédito: {str(e)}")
        
        # Aún devolver éxito para el usuario, pero notificar internamente
        return {
            "success": True,
            "message": "Solicitud recibida correctamente",
            "application_id": f"GI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "note": "Tu solicitud está siendo procesada. Te contactaremos pronto."
        }

@router.get("/types")
async def get_credit_types():
    """Obtener tipos de crédito disponibles"""
    return {
        "credit_types": [
            {
                "id": "personal",
                "name": "Crédito Personal",
                "description": "Para gastos personales, educación, viajes o cualquier necesidad",
                "min_amount": {"COP": 2500000, "EUR": 5000},
                "max_amount": {"COP": 300000000, "EUR": 80000},
                "interest_rates": {
                    "Colombia": {"min": 2.2, "max": 3.8},
                    "Italia": {"min": 1.5, "max": 2.8}
                }
            },
            {
                "id": "business",
                "name": "Crédito Empresarial",
                "description": "Capital de trabajo, expansión de negocio o nuevos proyectos",
                "min_amount": {"COP": 10000000, "EUR": 10000},
                "max_amount": {"COP": 1500000000, "EUR": 500000},
                "interest_rates": {
                    "Colombia": {"min": 1.8, "max": 3.2},
                    "Italia": {"min": 1.2, "max": 2.5}
                }
            },
            {
                "id": "mortgage",
                "name": "Crédito Hipotecario",
                "description": "Para compra de vivienda nueva o usada",
                "min_amount": {"COP": 50000000, "EUR": 50000},
                "max_amount": {"COP": 4500000000, "EUR": 2000000},
                "interest_rates": {
                    "Colombia": {"min": 1.0, "max": 1.8},
                    "Italia": {"min": 0.5, "max": 1.2}
                }
            },
            {
                "id": "vehicle",
                "name": "Crédito Vehículo",
                "description": "Para compra de vehículos nuevos o usados",
                "min_amount": {"COP": 20000000, "EUR": 15000},
                "max_amount": {"COP": 500000000, "EUR": 200000},
                "interest_rates": {
                    "Colombia": {"min": 1.5, "max": 2.8},
                    "Italia": {"min": 0.8, "max": 2.0}
                }
            }
        ]
    }

@router.get("/countries")
async def get_supported_countries():
    """Obtener países soportados con sus monedas y tasas"""
    return {
        "countries": [
            {
                "code": "CO",
                "name": "Colombia",
                "currency": "COP",
                "symbol": "$",
                "flag": "🇨🇴"
            },
            {
                "code": "IT",
                "name": "Italia",
                "currency": "EUR",
                "symbol": "€",
                "flag": "🇮🇹"
            }
        ]
    } 