import asyncio
from typing import Any, List, Dict, Optional
from backoff import backOff # type: ignore
from openfga_sdk.client import ClientConfiguration, OpenFgaClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def main():
    configuration = ClientConfiguration(
        api_url=settings.OPENFGA_API_URL,
        store_id=settings.OPENFGA_STORE_ID,
        authorization_model_id=settings.OPENFGA_AUTHORIZATION_MODEL_ID,
    )
    # Enter a context with an instance of the OpenFgaClient
    async with OpenFgaClient(configuration) as fga_client:
        api_response = await fga_client.read_authorization_models()
        await fga_client.close()

asyncio.run(main())

# async def attempt_connection():
#     async def initialize_fga():
#         if getattr(settings, "COMPOSE_ENVIRONMENT", False):
#             import json
#             import os
#             path = '/openfga/fga_variables.json'
#             if not os.path.exists(path):
#                 raise FileNotFoundError('FGA variables JSON file not found')
#             with open(path, 'r') as f:
#                 variables = json.load(f)
#             store_id = variables['storeId']
#             authorization_model_id = variables['authModelId']
#         else:
#             store_id = settings.OPENFGA_STORE_ID
#             authorization_model_id = settings.OPENFGA_AUTHORIZATION_MODEL_ID

#         if not settings.OPENFGA_API_URL:
#             raise ValueError('Missing required OpenFGA configuration (apiUrl)')

#         fga_client = OpenFgaClient(
#             api_url=settings.OPENFGA_API_URL,
#             store_id=store_id,
#             authorization_model_id=authorization_model_id,
#         )
#         await fga_client.check_valid_api_connection()

#         fga_state.fga_client = fga_client
#         fga_state.store_id = store_id
#         fga_state.authorization_model_id = authorization_model_id
#         fga_state.ready = True

#         logger.info(f'FGA client initialized successfully with storeId: {store_id}')
#         logger.info(f'FGA client initialized with apiUrl: {settings.OPENFGA_API_URL}')
#         logger.info('FGA client connection validated successfully')

#     try:
#         await backOff(initialize_fga)
#         return True
#     except Exception as error:
#         logger.error('Failed to initialize FGA client after maximum retries. Last error: %s', error)
#         fga_state.fga_client = None
#         fga_state.ready = False
#         return False

# async def check_object_access(fga_user_id: str, relation: str, object_type: str, object_id: str) -> bool:
#     if not fga_user_id:
#         raise ValueError('User id is required')
#     if not relation:
#         raise ValueError('Relation is required')
#     if not object_id:
#         raise ValueError('Object id is required')
#     if not fga_state.fga_client:
#         raise RuntimeError('FGA client is not initialized')

#     try:
#         result = await fga_state.fga_client.check({
#             "user": f"{'user'}:{fga_user_id}",
#             "relation": relation,
#             "object": f"{object_type}:{object_id}",
#         })
#         return result.get('allowed', False)
#     except Exception as error:
#         logger.error('Error checking access: %s', error)
#         raise RuntimeError('FGA check failed.') from error

# async def create_fga_tuple(writes: List[Dict[str, str]]):
#     if not writes or not isinstance(writes, list):
#         raise ValueError('Non-empty writes array is required')
#     if not fga_state.fga_client:
#         raise RuntimeError('FGA client is not initialized')

#     await fga_state.fga_client.write({
#         "writes": writes
#     })
#     logger.info(f"FGA tuples created: {writes}")

# async def delete_fga_tuple(user: str, relation: str, object_id: str):
#     if not user:
#         raise ValueError('User id is required')
#     if not relation:
#         raise ValueError('Relation is required')
#     if not object_id:
#         raise ValueError('Object id is required')
#     if not fga_state.fga_client:
#         raise RuntimeError('FGA client is not initialized')

#     await fga_state.fga_client.write({
#         "deletes": [
#             {
#                 "user": f"{'user'}:{user}",
#                 "relation": relation,
#                 "object": object_id,
#             }
#         ]
#     })
#     logger.info(f"FGA tuple deleted: user={user}, relation={relation}, object={object_id}")

# async def initialize_fga_client():
#     success = await attempt_connection()
#     if not success:
#         logger.warning('Application will start without FGA authorization')

# async def batch_check_user_permissions(
#     item_object_ids: List[Any],
#     user_id: str,
#     relation: str,
#     type_: str,
# ) -> ClientBatchCheckResponse:
#     if not item_object_ids:
#         raise ValueError('Item id array is required')
#     if not relation:
#         raise ValueError('Relation is required')
#     if not user_id:
#         raise ValueError('User id is required')
#     if not type_:
#         raise ValueError('Type is required')
#     if not fga_state.fga_client:
#         raise RuntimeError('FGA client is not initialized')

#     checks = [
#         {
#             "user": f"{'user'}:{user_id}",
#             "relation": relation,
#             "object": f"{type_}:{object_id}",
#             "correlationId": object_id,
#         }
#         for object_id in item_object_ids
#     ]

#     body = {"checks": checks}
#     options = {
#         "authorization_model_id": fga_state.authorization_model_id,
#         "maxBatchSize": 50,
#         "maxParallelRequests": 10,
#     }

#     try:
#         response = await fga_state.fga_client.batch_check(body, options)
#         return response
#     except Exception as error:
#         logger.error('Error checking permissions: %s', error)
#         raise RuntimeError('Failed to check permissions') from error
