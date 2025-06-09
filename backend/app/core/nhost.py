from typing import Optional
from pydantic import BaseModel, HttpUrl
from app.core.config import settings

class NhostConfig(BaseModel):
    """Configuración para Nhost."""
    url: HttpUrl
    admin_secret: str
    graphql_endpoint: Optional[HttpUrl] = None
    auth_endpoint: Optional[HttpUrl] = None
    storage_endpoint: Optional[HttpUrl] = None
    functions_endpoint: Optional[HttpUrl] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.graphql_endpoint:
            self.graphql_endpoint = f"{self.url}/v1/graphql"
        if not self.auth_endpoint:
            self.auth_endpoint = f"{self.url}/v1/auth"
        if not self.storage_endpoint:
            self.storage_endpoint = f"{self.url}/v1/storage"
        if not self.functions_endpoint:
            self.functions_endpoint = f"{self.url}/v1/functions"

nhost_config = NhostConfig(
    url=settings.NHOST_URL,
    admin_secret=settings.NHOST_ADMIN_SECRET,
) 