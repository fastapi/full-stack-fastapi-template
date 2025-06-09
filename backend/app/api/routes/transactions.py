from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from ...models import (
    Offer, OfferCreate, OfferUpdate,
    RentalContract, RentalContractCreate, RentalContractUpdate,
    SaleContract, SaleContractCreate, SaleContractUpdate,
    Payment, PaymentCreate, PaymentUpdate
)
from ...services.transactions import TransactionService
from ..deps import get_current_user, get_transaction_service
from ...models import User

router = APIRouter()

# Endpoints para Ofertas
@router.post("/offers", response_model=Offer)
async def create_offer(
    offer_data: OfferCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Crear una nueva oferta"""
    if current_user.role not in ["agent", "client"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear ofertas")
    
    return await transaction_service.create_offer(offer_data)

@router.put("/offers/{offer_id}", response_model=Offer)
async def update_offer(
    offer_id: UUID,
    offer_data: OfferUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Actualizar una oferta"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar ofertas")
    
    offer = await transaction_service.update_offer(offer_id, offer_data)
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    
    return offer

@router.get("/properties/{property_id}/offers", response_model=List[Offer])
async def get_property_offers(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Obtener todas las ofertas de una propiedad"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver ofertas")
    
    return await transaction_service.get_offers_by_property(property_id)

# Endpoints para Contratos de Alquiler
@router.post("/rentals", response_model=RentalContract)
async def create_rental_contract(
    contract_data: RentalContractCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Crear un nuevo contrato de alquiler"""
    if current_user.role not in ["agent", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear contratos de alquiler")
    
    return await transaction_service.create_rental_contract(contract_data)

@router.put("/rentals/{contract_id}", response_model=RentalContract)
async def update_rental_contract(
    contract_id: UUID,
    contract_data: RentalContractUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Actualizar un contrato de alquiler"""
    if current_user.role not in ["agent", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar contratos de alquiler")
    
    contract = await transaction_service.update_rental_contract(contract_id, contract_data)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return contract

# Endpoints para Contratos de Venta
@router.post("/sales", response_model=SaleContract)
async def create_sale_contract(
    contract_data: SaleContractCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Crear un nuevo contrato de venta"""
    if current_user.role not in ["agent", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear contratos de venta")
    
    return await transaction_service.create_sale_contract(contract_data)

@router.put("/sales/{contract_id}", response_model=SaleContract)
async def update_sale_contract(
    contract_id: UUID,
    contract_data: SaleContractUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Actualizar un contrato de venta"""
    if current_user.role not in ["agent", "manager"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar contratos de venta")
    
    contract = await transaction_service.update_sale_contract(contract_id, contract_data)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    
    return contract

# Endpoints para Pagos
@router.post("/payments", response_model=Payment)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Crear un nuevo pago"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear pagos")
    
    return await transaction_service.create_payment(payment_data)

@router.put("/payments/{payment_id}", response_model=Payment)
async def update_payment(
    payment_id: UUID,
    payment_data: PaymentUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Actualizar un pago"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar pagos")
    
    payment = await transaction_service.update_payment(payment_id, payment_data)
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    return payment

@router.get("/contracts/{contract_id}/payments", response_model=List[Payment])
async def get_contract_payments(
    contract_id: UUID,
    contract_type: str = Query(..., description="Tipo de contrato: 'rental' o 'sale'"),
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)
):
    """Obtener todos los pagos de un contrato"""
    if current_user.role not in ["agent", "manager", "supervisor"]:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver pagos")
    
    return await transaction_service.get_payments_by_contract(contract_id, contract_type) 