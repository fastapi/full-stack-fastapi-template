from typing import Any, Dict, Optional
import httpx
from app.core.nhost import nhost_config

class NhostClient:
    """Cliente para interactuar con Nhost."""
    
    def __init__(self):
        self.headers = {
            "x-hasura-admin-secret": nhost_config.admin_secret,
            "Content-Type": "application/json",
        }
        self.graphql_endpoint = str(nhost_config.graphql_endpoint)
        self.auth_endpoint = str(nhost_config.auth_endpoint)
        self.storage_endpoint = str(nhost_config.storage_endpoint)
        self.functions_endpoint = str(nhost_config.functions_endpoint)

    async def graphql_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Ejecuta una consulta GraphQL."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.graphql_endpoint,
                json={"query": query, "variables": variables or {}},
                headers={**self.headers, **(headers or {})},
            )
            response.raise_for_status()
            return response.json()

    async def auth_signup(
        self,
        email: str,
        password: str,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Registra un nuevo usuario."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_endpoint}/signup",
                json={
                    "email": email,
                    "password": password,
                    "options": {"data": user_metadata or {}},
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def auth_signin(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """Inicia sesión de un usuario."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_endpoint}/signin",
                json={
                    "email": email,
                    "password": password,
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def storage_upload(
        self,
        bucket: str,
        file_path: str,
        file_content: bytes,
        content_type: str,
    ) -> Dict[str, Any]:
        """Sube un archivo al storage."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.storage_endpoint}/files/{bucket}/{file_path}",
                content=file_content,
                headers={
                    **self.headers,
                    "Content-Type": content_type,
                },
            )
            response.raise_for_status()
            return response.json()

    async def function_call(
        self,
        function_name: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Llama a una función serverless."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.functions_endpoint}/{function_name}",
                json=payload,
                headers={**self.headers, **(headers or {})},
            )
            response.raise_for_status()
            return response.json()

nhost_client = NhostClient() 