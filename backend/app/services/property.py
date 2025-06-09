from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from nhost import NhostClient
from ..models import Property, PropertyCreate, PropertyUpdate, PropertySearch, PropertyVisit, PropertyVisitCreate, PropertyVisitUpdate

class PropertyService:
    def __init__(self, nhost: NhostClient):
        self.nhost = nhost

    async def create_property(self, property_data: PropertyCreate) -> Property:
        """Crear una nueva propiedad"""
        query = """
        mutation CreateProperty($property: properties_insert_input!) {
            insert_properties_one(object: $property) {
                id
                title
                description
                property_type
                status
                price
                currency
                address
                city
                state
                country
                zip_code
                bedrooms
                bathrooms
                area
                features
                amenities
                images
                latitude
                longitude
                year_built
                condition
                parking_spaces
                agent_id
                owner_id
                created_at
                updated_at
                views
                favorites
                visits
            }
        }
        """
        variables = {"property": property_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return Property(**result["data"]["insert_properties_one"])

    async def get_property(self, property_id: UUID) -> Optional[Property]:
        """Obtener una propiedad por su ID"""
        query = """
        query GetProperty($id: uuid!) {
            properties_by_pk(id: $id) {
                id
                title
                description
                property_type
                status
                price
                currency
                address
                city
                state
                country
                zip_code
                bedrooms
                bathrooms
                area
                features
                amenities
                images
                latitude
                longitude
                year_built
                condition
                parking_spaces
                agent_id
                owner_id
                created_at
                updated_at
                views
                favorites
                visits
            }
        }
        """
        variables = {"id": str(property_id)}
        result = await self.nhost.graphql.request(query, variables)
        property_data = result["data"]["properties_by_pk"]
        return Property(**property_data) if property_data else None

    async def update_property(self, property_id: UUID, property_data: PropertyUpdate) -> Optional[Property]:
        """Actualizar una propiedad"""
        query = """
        mutation UpdateProperty($id: uuid!, $property: properties_set_input!) {
            update_properties_by_pk(pk_columns: {id: $id}, _set: $property) {
                id
                title
                description
                property_type
                status
                price
                currency
                address
                city
                state
                country
                zip_code
                bedrooms
                bathrooms
                area
                features
                amenities
                images
                latitude
                longitude
                year_built
                condition
                parking_spaces
                agent_id
                owner_id
                created_at
                updated_at
                views
                favorites
                visits
            }
        }
        """
        variables = {
            "id": str(property_id),
            "property": {k: v for k, v in property_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        property_data = result["data"]["update_properties_by_pk"]
        return Property(**property_data) if property_data else None

    async def delete_property(self, property_id: UUID) -> bool:
        """Eliminar una propiedad"""
        query = """
        mutation DeleteProperty($id: uuid!) {
            delete_properties_by_pk(id: $id) {
                id
            }
        }
        """
        variables = {"id": str(property_id)}
        result = await self.nhost.graphql.request(query, variables)
        return bool(result["data"]["delete_properties_by_pk"])

    async def search_properties(self, search_params: PropertySearch, limit: int = 10, offset: int = 0) -> List[Property]:
        """Buscar propiedades según criterios"""
        where_clause = []
        variables = {}

        if search_params.property_type:
            where_clause.append("property_type: {_eq: $property_type}")
            variables["property_type"] = search_params.property_type

        if search_params.min_price is not None:
            where_clause.append("price: {_gte: $min_price}")
            variables["min_price"] = search_params.min_price

        if search_params.max_price is not None:
            where_clause.append("price: {_lte: $max_price}")
            variables["max_price"] = search_params.max_price

        # Agregar más condiciones según los parámetros de búsqueda...

        where_str = ", ".join(where_clause)
        query = f"""
        query SearchProperties($limit: Int!, $offset: Int!, {', '.join(f'${k}: {type(v).__name__}' for k, v in variables.items())}) {{
            properties(where: {{{where_str}}}, limit: $limit, offset: $offset) {{
                id
                title
                description
                property_type
                status
                price
                currency
                address
                city
                state
                country
                zip_code
                bedrooms
                bathrooms
                area
                features
                amenities
                images
                latitude
                longitude
                year_built
                condition
                parking_spaces
                agent_id
                owner_id
                created_at
                updated_at
                views
                favorites
                visits
            }}
        }}
        """
        variables.update({"limit": limit, "offset": offset})
        result = await self.nhost.graphql.request(query, variables)
        return [Property(**p) for p in result["data"]["properties"]]

    async def schedule_visit(self, visit_data: PropertyVisitCreate) -> PropertyVisit:
        """Programar una visita a una propiedad"""
        query = """
        mutation CreateVisit($visit: property_visits_insert_input!) {
            insert_property_visits_one(object: $visit) {
                id
                property_id
                client_id
                visit_date
                status
                notes
                agent_id
                feedback
                created_at
            }
        }
        """
        variables = {"visit": visit_data.dict()}
        result = await self.nhost.graphql.request(query, variables)
        return PropertyVisit(**result["data"]["insert_property_visits_one"])

    async def update_visit(self, visit_id: UUID, visit_data: PropertyVisitUpdate) -> Optional[PropertyVisit]:
        """Actualizar el estado de una visita"""
        query = """
        mutation UpdateVisit($id: uuid!, $visit: property_visits_set_input!) {
            update_property_visits_by_pk(pk_columns: {id: $id}, _set: $visit) {
                id
                property_id
                client_id
                visit_date
                status
                notes
                agent_id
                feedback
                created_at
            }
        }
        """
        variables = {
            "id": str(visit_id),
            "visit": {k: v for k, v in visit_data.dict().items() if v is not None}
        }
        result = await self.nhost.graphql.request(query, variables)
        visit_data = result["data"]["update_property_visits_by_pk"]
        return PropertyVisit(**visit_data) if visit_data else None

    async def record_view(self, property_id: UUID, user_id: Optional[UUID], ip_address: str, user_agent: str) -> None:
        """Registrar una vista de propiedad"""
        query = """
        mutation RecordView($view: property_views_insert_input!) {
            insert_property_views_one(object: $view) {
                id
            }
        }
        """
        variables = {
            "view": {
                "property_id": str(property_id),
                "user_id": str(user_id) if user_id else None,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow().isoformat()
            }
        }
        await self.nhost.graphql.request(query, variables)

    async def toggle_favorite(self, property_id: UUID, user_id: UUID) -> bool:
        """Agregar/quitar una propiedad de favoritos"""
        # Primero verificar si ya existe
        query = """
        query CheckFavorite($property_id: uuid!, $user_id: uuid!) {
            property_favorites(where: {property_id: {_eq: $property_id}, user_id: {_eq: $user_id}}) {
                id
            }
        }
        """
        variables = {
            "property_id": str(property_id),
            "user_id": str(user_id)
        }
        result = await self.nhost.graphql.request(query, variables)
        existing = result["data"]["property_favorites"]

        if existing:
            # Eliminar de favoritos
            query = """
            mutation RemoveFavorite($property_id: uuid!, $user_id: uuid!) {
                delete_property_favorites(where: {property_id: {_eq: $property_id}, user_id: {_eq: $user_id}}) {
                    affected_rows
                }
            }
            """
            result = await self.nhost.graphql.request(query, variables)
            return False
        else:
            # Agregar a favoritos
            query = """
            mutation AddFavorite($favorite: property_favorites_insert_input!) {
                insert_property_favorites_one(object: $favorite) {
                    id
                }
            }
            """
            variables = {
                "favorite": {
                    "property_id": str(property_id),
                    "user_id": str(user_id),
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            await self.nhost.graphql.request(query, variables)
            return True 