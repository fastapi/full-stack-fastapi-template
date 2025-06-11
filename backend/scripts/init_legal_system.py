#!/usr/bin/env python3
"""
Script de inicialización del Sistema de Cumplimiento Legal
GENIUS INDUSTRIES

Este script configura:
1. Templates de contratos con branding corporativo
2. Políticas de protección de datos
3. Configuración inicial del sistema legal
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path para importar módulos de la app
sys.path.append(str(Path(__file__).parent.parent))

from app.services.legal import LegalComplianceService
from app.models import LegalDocumentTemplateCreate, LegalDocumentType
from uuid import uuid4

class LegalSystemInitializer:
    def __init__(self):
        self.legal_service = LegalComplianceService()
        self.admin_user_id = uuid4()  # En producción, usar ID de CEO real
    
    def get_corporate_header(self) -> str:
        """Header corporativo con logo GENIUS INDUSTRIES"""
        return """
        <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
            <div style="margin-bottom: 15px;">
                <!-- GENIUS INDUSTRIES LOGO -->
                <div style="width: 200px; height: 80px; background-color: #000000; color: #FFFFFF; 
                           display: inline-block; line-height: 80px; font-weight: bold; font-size: 20px;">
                    GENIUS INDUSTRIES
                </div>
            </div>
            <h1 style="color: #000000; font-family: Arial, sans-serif; margin: 5px 0; font-size: 24px;">
                GENIUS INDUSTRIES
            </h1>
            <p style="color: #666666; margin: 5px 0; font-size: 12px;">
                Servicios Inmobiliarios y Financieros | Tel: +1 (555) 123-4567 | info@genius-industries.com
            </p>
        </div>
        """
    
    def get_corporate_footer(self) -> str:
        """Footer corporativo"""
        return """
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E5E5; text-align: center; font-size: 10px; color: #999999;">
            <p>GENIUS INDUSTRIES - www.genius-industries.com</p>
            <p>Este documento ha sido generado electrónicamente por GENIUS INDUSTRIES</p>
            <p>Documento generado el: {{generation_date}}</p>
        </div>
        """
    
    async def create_sale_contract_template(self):
        """Crear template de contrato de compra-venta"""
        template = LegalDocumentTemplateCreate(
            template_name="Contrato de Compra-Venta Inmobiliaria GENIUS INDUSTRIES",
            document_type=LegalDocumentType.SALE_CONTRACT,
            version="1.0",
            content="""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
                
                <h2 style="color: #000000; text-align: center; margin-bottom: 30px; text-transform: uppercase;">
                    CONTRATO DE COMPRA-VENTA INMOBILIARIA
                </h2>
                
                <div style="background-color: #F5F5F5; padding: 15px; margin-bottom: 20px; border-left: 4px solid #000000;">
                    <p><strong>Documento N°:</strong> {{document_number}}</p>
                    <p><strong>Fecha:</strong> {{generation_date}}</p>
                    <p><strong>Ciudad:</strong> {{contract_city}}</p>
                </div>

                <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">PARTES CONTRATANTES</h3>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #000000;">VENDEDOR:</h4>
                    <p><strong>Nombre:</strong> {{seller_name}}</p>
                    <p><strong>Identificación:</strong> {{seller_id}}</p>
                    <p><strong>Dirección:</strong> {{seller_address}}</p>
                    <p><strong>Teléfono:</strong> {{seller_phone}}</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #000000;">COMPRADOR:</h4>
                    <p><strong>Nombre:</strong> {{buyer_name}}</p>
                    <p><strong>Identificación:</strong> {{buyer_id}}</p>
                    <p><strong>Dirección:</strong> {{buyer_address}}</p>
                    <p><strong>Teléfono:</strong> {{buyer_phone}}</p>
                </div>

                <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">OBJETO DEL CONTRATO</h3>
                
                <div style="background-color: #F9F9F9; padding: 15px; margin: 15px 0; border: 1px solid #E5E5E5;">
                    <p><strong>Dirección:</strong> {{property_address}}</p>
                    <p><strong>Área:</strong> {{property_area}} metros cuadrados</p>
                    <p><strong>Tipo:</strong> {{property_type}}</p>
                    <p><strong>Matrícula:</strong> {{property_registry}}</p>
                </div>

                <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">PRECIO Y PAGO</h3>
                
                <div style="background-color: #F0F8FF; padding: 15px; margin: 15px 0; border: 1px solid #B0D4F1;">
                    <p style="font-size: 18px;"><strong>PRECIO TOTAL:</strong></p>
                    <p style="font-size: 20px; color: #000000; font-weight: bold;">{{currency}} {{sale_price}}</p>
                    <p><em>({{sale_price_words}})</em></p>
                </div>
                
                <p><strong>Forma de Pago:</strong> {{payment_method}}</p>

                <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">FIRMAS</h3>
                
                <div style="margin-top: 60px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 40px;">
                        <div style="text-align: center; width: 45%;">
                            <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                                <strong>{{seller_name}}</strong>
                            </div>
                            <p style="font-size: 12px;">VENDEDOR - {{seller_id}}</p>
                        </div>
                        <div style="text-align: center; width: 45%;">
                            <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                                <strong>{{buyer_name}}</strong>
                            </div>
                            <p style="font-size: 12px;">COMPRADOR - {{buyer_id}}</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px; width: 300px; margin: 0 auto;">
                            <strong>GENIUS INDUSTRIES</strong>
                        </div>
                        <p style="font-size: 12px;">INTERMEDIARIO INMOBILIARIO</p>
                    </div>
                </div>
            </div>
            """,
            variables={
                "contract_city": {"type": "string", "required": True, "description": "Ciudad del contrato"},
                "seller_name": {"type": "string", "required": True, "description": "Nombre del vendedor"},
                "seller_id": {"type": "string", "required": True, "description": "ID del vendedor"},
                "seller_address": {"type": "string", "required": True, "description": "Dirección del vendedor"},
                "seller_phone": {"type": "string", "required": True, "description": "Teléfono del vendedor"},
                "buyer_name": {"type": "string", "required": True, "description": "Nombre del comprador"},
                "buyer_id": {"type": "string", "required": True, "description": "ID del comprador"},
                "buyer_address": {"type": "string", "required": True, "description": "Dirección del comprador"},
                "buyer_phone": {"type": "string", "required": True, "description": "Teléfono del comprador"},
                "property_address": {"type": "string", "required": True, "description": "Dirección del inmueble"},
                "property_area": {"type": "number", "required": True, "description": "Área en m²"},
                "property_type": {"type": "string", "required": True, "description": "Tipo de inmueble"},
                "property_registry": {"type": "string", "required": True, "description": "Matrícula inmobiliaria"},
                "currency": {"type": "string", "required": True, "description": "Moneda"},
                "sale_price": {"type": "number", "required": True, "description": "Precio de venta"},
                "sale_price_words": {"type": "string", "required": True, "description": "Precio en palabras"},
                "payment_method": {"type": "string", "required": True, "description": "Forma de pago"}
            },
            created_by=self.admin_user_id
        )
        
        try:
            result = await self.legal_service.create_template(template)
            print(f"✅ Template de compra-venta creado: {result.template_name}")
            return result
        except Exception as e:
            print(f"❌ Error creando template de compra-venta: {e}")
            return None
    
    async def create_rental_contract_template(self):
        """Crear template de contrato de arrendamiento"""
        template = LegalDocumentTemplateCreate(
            template_name="Contrato de Arrendamiento GENIUS INDUSTRIES",
            document_type=LegalDocumentType.RENTAL_CONTRACT,
            version="1.0",
            content="""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
                
                <h2 style="color: #000000; text-align: center; margin-bottom: 30px; text-transform: uppercase;">
                    CONTRATO DE ARRENDAMIENTO
                </h2>
                
                <div style="background-color: #F5F5F5; padding: 15px; margin-bottom: 20px; border-left: 4px solid #000000;">
                    <p><strong>Documento N°:</strong> {{document_number}}</p>
                    <p><strong>Fecha:</strong> {{generation_date}}</p>
                    <p><strong>Vigencia:</strong> {{contract_duration}} meses</p>
                </div>

                <h3>ARRENDADOR:</h3>
                <p><strong>{{landlord_name}}</strong> - {{landlord_id}}</p>
                <p>{{landlord_address}}</p>
                
                <h3>ARRENDATARIO:</h3>
                <p><strong>{{tenant_name}}</strong> - {{tenant_id}}</p>
                <p>{{tenant_address}}</p>
                
                <h3>INMUEBLE ARRENDADO:</h3>
                <div style="background-color: #F9F9F9; padding: 15px; margin: 15px 0; border: 1px solid #E5E5E5;">
                    <p><strong>Dirección:</strong> {{property_address}}</p>
                    <p><strong>Tipo:</strong> {{property_type}}</p>
                    <p><strong>Área:</strong> {{property_area}} m²</p>
                </div>
                
                <h3>CONDICIONES ECONÓMICAS:</h3>
                <div style="background-color: #F0F8FF; padding: 15px; margin: 15px 0; border: 1px solid #B0D4F1;">
                    <p><strong>Canon Mensual:</strong> {{currency}} {{monthly_rent}}</p>
                    <p><strong>Depósito:</strong> {{currency}} {{security_deposit}}</p>
                    <p><strong>Administración:</strong> {{currency}} {{admin_fee}}</p>
                </div>
                
                <div style="margin-top: 60px; text-align: center;">
                    <div style="display: inline-block; margin: 0 50px;">
                        <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                            <strong>{{landlord_name}}</strong>
                        </div>
                        <p style="font-size: 12px;">ARRENDADOR</p>
                    </div>
                    <div style="display: inline-block; margin: 0 50px;">
                        <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                            <strong>{{tenant_name}}</strong>
                        </div>
                        <p style="font-size: 12px;">ARRENDATARIO</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px;">
                    <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px; width: 300px; margin: 0 auto;">
                        <strong>GENIUS INDUSTRIES</strong>
                    </div>
                    <p style="font-size: 12px;">INMOBILIARIA</p>
                </div>
            </div>
            """,
            variables={
                "landlord_name": {"type": "string", "required": True, "description": "Nombre del arrendador"},
                "landlord_id": {"type": "string", "required": True, "description": "ID del arrendador"},
                "landlord_address": {"type": "string", "required": True, "description": "Dirección del arrendador"},
                "tenant_name": {"type": "string", "required": True, "description": "Nombre del arrendatario"},
                "tenant_id": {"type": "string", "required": True, "description": "ID del arrendatario"},
                "tenant_address": {"type": "string", "required": True, "description": "Dirección del arrendatario"},
                "property_address": {"type": "string", "required": True, "description": "Dirección del inmueble"},
                "property_type": {"type": "string", "required": True, "description": "Tipo de inmueble"},
                "property_area": {"type": "number", "required": True, "description": "Área en m²"},
                "monthly_rent": {"type": "number", "required": True, "description": "Canon mensual"},
                "security_deposit": {"type": "number", "required": True, "description": "Depósito"},
                "admin_fee": {"type": "number", "required": True, "description": "Administración"},
                "contract_duration": {"type": "number", "required": True, "description": "Duración en meses"},
                "currency": {"type": "string", "required": True, "description": "Moneda"}
            },
            created_by=self.admin_user_id
        )
        
        try:
            result = await self.legal_service.create_template(template)
            print(f"✅ Template de arrendamiento creado: {result.template_name}")
            return result
        except Exception as e:
            print(f"❌ Error creando template de arrendamiento: {e}")
            return None
    
    async def create_loan_contract_template(self):
        """Crear template de contrato de préstamo"""
        template = LegalDocumentTemplateCreate(
            template_name="Contrato de Préstamo GENIUS INDUSTRIES",
            document_type=LegalDocumentType.LOAN_CONTRACT,
            version="1.0",
            content="""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
                
                <h2 style="color: #000000; text-align: center; margin-bottom: 30px; text-transform: uppercase;">
                    CONTRATO DE PRÉSTAMO PERSONAL
                </h2>
                
                <div style="background-color: #F5F5F5; padding: 15px; margin-bottom: 20px; border-left: 4px solid #000000;">
                    <p><strong>Documento N°:</strong> {{document_number}}</p>
                    <p><strong>Fecha:</strong> {{generation_date}}</p>
                </div>

                <h3>PRESTAMISTA:</h3>
                <div style="background-color: #000000; color: #FFFFFF; padding: 15px; margin: 10px 0;">
                    <p><strong>GENIUS INDUSTRIES</strong></p>
                    <p>NIT: 900.123.456-7</p>
                    <p>Entidad Financiera Licenciada</p>
                </div>
                
                <h3>PRESTATARIO:</h3>
                <p><strong>{{borrower_name}}</strong> - {{borrower_id}}</p>
                <p>{{borrower_address}}</p>
                <p>Tel: {{borrower_phone}}</p>
                
                <h3>CONDICIONES DEL PRÉSTAMO:</h3>
                <div style="background-color: #F0F8FF; padding: 15px; margin: 15px 0; border: 1px solid #B0D4F1;">
                    <p><strong>Monto del Préstamo:</strong> {{currency}} {{loan_amount}}</p>
                    <p><strong>Tasa de Interés:</strong> {{interest_rate}}% anual</p>
                    <p><strong>Plazo:</strong> {{loan_term}} meses</p>
                    <p><strong>Cuota Mensual:</strong> {{currency}} {{monthly_payment}}</p>
                    <p><strong>Total a Pagar:</strong> {{currency}} {{total_amount}}</p>
                </div>
                
                <h3>GARANTÍAS:</h3>
                <p>{{guarantees}}</p>
                
                <div style="margin-top: 60px; text-align: center;">
                    <div style="display: inline-block; margin: 0 50px;">
                        <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                            <strong>GENIUS INDUSTRIES</strong>
                        </div>
                        <p style="font-size: 12px;">PRESTAMISTA</p>
                    </div>
                    <div style="display: inline-block; margin: 0 50px;">
                        <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                            <strong>{{borrower_name}}</strong>
                        </div>
                        <p style="font-size: 12px;">PRESTATARIO</p>
                    </div>
                </div>
            </div>
            """,
            variables={
                "borrower_name": {"type": "string", "required": True, "description": "Nombre del prestatario"},
                "borrower_id": {"type": "string", "required": True, "description": "ID del prestatario"},
                "borrower_address": {"type": "string", "required": True, "description": "Dirección del prestatario"},
                "borrower_phone": {"type": "string", "required": True, "description": "Teléfono del prestatario"},
                "loan_amount": {"type": "number", "required": True, "description": "Monto del préstamo"},
                "interest_rate": {"type": "number", "required": True, "description": "Tasa de interés anual"},
                "loan_term": {"type": "number", "required": True, "description": "Plazo en meses"},
                "monthly_payment": {"type": "number", "required": True, "description": "Cuota mensual"},
                "total_amount": {"type": "number", "required": True, "description": "Total a pagar"},
                "guarantees": {"type": "string", "required": True, "description": "Garantías del préstamo"},
                "currency": {"type": "string", "required": True, "description": "Moneda"}
            },
            created_by=self.admin_user_id
        )
        
        try:
            result = await self.legal_service.create_template(template)
            print(f"✅ Template de préstamo creado: {result.template_name}")
            return result
        except Exception as e:
            print(f"❌ Error creando template de préstamo: {e}")
            return None
    
    async def initialize_system(self):
        """Inicializar todo el sistema legal"""
        print("🏗️ Inicializando Sistema de Cumplimiento Legal - GENIUS INDUSTRIES")
        print("=" * 60)
        
        # Crear templates
        await self.create_sale_contract_template()
        await self.create_rental_contract_template()
        await self.create_loan_contract_template()
        
        print("=" * 60)
        print("✅ Sistema Legal inicializado correctamente")
        print("\n📋 Templates disponibles:")
        print("   • Contrato de Compra-Venta")
        print("   • Contrato de Arrendamiento")
        print("   • Contrato de Préstamo")
        print("\n🎨 Todos los templates incluyen branding de GENIUS INDUSTRIES")

async def main():
    """Función principal"""
    initializer = LegalSystemInitializer()
    await initializer.initialize_system()

if __name__ == "__main__":
    asyncio.run(main()) 