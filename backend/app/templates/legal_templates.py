"""
Legal Document Templates for GENIUS INDUSTRIES
Templates include corporate branding and logo placeholders
"""

from typing import Dict, Any

def get_document_header() -> str:
    """Corporate header with GENIUS INDUSTRIES branding"""
    return """
    <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
        <div style="margin-bottom: 15px;">
            <!-- GENIUS INDUSTRIES LOGO -->
            <div style="width: 200px; height: 80px; background-color: #000000; color: #FFFFFF; 
                       display: inline-block; line-height: 80px; font-weight: bold; font-size: 20px; margin: 0 auto;">
                GENIUS INDUSTRIES
            </div>
        </div>
        <h1 style="color: #000000; font-family: 'Arial', sans-serif; margin: 5px 0; font-size: 24px; font-weight: bold;">
            GENIUS INDUSTRIES
        </h1>
        <p style="color: #666666; margin: 5px 0; font-size: 12px;">
            Servicios Inmobiliarios y Financieros | Tel: +1 (555) 123-4567 | info@genius-industries.com
        </p>
    </div>
    """

def get_document_footer() -> str:
    """Corporate footer"""
    return """
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E5E5; text-align: center; font-size: 10px; color: #999999;">
        <p>GENIUS INDUSTRIES - www.genius-industries.com</p>
        <p>Este documento ha sido generado electrónicamente y es válido sin firma física</p>
        <p>Documento generado el: {{generation_date}}</p>
    </div>
    """

