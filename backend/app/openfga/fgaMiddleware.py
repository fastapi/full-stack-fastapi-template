import logging
from typing import Any
from app.core.config import settings
from openfga_sdk import (
    Condition,
    ConditionParamTypeRef,
    CreateStoreRequest,
    Metadata,
    ObjectRelation,
    OpenFgaClient,
    ReadRequestTupleKey,
    RelationMetadata,
    RelationReference,
    RelationshipCondition,
    TypeDefinition,
    Userset,
    Usersets,
    UserTypeFilter,
    WriteAuthorizationModelRequest,
)
from openfga_sdk.client.models import (
    ClientAssertion,
    ClientBatchCheckItem,
    ClientBatchCheckRequest,
    ClientCheckRequest,
    ClientListObjectsRequest,
    ClientListRelationsRequest,
    ClientReadChangesRequest,
    ClientTuple,
    ClientWriteRequest,
    WriteTransactionOpts,
)
from openfga_sdk.client.models.list_users_request import ClientListUsersRequest
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.models.fga_object import FgaObject
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.sync import OpenFgaClient


import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_fga_client():
    configuration = ClientConfiguration(
        api_url=settings.OPENFGA_API_URL,  # required
        store_id=settings.OPENFGA_STORE_ID,  # optional, not needed when calling `CreateStore` or `ListStores`
        authorization_model_id=settings.OPENFGA_AUTHORIZATION_MODEL_ID,  # optional, can be overridden per request
    )
    # Enter a context with an instance of the OpenFgaClient
    with OpenFgaClient(configuration) as fga_client:
        return fga_client

def close_fga_client(fga_client: OpenFgaClient):
    fga_client.close()

# Check if a user has a permission on an object
def check_user_has_permission(fga_client: OpenFgaClient, tuple: ClientTuple) -> bool:
    if fga_client is None: # type: ignore
        fga_client = initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
        
    try:
        response = fga_client.check(
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
def check_user_has_permission_batch(fga_client: OpenFgaClient, tuples: list[ClientBatchCheckItem]) -> bool:
    if fga_client is None: # type: ignore
        fga_client = initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
    
    logger.info(f"Check fga_client: {fga_client}")
    logger.info(f"Check fga status: {fga_client.get_store_id()}")
    
    try:
        response = fga_client.batch_check(
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
def create_fga_tuple(fga_client: OpenFgaClient, tuples: list[ClientTuple]) -> bool:
    if fga_client is None: # type: ignore
        fga_client = initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
    
    logger.info(f"Creating FGA tuple: {tuples}")
    logger.info(f"So is this even working lol: {fga_client.get_store_id()}")

    try:
        response = fga_client.write_tuples(tuples)
        logger.info(f"Response vars: {vars(response)}")
        return True
    except Exception as e:
        logger.info(f"Error creating FGA tuple: {e}") # type: ignore
        return False
    
# Delete a tuple
def delete_fga_tuple(fga_client: OpenFgaClient, tuples: list[ClientTuple]) -> bool:
    # This is the opposite of the create_fga_tuple function
    if fga_client is None: # type: ignore
        fga_client = initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return False
    
    try:
        response = fga_client.write(
            ClientWriteRequest(
                deletes=tuples
            )
        )
        return response.allowed # type: ignore
    except Exception as e:
        logger.info(f"Error deleting FGA tuple: {e}") # type: ignore
        return False


def check_user_has_relation(fga_client: OpenFgaClient, relation: str, user: str) -> list[str]:

    if fga_client is None: # type: ignore
        fga_client = initialize_fga_client()

    if fga_client is None:
        logger.info("FGA client not initialized") # type: ignore
        return []
    
    body = ClientListObjectsRequest(
        user=f"user:{user}",
        relation=f"{relation}",
        type="item"
    )

    try:
        response = fga_client.list_objects(body)
        # response.objects = ["document:otherdoc", "document:planning"]
        # we need to return a list of objects
        if len(response.objects) > 0:
            return [item.split(":")[1] for item in response.objects] # type: ignore
        else:
            return []
    except Exception as e:
        logger.info(f"Error checking user relation: {e}")
        logger.info(traceback.format_exc())
        return []