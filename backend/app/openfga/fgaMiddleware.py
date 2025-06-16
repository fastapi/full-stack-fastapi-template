import asyncio
from app.core.config import settings
from fastapi import logger
from openfga_sdk.client import ClientConfiguration, OpenFgaClient, ClientCheckRequest
from openfga_sdk.client.models import ClientBatchCheckRequest, ClientWriteRequest, ClientBatchCheckItem
from openfga_sdk.client.models.tuple import ClientTuple

# We default fga_client to None until it is initialized
fga_client = None

async def initialize_fga_client():
    # This function is called to initialize our FGA Client instance if it is not already available
    print("Initializing OpenFGA Client SDK")
    configuration = ClientConfiguration(
        api_url = settings.OPENFGA_API_URL, 
        store_id = settings.OPENFGA_STORE_ID, 
        authorization_model_id = settings.OPENFGA_AUTHORIZATION_MODEL_ID, 
    )

    global fga_client

    # Enter a context with an instance of the OpenFgaClient
    async with OpenFgaClient(configuration) as fga_client:
        fga_client = OpenFgaClient(configuration)
        await fga_client.read_authorization_models() # type: ignore
        print("FGA Client initialized.")
        return True

async def close_fga_client(fga_client: OpenFgaClient):
    await fga_client.close()

# Check if a user has a permission on an object
async def check_user_has_permission(tuple: ClientTuple) -> bool:
    if fga_client is None:
        await initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
        
    try:
        response = await fga_client.check(
            ClientCheckRequest( 
                user=tuple.user,
                relation=tuple.relation,
                object=tuple.object
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.info(f"Error checking user permission: {e}") # type: ignore
        return False
    
# Check if a user has a permission on multiple objects
# Example list of ClientBatchCheckItem is:
# [
#     {
#         "user": "user:123",
#         "relation": "can_view",
#         "object": "document:123"
#     },
#     {
#         "user": "user:123",
#         "relation": "can_view",
#         "object": "document:123"
#     }
# ]
async def check_user_has_permission_batch(tuples: list[ClientBatchCheckItem]) -> bool:
    if fga_client is None:
        await initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
    
    try:
        response = await fga_client.batch_check(
            ClientBatchCheckRequest(
                checks=tuples
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.info(f"Error checking user permission: {e}") # type: ignore
        return False
    
# Create a tuple
# Example list of ClientTuple is:
# [
#     {
#         "user": "user:123",
#         "relation": "can_view",
#         "object": "document:123"
#     }
# ]
async def create_fga_tuple(tuples: list[ClientTuple]) -> bool:
    if fga_client is None:
        await initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
    
    try:
        response = await fga_client.write(
            ClientWriteRequest(
                writes=tuples
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.info(f"Error creating FGA tuple: {e}") # type: ignore
        return False
    
# Delete a tuple
async def delete_fga_tuple(tuples: list[ClientTuple]) -> bool:
    # This is the opposite of the create_fga_tuple function
    if fga_client is None:
        await initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
    
    try:
        response = await fga_client.write(
            ClientWriteRequest(
                deletes=tuples
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.info(f"Error deleting FGA tuple: {e}") # type: ignore
        return False