# SALE CONTRACT TEMPLATE
SALE_CONTRACT_TEMPLATE = {
    "template_name": "Contrato de Compra-Venta Inmobiliaria",
    "document_type": "sale_contract",
    "version": "1.0",
    "content": get_document_header() + """
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
        
        <h2 style="color: #000000; text-align: center; margin-bottom: 30px; text-transform: uppercase;">
            CONTRATO DE COMPRA-VENTA INMOBILIARIA
        </h2>
        
        <div style="background-color: #F5F5F5; padding: 15px; margin-bottom: 20px; border-left: 4px solid #000000;">
            <p><strong>Documento N°:</strong> {{document_number}}</p>
            <p><strong>Fecha de Generación:</strong> {{generation_date}}</p>
            <p><strong>Lugar:</strong> {{contract_city}}</p>
        </div>

        <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">I. IDENTIFICACIÓN DE LAS PARTES</h3>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #000000;">VENDEDOR:</h4>
            <p><strong>Nombre:</strong> {{seller_name}}</p>
            <p><strong>Identificación:</strong> {{seller_id}}</p>
            <p><strong>Dirección:</strong> {{seller_address}}</p>
            <p><strong>Teléfono:</strong> {{seller_phone}}</p>
            <p><strong>Email:</strong> {{seller_email}}</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <h4 style="color: #000000;">COMPRADOR:</h4>
            <p><strong>Nombre:</strong> {{buyer_name}}</p>
            <p><strong>Identificación:</strong> {{buyer_id}}</p>
            <p><strong>Dirección:</strong> {{buyer_address}}</p>
            <p><strong>Teléfono:</strong> {{buyer_phone}}</p>
            <p><strong>Email:</strong> {{buyer_email}}</p>
        </div>

        <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">II. OBJETO DEL CONTRATO</h3>
        
        <p>El VENDEDOR declara ser propietario del inmueble que por este contrato vende al COMPRADOR, ubicado en:</p>
        
        <div style="background-color: #F9F9F9; padding: 15px; margin: 15px 0; border: 1px solid #E5E5E5;">
            <p><strong>Dirección:</strong> {{property_address}}</p>
            <p><strong>Ciudad:</strong> {{property_city}}</p>
            <p><strong>Área Total:</strong> {{property_area}} metros cuadrados</p>
            <p><strong>Área Construida:</strong> {{property_built_area}} metros cuadrados</p>
            <p><strong>Tipo de Inmueble:</strong> {{property_type}}</p>
            <p><strong>Matrícula Inmobiliaria:</strong> {{property_registry}}</p>
            <p><strong>Linderos:</strong> {{property_boundaries}}</p>
        </div>

        <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">III. PRECIO Y FORMA DE PAGO</h3>
        
        <div style="background-color: #F0F8FF; padding: 15px; margin: 15px 0; border: 1px solid #B0D4F1;">
            <p style="font-size: 18px;"><strong>PRECIO TOTAL DE VENTA:</strong></p>
            <p style="font-size: 20px; color: #000000; font-weight: bold;">{{currency}} {{sale_price}}</p>
            <p><em>({{sale_price_words}})</em></p>
        </div>
        
        <p><strong>Forma de Pago:</strong> {{payment_method}}</p>
        <p><strong>Fecha de Pago:</strong> {{payment_date}}</p>
        
        {% if down_payment %}
        <p><strong>Cuota Inicial:</strong> {{currency}} {{down_payment}}</p>
        <p><strong>Saldo:</strong> {{currency}} {{balance_amount}}</p>
        {% endif %}

        <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">IV. OBLIGACIONES DE LAS PARTES</h3>
        
        <h4>Obligaciones del Vendedor:</h4>
        <ul>
            <li>Entregar el inmueble libre de gravámenes y limitaciones</li>
            <li>Proporcionar todos los documentos de propiedad</li>
            <li>Garantizar la paz y tranquilidad en el dominio</li>
            <li>{{seller_obligations}}</li>
        </ul>
        
        <h4>Obligaciones del Comprador:</h4>
        <ul>
            <li>Pagar el precio acordado en la forma convenida</li>
            <li>Recibir el inmueble en el estado en que se encuentra</li>
            <li>Asumir los gastos de escrituración y registro</li>
            <li>{{buyer_obligations}}</li>
        </ul>

        <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">V. CLÁUSULAS ESPECIALES</h3>
        <p>{{special_clauses}}</p>

        <h3 style="color: #000000; border-bottom: 1px solid #E5E5E5; padding-bottom: 5px;">VI. FIRMAS</h3>
        
        <div style="margin-top: 60px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 40px;">
                <div style="text-align: center; width: 45%;">
                    <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                        <strong>{{seller_name}}</strong>
                    </div>
                    <p style="font-size: 12px;">VENDEDOR<br>{{seller_id}}</p>
                </div>
                <div style="text-align: center; width: 45%;">
                    <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px;">
                        <strong>{{buyer_name}}</strong>
                    </div>
                    <p style="font-size: 12px;">COMPRADOR<br>{{buyer_id}}</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <div style="border-top: 1px solid #000000; margin-bottom: 10px; padding-top: 5px; width: 300px; margin: 0 auto;">
                    <strong>GENIUS INDUSTRIES</strong>
                </div>
                <p style="font-size: 12px;">INTERMEDIARIO INMOBILIARIO<br>Licencia No. {{intermediary_license}}</p>
            </div>
        </div>
        
        <div style="margin-top: 30px; font-size: 10px; color: #666666;">
            <p><strong>Testigos:</strong></p>
            <div style="display: flex; justify-content: space-between;">
                <div>_________________________<br>{{witness1_name}}<br>{{witness1_id}}</div>
                <div>_________________________<br>{{witness2_name}}<br>{{witness2_id}}</div>
            </div>
        </div>
    </div>
    """ + get_document_footer(),
    
    "variables": {
        "contract_city": {"type": "string", "required": True, "description": "Ciudad donde se firma el contrato"},
        "seller_name": {"type": "string", "required": True, "description": "Nombre completo del vendedor"},
        "seller_id": {"type": "string", "required": True, "description": "Número de identificación del vendedor"},
        "seller_address": {"type": "string", "required": True, "description": "Dirección del vendedor"},
        "seller_phone": {"type": "string", "required": True, "description": "Teléfono del vendedor"},
        "seller_email": {"type": "string", "required": True, "description": "Email del vendedor"},
        "buyer_name": {"type": "string", "required": True, "description": "Nombre completo del comprador"},
        "buyer_id": {"type": "string", "required": True, "description": "Número de identificación del comprador"},
        "buyer_address": {"type": "string", "required": True, "description": "Dirección del comprador"},
        "buyer_phone": {"type": "string", "required": True, "description": "Teléfono del comprador"},
        "buyer_email": {"type": "string", "required": True, "description": "Email del comprador"},
        "property_address": {"type": "string", "required": True, "description": "Dirección completa del inmueble"},
        "property_city": {"type": "string", "required": True, "description": "Ciudad del inmueble"},
        "property_area": {"type": "number", "required": True, "description": "Área total en metros cuadrados"},
        "property_built_area": {"type": "number", "required": True, "description": "Área construida en metros cuadrados"},
        "property_type": {"type": "string", "required": True, "description": "Tipo de inmueble (casa, apartamento, lote, etc.)"},
        "property_registry": {"type": "string", "required": True, "description": "Matrícula inmobiliaria"},
        "property_boundaries": {"type": "string", "required": True, "description": "Linderos del inmueble"},
        "currency": {"type": "string", "required": True, "description": "Moneda (COP, USD, etc.)"},
        "sale_price": {"type": "number", "required": True, "description": "Precio de venta en números"},
        "sale_price_words": {"type": "string", "required": True, "description": "Precio de venta en palabras"},
        "payment_method": {"type": "string", "required": True, "description": "Forma de pago"},
        "payment_date": {"type": "string", "required": True, "description": "Fecha de pago"},
        "down_payment": {"type": "number", "required": False, "description": "Cuota inicial"},
        "balance_amount": {"type": "number", "required": False, "description": "Saldo pendiente"},
        "seller_obligations": {"type": "string", "required": False, "description": "Obligaciones adicionales del vendedor"},
        "buyer_obligations": {"type": "string", "required": False, "description": "Obligaciones adicionales del comprador"},
        "special_clauses": {"type": "string", "required": False, "description": "Cláusulas especiales del contrato"},
        "intermediary_license": {"type": "string", "required": True, "description": "Número de licencia del intermediario"},
        "witness1_name": {"type": "string", "required": False, "description": "Nombre del primer testigo"},
        "witness1_id": {"type": "string", "required": False, "description": "ID del primer testigo"},
        "witness2_name": {"type": "string", "required": False, "description": "Nombre del segundo testigo"},
        "witness2_id": {"type": "string", "required": False, "description": "ID del segundo testigo"}
    }
}

