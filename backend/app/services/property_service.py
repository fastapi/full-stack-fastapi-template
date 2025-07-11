from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, func
from fastapi import HTTPException
import uuid

from app.core.db import engine
from app.models import User

# Como no tenemos ORM, usaremos consultas SQL directas con el motor de base de datos
# Esto sigue las reglas del proyecto de no usar ORM

class PropertyService:
    @staticmethod
    async def create_property(property_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Crear una nueva propiedad en PostgreSQL"""
        try:
            with Session(engine) as session:
                # Ejecutar INSERT SQL directo
                property_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                # SQL directo para insertar propiedad
                sql = """
                    INSERT INTO properties (
                        id, title, description, property_type, status, price, currency,
                        address, city, state, country, zip_code, bedrooms, bathrooms, area,
                        features, amenities, images, latitude, longitude, year_built,
                        condition, parking_spaces, agent_id, owner_id, created_at, updated_at,
                        views, favorites, visits
                    ) VALUES (
                        :id, :title, :description, :property_type, :status, :price, :currency,
                        :address, :city, :state, :country, :zip_code, :bedrooms, :bathrooms, :area,
                        :features, :amenities, :images, :latitude, :longitude, :year_built,
                        :condition, :parking_spaces, :agent_id, :owner_id, :created_at, :updated_at,
                        0, 0, 0
                    )
                    RETURNING *
                """
                
                result = session.execute(sql, {
                    "id": property_id,
                    "title": property_data.get("title", ""),
                    "description": property_data.get("description", ""),
                    "property_type": property_data.get("property_type", "apartment"),
                    "status": property_data.get("status", "available"),
                    "price": property_data.get("price", 0),
                    "currency": property_data.get("currency", "USD"),
                    "address": property_data.get("address", ""),
                    "city": property_data.get("city", ""),
                    "state": property_data.get("state", ""),
                    "country": property_data.get("country", ""),
                    "zip_code": property_data.get("zip_code", ""),
                    "bedrooms": property_data.get("bedrooms"),
                    "bathrooms": property_data.get("bathrooms"),
                    "area": property_data.get("area", 0),
                    "features": property_data.get("features", []),
                    "amenities": property_data.get("amenities", []),
                    "images": property_data.get("images", []),
                    "latitude": property_data.get("latitude"),
                    "longitude": property_data.get("longitude"),
                    "year_built": property_data.get("year_built"),
                    "condition": property_data.get("condition"),
                    "parking_spaces": property_data.get("parking_spaces"),
                    "agent_id": current_user.id,
                    "owner_id": current_user.id,
                    "created_at": now,
                    "updated_at": now
                })
                
                session.commit()
                property_record = result.fetchone()
                
                return {
                    "id": str(property_record.id),
                    "title": property_record.title,
                    "description": property_record.description,
                    "property_type": property_record.property_type,
                    "status": property_record.status,
                    "price": float(property_record.price),
                    "currency": property_record.currency,
                    "address": property_record.address,
                    "city": property_record.city,
                    "state": property_record.state,
                    "country": property_record.country,
                    "zip_code": property_record.zip_code,
                    "bedrooms": property_record.bedrooms,
                    "bathrooms": property_record.bathrooms,
                    "area": float(property_record.area),
                    "features": property_record.features or [],
                    "amenities": property_record.amenities or [],
                    "images": property_record.images or [],
                    "latitude": property_record.latitude,
                    "longitude": property_record.longitude,
                    "year_built": property_record.year_built,
                    "condition": property_record.condition,
                    "parking_spaces": property_record.parking_spaces,
                    "created_at": property_record.created_at.isoformat(),
                    "updated_at": property_record.updated_at.isoformat(),
                    "views": property_record.views,
                    "favorites": property_record.favorites,
                    "visits": property_record.visits
                }
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating property: {str(e)}")

    @staticmethod
    async def get_properties(
        skip: int = 0,
        limit: int = 10,
        property_type: Optional[str] = None,
        status: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        city: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener propiedades con filtros desde PostgreSQL"""
        try:
            with Session(engine) as session:
                # Construir consulta SQL con filtros
                where_conditions = []
                params = {}
                
                if property_type:
                    where_conditions.append("property_type = :property_type")
                    params["property_type"] = property_type
                
                if status:
                    where_conditions.append("status = :status")
                    params["status"] = status
                    
                if min_price:
                    where_conditions.append("price >= :min_price")
                    params["min_price"] = min_price
                    
                if max_price:
                    where_conditions.append("price <= :max_price")
                    params["max_price"] = max_price
                    
                if city:
                    where_conditions.append("LOWER(city) LIKE LOWER(:city)")
                    params["city"] = f"%{city}%"
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # Consulta para contar total
                count_sql = f"SELECT COUNT(*) as total FROM properties {where_clause}"
                count_result = session.execute(count_sql, params).fetchone()
                total = count_result.total if count_result else 0
                
                # Consulta para obtener propiedades paginadas
                sql = f"""
                    SELECT * FROM properties 
                    {where_clause}
                    ORDER BY created_at DESC 
                    OFFSET :skip LIMIT :limit
                """
                params["skip"] = skip
                params["limit"] = limit
                
                result = session.execute(sql, params)
                properties = []
                
                for row in result:
                    properties.append({
                        "id": str(row.id),
                        "title": row.title,
                        "description": row.description,
                        "property_type": row.property_type,
                        "status": row.status,
                        "price": float(row.price),
                        "currency": row.currency,
                        "address": row.address,
                        "city": row.city,
                        "state": row.state,
                        "country": row.country,
                        "zip_code": row.zip_code,
                        "bedrooms": row.bedrooms,
                        "bathrooms": row.bathrooms,
                        "area": float(row.area),
                        "features": row.features or [],
                        "amenities": row.amenities or [],
                        "images": row.images or [],
                        "latitude": row.latitude,
                        "longitude": row.longitude,
                        "year_built": row.year_built,
                        "condition": row.condition,
                        "parking_spaces": row.parking_spaces,
                        "created_at": row.created_at.isoformat(),
                        "updated_at": row.updated_at.isoformat(),
                        "views": row.views,
                        "favorites": row.favorites,
                        "visits": row.visits
                    })
                
                return {
                    "data": properties,
                    "total": total,
                    "page": (skip // limit) + 1,
                    "limit": limit,
                    "total_pages": (total + limit - 1) // limit if total > 0 else 0
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching properties: {str(e)}")

    @staticmethod
    async def get_property_by_id(property_id: str) -> Optional[Dict[str, Any]]:
        """Obtener una propiedad específica por ID"""
        try:
            with Session(engine) as session:
                sql = "SELECT * FROM properties WHERE id = :property_id"
                result = session.execute(sql, {"property_id": property_id}).fetchone()
                
                if not result:
                    return None
                
                return {
                    "id": str(result.id),
                    "title": result.title,
                    "description": result.description,
                    "property_type": result.property_type,
                    "status": result.status,
                    "price": float(result.price),
                    "currency": result.currency,
                    "address": result.address,
                    "city": result.city,
                    "state": result.state,
                    "country": result.country,
                    "zip_code": result.zip_code,
                    "bedrooms": result.bedrooms,
                    "bathrooms": result.bathrooms,
                    "area": float(result.area),
                    "features": result.features or [],
                    "amenities": result.amenities or [],
                    "images": result.images or [],
                    "latitude": result.latitude,
                    "longitude": result.longitude,
                    "year_built": result.year_built,
                    "condition": result.condition,
                    "parking_spaces": result.parking_spaces,
                    "created_at": result.created_at.isoformat(),
                    "updated_at": result.updated_at.isoformat(),
                    "views": result.views,
                    "favorites": result.favorites,
                    "visits": result.visits
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching property: {str(e)}")

    @staticmethod
    async def update_property(
        property_id: str, 
        property_data: Dict[str, Any], 
        current_user: User
    ) -> Optional[Dict[str, Any]]:
        """Actualizar una propiedad existente"""
        try:
            with Session(engine) as session:
                # Verificar que la propiedad existe y pertenece al usuario
                check_sql = "SELECT id FROM properties WHERE id = :property_id AND (owner_id = :user_id OR agent_id = :user_id)"
                check_result = session.execute(check_sql, {
                    "property_id": property_id,
                    "user_id": current_user.id
                }).fetchone()
                
                if not check_result:
                    return None
                
                # Construir UPDATE dinámico
                set_clauses = []
                params = {"property_id": property_id, "updated_at": datetime.utcnow()}
                
                for key, value in property_data.items():
                    if key not in ["id", "created_at", "updated_at"] and value is not None:
                        set_clauses.append(f"{key} = :{key}")
                        params[key] = value
                
                if not set_clauses:
                    return await PropertyService.get_property_by_id(property_id)
                
                sql = f"""
                    UPDATE properties 
                    SET {', '.join(set_clauses)}, updated_at = :updated_at
                    WHERE id = :property_id
                    RETURNING *
                """
                
                result = session.execute(sql, params).fetchone()
                session.commit()
                
                if not result:
                    return None
                
                return {
                    "id": str(result.id),
                    "title": result.title,
                    "description": result.description,
                    "property_type": result.property_type,
                    "status": result.status,
                    "price": float(result.price),
                    "currency": result.currency,
                    "address": result.address,
                    "city": result.city,
                    "state": result.state,
                    "country": result.country,
                    "zip_code": result.zip_code,
                    "bedrooms": result.bedrooms,
                    "bathrooms": result.bathrooms,
                    "area": float(result.area),
                    "features": result.features or [],
                    "amenities": result.amenities or [],
                    "images": result.images or [],
                    "latitude": result.latitude,
                    "longitude": result.longitude,
                    "year_built": result.year_built,
                    "condition": result.condition,
                    "parking_spaces": result.parking_spaces,
                    "created_at": result.created_at.isoformat(),
                    "updated_at": result.updated_at.isoformat(),
                    "views": result.views,
                    "favorites": result.favorites,
                    "visits": result.visits
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating property: {str(e)}")

    @staticmethod
    async def delete_property(property_id: str, current_user: User) -> bool:
        """Eliminar una propiedad"""
        try:
            with Session(engine) as session:
                # Verificar permisos y eliminar
                sql = """
                    DELETE FROM properties 
                    WHERE id = :property_id AND (owner_id = :user_id OR agent_id = :user_id)
                    RETURNING id
                """
                result = session.execute(sql, {
                    "property_id": property_id,
                    "user_id": current_user.id
                }).fetchone()
                
                session.commit()
                return result is not None
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting property: {str(e)}")

    @staticmethod
    async def get_property_analytics() -> Dict[str, Any]:
        """Obtener analytics reales de propiedades desde PostgreSQL"""
        try:
            with Session(engine) as session:
                # Estadísticas básicas
                stats_sql = """
                    SELECT 
                        COUNT(*) as total_properties,
                        COUNT(CASE WHEN status = 'available' THEN 1 END) as available_properties,
                        COUNT(CASE WHEN status = 'sold' THEN 1 END) as sold_properties,
                        COUNT(CASE WHEN status = 'rented' THEN 1 END) as rented_properties,
                        SUM(price) as total_inventory_value,
                        AVG(price) as average_property_price
                    FROM properties
                """
                stats = session.execute(stats_sql).fetchone()
                
                # Propiedades por ciudad
                city_sql = """
                    SELECT city, COUNT(*) as count, AVG(price) as average_price
                    FROM properties
                    GROUP BY city
                    ORDER BY count DESC
                    LIMIT 10
                """
                cities = session.execute(city_sql).fetchall()
                
                # Propiedades por tipo
                type_sql = """
                    SELECT 
                        property_type as type, 
                        COUNT(*) as count, 
                        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM properties), 2) as percentage
                    FROM properties
                    GROUP BY property_type
                    ORDER BY count DESC
                """
                types = session.execute(type_sql).fetchall()
                
                return {
                    "total_properties": stats.total_properties or 0,
                    "available_properties": stats.available_properties or 0,
                    "sold_properties": stats.sold_properties or 0,
                    "rented_properties": stats.rented_properties or 0,
                    "total_inventory_value": float(stats.total_inventory_value or 0),
                    "average_property_price": float(stats.average_property_price or 0),
                    "total_sales_this_month": 0,  # TODO: Implementar con fechas
                    "commission_earned_this_month": 0,  # TODO: Implementar
                    "properties_by_city": [
                        {
                            "city": city.city,
                            "count": city.count,
                            "average_price": float(city.average_price or 0)
                        }
                        for city in cities
                    ],
                    "properties_by_type": [
                        {
                            "type": type_row.type,
                            "count": type_row.count,
                            "percentage": float(type_row.percentage or 0)
                        }
                        for type_row in types
                    ]
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}") 