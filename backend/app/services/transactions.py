from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from nhost import NhostClient
from ..models import (
    Offer, OfferCreate, OfferUpdate,
    RentalContract, RentalContractCreate, RentalContractUpdate,
    SaleContract, SaleContractCreate, SaleContractUpdate,
    Payment, PaymentCreate, PaymentUpdate
)

class TransactionService:
    def __init__(self, nhost: NhostClient):
        self.nhost = nhost

    # Gestión de Ofertas
    async def create_offer(self, offer_data: OfferCreate) -> Offer:
        """Crear una nueva oferta"""
        query = """
        mutation CreateOffer($offer: offers_insert_input!) {
            insert_offers_one(object: $offer) {
                id
                property_id
                client_id
                amount
                currency
                status
                notes
                conditions
                valid_until
                agent_id
                created_at
                updated_at
                counter_offers
            }
        }
        """
        variables = {"offer": offer_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return Offer(**result["data"]["insert_offers_one"])

    async def update_offer(self, offer_id: UUID, offer_data: OfferUpdate) -> Optional[Offer]:
        """Actualizar una oferta"""
        query = """
        mutation UpdateOffer($id: uuid!, $offer: offers_set_input!) {
            update_offers_by_pk(pk_columns: {id: $id}, _set: $offer) {
                id
                property_id
                client_id
                amount
                currency
                status
                notes
                conditions
                valid_until
                agent_id
                created_at
                updated_at
                counter_offers
            }
        }
        """
        variables = {
            "id": str(offer_id),
            "offer": {k: v for k, v in offer_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        offer_data = result["data"]["update_offers_by_pk"]
        return Offer(**offer_data) if offer_data else None

    async def get_offers_by_property(self, property_id: UUID) -> List[Offer]:
        """Obtener todas las ofertas de una propiedad"""
        query = """
        query GetOffersByProperty($property_id: uuid!) {
            offers(where: {property_id: {_eq: $property_id}}) {
                id
                property_id
                client_id
                amount
                currency
                status
                notes
                conditions
                valid_until
                agent_id
                created_at
                updated_at
                counter_offers
            }
        }
        """
        variables = {"property_id": str(property_id)}
        result = await self.nhost.graphql.request(query, variables)
        return [Offer(**offer) for offer in result["data"]["offers"]]

    # Gestión de Contratos de Alquiler
    async def create_rental_contract(self, contract_data: RentalContractCreate) -> RentalContract:
        """Crear un nuevo contrato de alquiler"""
        query = """
        mutation CreateRentalContract($contract: rental_contracts_insert_input!) {
            insert_rental_contracts_one(object: $contract) {
                id
                property_id
                tenant_id
                owner_id
                start_date
                end_date
                monthly_rent
                currency
                deposit_amount
                status
                terms
                agent_id
                created_at
                updated_at
                payment_history
                maintenance_requests
            }
        }
        """
        variables = {"contract": contract_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return RentalContract(**result["data"]["insert_rental_contracts_one"])

    async def update_rental_contract(self, contract_id: UUID, contract_data: RentalContractUpdate) -> Optional[RentalContract]:
        """Actualizar un contrato de alquiler"""
        query = """
        mutation UpdateRentalContract($id: uuid!, $contract: rental_contracts_set_input!) {
            update_rental_contracts_by_pk(pk_columns: {id: $id}, _set: $contract) {
                id
                property_id
                tenant_id
                owner_id
                start_date
                end_date
                monthly_rent
                currency
                deposit_amount
                status
                terms
                agent_id
                created_at
                updated_at
                payment_history
                maintenance_requests
            }
        }
        """
        variables = {
            "id": str(contract_id),
            "contract": {k: v for k, v in contract_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        contract_data = result["data"]["update_rental_contracts_by_pk"]
        return RentalContract(**contract_data) if contract_data else None

    # Gestión de Contratos de Venta
    async def create_sale_contract(self, contract_data: SaleContractCreate) -> SaleContract:
        """Crear un nuevo contrato de venta"""
        query = """
        mutation CreateSaleContract($contract: sale_contracts_insert_input!) {
            insert_sale_contracts_one(object: $contract) {
                id
                property_id
                buyer_id
                seller_id
                sale_price
                currency
                status
                closing_date
                terms
                agent_id
                commission_rate
                commission_amount
                created_at
                updated_at
                payment_history
                documents
            }
        }
        """
        variables = {"contract": contract_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return SaleContract(**result["data"]["insert_sale_contracts_one"])

    async def update_sale_contract(self, contract_id: UUID, contract_data: SaleContractUpdate) -> Optional[SaleContract]:
        """Actualizar un contrato de venta"""
        query = """
        mutation UpdateSaleContract($id: uuid!, $contract: sale_contracts_set_input!) {
            update_sale_contracts_by_pk(pk_columns: {id: $id}, _set: $contract) {
                id
                property_id
                buyer_id
                seller_id
                sale_price
                currency
                status
                closing_date
                terms
                agent_id
                commission_rate
                commission_amount
                created_at
                updated_at
                payment_history
                documents
            }
        }
        """
        variables = {
            "id": str(contract_id),
            "contract": {k: v for k, v in contract_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        contract_data = result["data"]["update_sale_contracts_by_pk"]
        return SaleContract(**contract_data) if contract_data else None

    # Gestión de Pagos
    async def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Crear un nuevo pago"""
        query = """
        mutation CreatePayment($payment: payments_insert_input!) {
            insert_payments_one(object: $payment) {
                id
                contract_id
                contract_type
                amount
                currency
                payment_date
                payment_method
                status
                reference
                notes
                created_at
                updated_at
                transaction_id
            }
        }
        """
        variables = {"payment": payment_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return Payment(**result["data"]["insert_payments_one"])

    async def update_payment(self, payment_id: UUID, payment_data: PaymentUpdate) -> Optional[Payment]:
        """Actualizar un pago"""
        query = """
        mutation UpdatePayment($id: uuid!, $payment: payments_set_input!) {
            update_payments_by_pk(pk_columns: {id: $id}, _set: $payment) {
                id
                contract_id
                contract_type
                amount
                currency
                payment_date
                payment_method
                status
                reference
                notes
                created_at
                updated_at
                transaction_id
            }
        }
        """
        variables = {
            "id": str(payment_id),
            "payment": {k: v for k, v in payment_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        payment_data = result["data"]["update_payments_by_pk"]
        return Payment(**payment_data) if payment_data else None

    async def get_payments_by_contract(self, contract_id: UUID, contract_type: str) -> List[Payment]:
        """Obtener todos los pagos de un contrato"""
        query = """
        query GetPaymentsByContract($contract_id: uuid!, $contract_type: String!) {
            payments(where: {contract_id: {_eq: $contract_id}, contract_type: {_eq: $contract_type}}) {
                id
                contract_id
                contract_type
                amount
                currency
                payment_date
                payment_method
                status
                reference
                notes
                created_at
                updated_at
                transaction_id
            }
        }
        """
        variables = {
            "contract_id": str(contract_id),
            "contract_type": contract_type
        }
        result = await self.nhost.graphql.request(query, variables)
        return [Payment(**payment) for payment in result["data"]["payments"]] 