# RENTAL CONTRACT TEMPLATE
RENTAL_CONTRACT_TEMPLATE = {
    "template_name": "Contrato de Arrendamiento",
    "document_type": "rental_contract",
    "version": "1.0",
    "content": get_document_header() + """
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
        <p>{{landlord_name}} - {{landlord_id}}</p>
        
        <h3>ARRENDATARIO:</h3>
        <p>{{tenant_name}} - {{tenant_id}}</p>
        
        <h3>INMUEBLE:</h3>
        <p>{{property_address}}</p>
        
        <h3>CANON DE ARRENDAMIENTO:</h3>
        <p><strong>{{currency}} {{monthly_rent}}</strong> mensuales</p>
        
        <h3>DEPÓSITO:</h3>
        <p>{{currency}} {{security_deposit}}</p>
        
        <div style="margin-top: 60px; text-align: center;">
            <div style="display: inline-block; margin: 0 50px;">
                <p>_________________________</p>
                <p><strong>{{landlord_name}}</strong><br>ARRENDADOR</p>
            </div>
            <div style="display: inline-block; margin: 0 50px;">
                <p>_________________________</p>
                <p><strong>{{tenant_name}}</strong><br>ARRENDATARIO</p>
            </div>
        </div>
    </div>
    """ + get_document_footer(),
    
    "variables": {
        "landlord_name": {"type": "string", "required": True, "description": "Nombre del arrendador"},
        "landlord_id": {"type": "string", "required": True, "description": "ID del arrendador"},
        "tenant_name": {"type": "string", "required": True, "description": "Nombre del arrendatario"},
        "tenant_id": {"type": "string", "required": True, "description": "ID del arrendatario"},
        "property_address": {"type": "string", "required": True, "description": "Dirección del inmueble"},
        "monthly_rent": {"type": "number", "required": True, "description": "Canon mensual"},
        "security_deposit": {"type": "number", "required": True, "description": "Depósito de garantía"},
        "contract_duration": {"type": "number", "required": True, "description": "Duración en meses"},
        "currency": {"type": "string", "required": True, "description": "Moneda"}
    }
}

