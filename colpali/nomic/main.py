# !pip install -q "qdrant-client" "colpali_engine>=0.3.1" "datasets" "huggingface_hub[hf_transfer]" "transformers>=4.45.0" "fastapi" "uvicorn" "requests"

from datasets import load_dataset
from qdrant_client import QdrantClient, models
from tqdm import tqdm
import uuid
import numpy as np
import random
from model_client import model_client

client = QdrantClient(url="http://localhost:6333")
collection_name = "le-collection"
ufo_dataset = "davanstrien/ufo-ColPali"
dataset = load_dataset(ufo_dataset, split="train")

collection_exists = client.get_collection(collection_name)
if not collection_exists:    
    print(f"Creating collection '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "original":
                models.VectorParams( #switch off HNSW
                      size=128,
                      distance=models.Distance.COSINE,
                      multivector_config=models.MultiVectorConfig(
                          comparator=models.MultiVectorComparator.MAX_SIM
                      ),
                      hnsw_config=models.HnswConfigDiff(
                          m=0 #switching off HNSW
                      )
                ),
            "mean_pooling_columns": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    )
                ),
            "mean_pooling_rows": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    )
                )
        }
    )
else:
    print(f"Collection '{collection_name}' already exists.")

def upload_batch(original_batch, pooled_by_rows_batch, pooled_by_columns_batch, payload_batch, collection_name):
    try:
        client.upload_collection(
            collection_name=collection_name,
            vectors={
                "original": original_batch,
                "mean_pooling_columns": pooled_by_columns_batch,
                "mean_pooling_rows": pooled_by_rows_batch
            },
            payload=payload_batch,
            ids=[str(uuid.uuid4()) for i in range(len(original_batch))]
        )
    except Exception as e:
        print(f"Error during upsert: {e}")

batch_size = 4 #based on available compute
dataset_source = ufo_dataset

with tqdm(total=len(dataset), desc=f"Uploading progress of \"{dataset_source}\" dataset to \"{collection_name}\" collection") as pbar:
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i : i + batch_size]
        image_batch = batch["image"]
        current_batch_size = len(image_batch)
        try:
            original_batch, pooled_by_rows_batch, pooled_by_columns_batch = model_client.embed_and_mean_pool_batch(image_batch)
        except Exception as e:
            print(f"Error during embed: {e}")
            continue
        try:
            upload_batch(
                np.asarray(original_batch, dtype=np.float32),
                np.asarray(pooled_by_rows_batch, dtype=np.float32),
                np.asarray(pooled_by_columns_batch, dtype=np.float32),
                [
                    {
                        "source": dataset_source,
                        "index": j
                    }
                    for j in range(i, i + current_batch_size)
                ],
                collection_name
            )
        except Exception as e:
            print(f"Error during upsert: {e}")
            continue
        # Update the progress bar
        pbar.update(current_batch_size)
print("Uploading complete!")

query = "Megalithic statues on Pasqua Island"
colqwen_query = model_client.batch_embed_query([query])

def reranking_search_batch(query_batch,
                           collection_name,
                           search_limit=20,
                           prefetch_limit=200):
    search_queries = [
      models.QueryRequest(
          query=query,
          prefetch=[
              models.Prefetch(
                  query=query,
                  limit=prefetch_limit,
                  using="mean_pooling_columns"
              ),
              models.Prefetch(
                  query=query,
                  limit=prefetch_limit,
                  using="mean_pooling_rows"
              ),
          ],
          limit=search_limit,
          with_payload=True,
          with_vector=False,
          using="original"
      ) for query in query_batch
    ]
    return client.query_batch_points(
        collection_name=collection_name,
        requests=search_queries
    )

answer_colqwen = reranking_search_batch(colqwen_query, "colqwen_tutorial")

dataset[answer_colqwen[0].points[0].payload['index']]['image']