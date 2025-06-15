from app.core.config import settings
from fastapi import logger
from openfga_sdk.client import ClientConfiguration, OpenFgaClient, ClientCheckRequest, ClientBatchCheckRequest, ClientWriteRequest # type: ignore

configuration = ClientConfiguration(
    api_url=settings.OPENFGA_API_URL,
    store_id=settings.OPENFGA_STORE_ID,
    authorization_model_id=settings.OPENFGA_AUTHORIZATION_MODEL_ID,
)

fga_client = OpenFgaClient(configuration)

# Check if a user has a permission on an object
async def check_user_has_permission(user: str, relation: str, object: str) -> bool:
    try:
        response = await fga_client.check(
            ClientCheckRequest(
                user=user,
                relation=relation,
                object=object
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.error(f"Error checking user permission: {e}") # type: ignore
        return False
    
# Check if a user has a permission on multiple objects
async def check_user_has_permission_batch(user: str, relation: str, object: str) -> bool:
    try:
        response = await fga_client.batch_check(
            ClientBatchCheckRequest(
                user=user,
                relation=relation,
                object=object
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.error(f"Error checking user permission: {e}") # type: ignore
        return False
    
# Create a tuple
# Here is what a 'tuple' looks like:
# [
#     {
#         "user": "user:123",
#         "relation": "can_view",
#         "object": "document:123"
#     }
# ]
async def create_fga_tuple(tuples: list[tuple[str, str, str]]) -> bool:
    try:
        response = await fga_client.write(
            ClientWriteRequest(
                writes=tuples
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.error(f"Error creating FGA tuple: {e}") # type: ignore
        return False