# LOAN CONTRACT TEMPLATE
LOAN_CONTRACT_TEMPLATE = {
    "template_name": "Contrato de Préstamo Personal",
    "document_type": "loan_contract",
    "version": "1.0",
    "content": get_document_header() + """
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
        
        <h2 style="color: #000000; text-align: center; margin-bottom: 30px; text-transform: uppercase;">
            CONTRATO DE PRÉSTAMO PERSONAL
        </h2>
        
        <div style="background-color: #F5F5F5; padding: 15px; margin-bottom: 20px; border-left: 4px solid #000000;">
            <p><strong>Documento N°:</strong> {{document_number}}</p>
            <p><strong>Fecha:</strong> {{generation_date}}</p>
        </div>

        <h3>PRESTAMISTA:</h3>
        <p><strong>GENIUS INDUSTRIES</strong></p>
        <p>NIT: 900.123.456-7</p>
        
        <h3>PRESTATARIO:</h3>
        <p>{{borrower_name}} - {{borrower_id}}</p>
        <p>{{borrower_address}}</p>
        
        <h3>CONDICIONES DEL PRÉSTAMO:</h3>
        <div style="background-color: #F0F8FF; padding: 15px; margin: 15px 0; border: 1px solid #B0D4F1;">
            <p><strong>Monto:</strong> {{currency}} {{loan_amount}}</p>
            <p><strong>Tasa de Interés:</strong> {{interest_rate}}% anual</p>
            <p><strong>Plazo:</strong> {{loan_term}} meses</p>
            <p><strong>Cuota Mensual:</strong> {{currency}} {{monthly_payment}}</p>
        </div>
        
        <div style="margin-top: 60px; text-align: center;">
            <div style="display: inline-block; margin: 0 50px;">
                <p>_________________________</p>
                <p><strong>GENIUS INDUSTRIES</strong><br>PRESTAMISTA</p>
            </div>
            <div style="display: inline-block; margin: 0 50px;">
                <p>_________________________</p>
                <p><strong>{{borrower_name}}</strong><br>PRESTATARIO</p>
            </div>
        </div>
    </div>
    """ + get_document_footer(),
    
    "variables": {
        "borrower_name": {"type": "string", "required": True, "description": "Nombre del prestatario"},
        "borrower_id": {"type": "string", "required": True, "description": "ID del prestatario"},
        "borrower_address": {"type": "string", "required": True, "description": "Dirección del prestatario"},
        "loan_amount": {"type": "number", "required": True, "description": "Monto del préstamo"},
        "interest_rate": {"type": "number", "required": True, "description": "Tasa de interés anual"},
        "loan_term": {"type": "number", "required": True, "description": "Plazo en meses"},
        "monthly_payment": {"type": "number", "required": True, "description": "Cuota mensual"},
        "currency": {"type": "string", "required": True, "description": "Moneda"}
    }
}

# Export all templates
LEGAL_TEMPLATES = [
    SALE_CONTRACT_TEMPLATE,
    RENTAL_CONTRACT_TEMPLATE,
    LOAN_CONTRACT_TEMPLATE
] 