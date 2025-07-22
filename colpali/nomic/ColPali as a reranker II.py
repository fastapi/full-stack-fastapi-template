
# %%
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
from datasets import load_dataset
from google.colab import userdata
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
import random
from ranx import compare, Qrels, Run
import torch
from tqdm import tqdm

client = QdrantClient(url="http://localhost:6333")
collection_name = "le-collection"

model_name = (
    "nomic-ai/colnomic-embed-multimodal-3b"
)
colqwen_model = ColQwen2_5.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0" if torch.cuda.is_available() else "cpu"
).eval()

colqwen_processor = ColQwen2_5_Processor.from_pretrained(
    model_name
)

random_query_sample = client.query_points(
    collection_name=collection_name,
    limit=1000,
    query_filter=models.Filter(
        must_not=[
            models.IsNullCondition( #some of the queries in the datasets (ViDoRe) were null
                is_null=models.PayloadField(key="query")
            )
        ]
    ),
    query=models.SampleQuery(sample=models.Sample.RANDOM)
).points

random_query_sample = [sample.payload['query'] for sample in random_query_sample]

random_query_sample[0]

dataset_ufo = load_dataset("davanstrien/ufo-ColPali", split="train")
dataset_ufo = dataset_ufo.filter(lambda x: x['parsed_into_json']) #ones unparsed were not included in our final collection
ufo_queries = dataset_ufo['specific_detail_query']
ufo_queries = random.sample(ufo_queries, 1000)

ufo_queries[0]

with torch.no_grad():
    batch_query = colqwen_processor.process_queries([ufo_queries[0]]).to(
        colqwen_model.device
    )
    print(colqwen_processor.tokenizer.tokenize(
        colqwen_processor.decode(batch_query.input_ids[0])
    ))


def colpali_query(query): #per query
    with torch.no_grad():
        batch_query = colqwen_processor.process_queries([query]).to(
            colqwen_model.device
        )
        mask_without_pad = batch_query.input_ids.bool().unsqueeze(-1)
    query_embedding = colqwen_model(**batch_query)
    query_without_pad = torch.masked_select(query_embedding, mask_without_pad).view(1, -1, 128)
    return {
        "full": query_embedding[0].cpu().float().numpy().tolist(),
        "cut": query_without_pad[0].cpu().float().numpy().tolist()
    }


ufo_queries_sample_embeddings = [colpali_query(sample) for sample in ufo_queries]


def search_qdrant_batch(query_batch,
                        named_vector,
                        query_state="full", #or "cut", related to <pad> tokens
                        search_limit=20,
                        timeout=1000,
                        collection_name="le-collection"
                        ):
    search_queries = [
      models.QueryRequest(
          query=query[query_state],
          limit=search_limit,
          using=named_vector,
          params=models.SearchParams(
              exact=True #no HNSW index used, KNN search instead of ANN
          )
      ) for query in query_batch
    ]
    return client.query_batch_points(
        collection_name=collection_name,
        requests=search_queries,
        timeout=timeout
    )

batch_size = 8
ufo_full_exact_search_result = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    current_batch_size = len(batch_embeddings)
    batch_result = search_qdrant_batch(batch_embeddings,
                                       'initial'
                                       )
    ufo_full_exact_search_result += batch_result

def search_prefetch_qdrant_batch(query_batch,
                                 named_vector,
                                 named_vector_prefetch,
                                 query_state="full",
                                 query_state_prefetch="full",
                                 prefetch_quantization_ignore=True,
                                 prefetch_quantization_rescore=False,
                                 prefetch_oversampling=1.0,
                                 search_limit=20,
                                 prefetch_limit=200,
                                 timeout=1000,
                                 collection_name="le-collection"
                                 ):
    search_queries = [
      models.QueryRequest(
          query=query[query_state],
          prefetch=models.Prefetch(
              query=query[query_state_prefetch],
              limit=prefetch_limit,
              params=models.SearchParams(
                  quantization=models.QuantizationSearchParams(
                      ignore=prefetch_quantization_ignore,
                      rescore=prefetch_quantization_rescore,
                      oversampling=prefetch_oversampling
                  )
              ),
              using=named_vector_prefetch
          ),
          params=models.SearchParams(
              exact=True #exact mode
          ),
          limit=search_limit,
          using=named_vector
      ) for query in query_batch
    ]
    return client.query_batch_points(
        collection_name=collection_name,
        requests=search_queries,
        timeout=timeout
    )

batch_size = 8
ufo_full_exact_search_result_prefetch_max = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    batch_result_max = search_prefetch_qdrant_batch(batch_embeddings, 'initial', 'max_pooling')
    ufo_full_exact_search_result_prefetch_max += batch_result_max

batch_size = 8
ufo_full_exact_search_result_prefetch_mean = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    batch_result_mean = search_prefetch_qdrant_batch(batch_embeddings, 'initial', 'mean_pooling')
    ufo_full_exact_search_result_prefetch_mean += batch_result_mean


def prep_for_ranx(queries_array):
    ranx_dict = {}
    for query_id, query in enumerate(queries_array): #we assign query ID for `ranx` based on queries order
        max_rank = 20
        query_docs = {}
        for doc_num, docs in enumerate(query.points):
            query_docs[f'''d_{docs.id}'''] = max_rank #We assign returned documents (PDF pages) ID of a point in Qdrant
            max_rank -= 1
        ranx_dict[f'''q_{query_id}'''] = query_docs
    return ranx_dict

qrels_ufo = Qrels(prep_for_ranx(ufo_full_exact_search_result), name="ufo_original_ColPALI")
run_max_ufo = Run(prep_for_ranx(ufo_full_exact_search_result_prefetch_max), name="ufo_prefetch_ColPALI_maxpool")
run_mean_ufo = Run(prep_for_ranx(ufo_full_exact_search_result_prefetch_mean), name="ufo_prefetch_ColPALI_meanpool")

report_ufo = compare(
    qrels=qrels_ufo,
    runs=[run_max_ufo, run_mean_ufo],
    metrics=["ndcg@20", "recall@20"]
)

print(report_ufo)

batch_size = 8
ufo_cut_exact_search_result_prefetch_mean = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    batch_result_mean = search_prefetch_qdrant_batch(batch_embeddings,
                                                    'initial',
                                                    'mean_pooling',
                                                    'full',
                                                    'cut')
    ufo_cut_exact_search_result_prefetch_mean += batch_result_mean

batch_size = 8
binary_ufo_full_exact_search_result_prefetch_mean = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    batch_result_mean = search_prefetch_qdrant_batch(batch_embeddings,
                                                     'initial',
                                                     'mean_pooling',
                                                     'full',
                                                     'full',
                                                     False)
    binary_ufo_full_exact_search_result_prefetch_mean += batch_result_mean

run_mean_ufo_cut = Run(prep_for_ranx(ufo_cut_exact_search_result_prefetch_mean), name="ufo_prefetch_ColPALI_meanpool_cut")
run_mean_ufo_binary = Run(prep_for_ranx(binary_ufo_full_exact_search_result_prefetch_mean), name="ufo_prefetch_ColPALI_meanpool_binary")

report_ufo = compare(
    qrels=qrels_ufo,
    runs=[run_max_ufo, run_mean_ufo, run_mean_ufo_cut, run_mean_ufo_binary],
    metrics=["ndcg@20", "recall@20"]
)

print(report_ufo)