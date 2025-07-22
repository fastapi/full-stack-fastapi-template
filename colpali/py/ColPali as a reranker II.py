# %% [markdown]
# # Introduction
# 
# In the previous notebook, **ColPali as a reranker I.ipynb**, we demonstrated how to set up the Qdrant collection and upload vectors for large-scale experiments.
# 
# In this notebook, we’ll do **retrieval quality and speed comparisons** and analyze the trade-offs between speed and accuracy when using pooled ColPali vectors + reranking versus the original ColPali model.
# 
# 
# 
# 
# 
# 

# %%
# !pip install -q "colpali_engine>=0.3.1" "datasets" "huggingface_hub[hf_transfer]" "transformers>=4.45.0" "qdrant-client" "ranx"

# %%
from colpali_engine.models import ColPali, ColPaliProcessor
from datasets import load_dataset
from google.colab import userdata
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
import random
from ranx import compare, Qrels, Run
import torch
from tqdm import tqdm

# %%
client = QdrantClient(
    url="https://187badc9-1579-40af-b564-cf6aa73c84c3.us-east4-0.gcp.cloud.qdrant.io",
    api_key=userdata.get('qdrant_cloud'),
)

collection_name = "colpali_demo"

# %%
model_name = (
    "vidore/colpali-v1.3"
)
colpali_model = ColPali.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0",  # Use "cuda:0" for GPU, "cpu" for CPU, or "mps" for Apple Silicon
).eval()

colpali_processor = ColPaliProcessor.from_pretrained(
    model_name
)

# %% [markdown]
# ## Testing "ColPali as a Reranker" Approach
# 
# Our goal is to fairly evaluate whether the **"ColPali as a Reranker"** approach on mean and max pooled multivectors performs as well as the original ColPali-based retriever while being much faster. We will test on:
# - **1,000 queries** sampled from the dataset.
# - The **top-20 retrieved PDF pages** for each query, measuring both quality and speed on average.
# 
# Let's randomly subsample **1,000 queries** from our mixed dataset. The queries are saved in the repository for reproducibility (feel free to check them if needed).

# %%
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

# %% [markdown]
# While random sampling provides a good starting point, not all queries in our dataset are well-suited for retrieval.
# 
# These queries:
# - Don’t correspond 1-to-1 to a specific PDF page.
# - Often ask generic questions about a PDF that could relate to multiple documents in the dataset rather than describing or referencing a single page specifically.
# 
# Citing the author of the **UFO dataset** when discussing **ViDoRe**:
# 
# > One thing you might notice about these queries is that many of them are more focused on “questions” about documents rather than traditional search queries. We’ll shortly see the prompting approach used to generate these queries but we might already want to consider, depending on our use case, whether we want to generate more “search”-like queries or more “question”-like queries.”
# 

# %%
random_query_sample[0]

# %% [markdown]
# To address this, we’ll focus on the **UFO subdataset of our 21k points**, which is specifically designed for retrieval tasks. From this subset, we will randomly sample **1,000 queries** for our experiments. These refined queries will ensure that the evaluation is fair in our retrieval approach.
# 

# %%
dataset_ufo = load_dataset("davanstrien/ufo-ColPali", split="train")
dataset_ufo = dataset_ufo.filter(lambda x: x['parsed_into_json']) #ones unparsed were not included in our final collection
ufo_queries = dataset_ufo['specific_detail_query']
ufo_queries = random.sample(ufo_queries, 1000)

# %% [markdown]
# The **1,000 subsampled queries** from the UFO part of our dataset are saved in the repository for reproducibility. Feel free to check them out!
# 
# Now, let’s look at an example to understand why these queries are suitable for retrieval tasks.

# %%
ufo_queries[0]

# %% [markdown]
# Now that we have our **test set** of 1,000 refined queries, it’s time to evaluate the retrieval process.
# 
# But before diving into testing, let’s take a closer look at how **ColPali processes and embeds textual queries**.

# %%
with torch.no_grad():
    batch_query = colpali_processor.process_queries([ufo_queries[0]]).to(
        colpali_model.device
    )
    print(colpali_processor.tokenizer.tokenize(
        colpali_processor.decode(batch_query.input_ids[0])
    ))

# %% [markdown]
# We notice the following:
# - Queries are prefixed with `"Query:"` and include the `<bos>` (beginning of sentence) token.
# - **A significant number of `<pad>` tokens** are added to the end of each query.
# 
# While these `<pad>` tokens contribute to a query representation, they also increase the number of multivectors embedding a query — sometimes even doubling it. This raises an interesting question:  
# **What happens if we remove the `<pad>` tokens from the query?**
# 
# To explore this, we use a function that embeds ColPali queries both:
# 1. **With `<pad>` tokens ("full").**
# 2. **Without `<pad>` tokens ("cut").**

# %%
def colpali_query(query): #per query
    with torch.no_grad():
        batch_query = colpali_processor.process_queries([query]).to(
            colpali_model.device
        )
        mask_without_pad = batch_query.input_ids.bool().unsqueeze(-1)
    query_embedding = colpali_model(**batch_query)
    query_without_pad = torch.masked_select(query_embedding, mask_without_pad).view(1, -1, 128)
    return {
        "full": query_embedding[0].cpu().float().numpy().tolist(),
        "cut": query_without_pad[0].cpu().float().numpy().tolist()
    }

# %% [markdown]
# Embedding test queries with ColPali

# %%
ufo_queries_sample_embeddings = [colpali_query(sample) for sample in ufo_queries]

# %% [markdown]
# > **Note:** The encoded embeddings have already been saved in the repository for reproducibility. Feel free to check it out!
# 
# 

# %% [markdown]
# ### Creating the Ground Truth for Comparison
# 
# To evaluate the performance of our experiments, we first need to establish a **ground truth**. This will serve as the benchmark against which we’ll compare all optimized approaches.
# 
# #### Ground Truth Setup
# For our ground truth, we will:
# 1. Use the original **1,030 ColPali vectors** for retrieval.
# 2. Perform retrieval in **exact mode**. This ensures we don’t need to account for the approximations introduced by index-based searches.
# 
# ### Implementing a Batch Search Function
# 
# 

# %%
def search_qdrant_batch(query_batch,
                        named_vector,
                        query_state="full", #or "cut", related to <pad> tokens
                        search_limit=20,
                        timeout=1000,
                        collection_name="colpali_demo"
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

# %% [markdown]
# Running it.

# %%
batch_size = 8
ufo_full_exact_search_result = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    current_batch_size = len(batch_embeddings)
    batch_result = search_qdrant_batch(batch_embeddings,
                                       'initial'
                                       )
    ufo_full_exact_search_result += batch_result

# %% [markdown]
# We see that **search takes an average of 30 seconds per iteration (batch of 8 queries)**, however, considering **network latency**: since the search is performed on a remote Qdrant cluster, network delays contribute to the overall time.  
#    *(Testing the same retrieval process locally on Qdrant will show how faster it can be.)*
# 
# Although the time measured using `tqdm` is not entirely precise, it’s **sufficient to show relative differences in search times** between the ground truth and optimized approaches.

# %% [markdown]
# ### Setting Up the "ColPali as a Reranker"
# 
# To test our approach, we will now set up a **batch prefetch search**:
# 1. **Pooled vectors** are used as the **first-stage retriever** of 200 vectors (oversampling rate of **10**.
# 2. **Original ColPali vectors** are used only for **reranking** 200 retrieved documents, and selecting top-20 out of them
# 
# We are using Qdrant's [**Prefetch functionality**](https://qdrant.tech/documentation/concepts/hybrid-queries/?q=+Multi-Stage+Queries#multi-stage-queries), which is also ideal for hybrid multi-stage queries.
# 
# #### Experiment Details
# 
# We’re testing two pooling strategies for prefetch:
# - **Max pooling**: Pooling image grid rows by taking the maximum value per patch vector dimension (128).
# - **Mean pooling**: Pooling image grid rows by averaging values per patch vector dimension.
# 
# Notes:
# 
# [NB] **HNSW Index**: Built using quantized vectors if quantization is set up.
# 
# [NB] **Prefetch and Rescoring by Shard**:
#    - Our experimental collection is split into **4 shards**.
#    - Each shard prefetches 200 documents and selects top-20 after rescoring.
#    - The **final top-20 results** are fused from the 80 rescored points across shards.
# 
# [NB] **RAM Storage**: All vectors are stored in RAM for this experiment, ensuring no caching effects. This shouldn't align with production setups.
# 
# [NB] **Exact Search Mode**: When using exact search mode, only the original vectors are used, even if a quantisation configuration is set up.

# %%
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
                                 collection_name="colpali_demo"
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

# %% [markdown]
# Let's test

# %%
batch_size = 8
ufo_full_exact_search_result_prefetch_max = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    batch_result_max = search_prefetch_qdrant_batch(batch_embeddings, 'initial', 'max_pooling')
    ufo_full_exact_search_result_prefetch_max += batch_result_max

# %%
batch_size = 8
ufo_full_exact_search_result_prefetch_mean = []

for i in tqdm(range(0, len(ufo_queries_sample_embeddings), batch_size)):
    batch_embeddings = ufo_queries_sample_embeddings[i:i + batch_size]
    batch_result_mean = search_prefetch_qdrant_batch(batch_embeddings, 'initial', 'mean_pooling')
    ufo_full_exact_search_result_prefetch_mean += batch_result_mean

# %% [markdown]
# ### Step 11: Evaluating Speed and Quality
# 
# The experimental search pipeline is **more than 10 times faster** than the original ColPali retrieval process. While this speedup is expected, the key question is:
# 
# **What about the quality?**  
# How do the retrieved PDF pages differ between this method and the original ColPali?
# 
# To answer it, we’ll use the [`ranx`](https://github.com/AmenRa/ranx) library.
# 
# The `ranx` library is designed for ranking and evaluation tasks, but it requires a specific input format. To make it compatible with our experiment, we created a function to map the results returned by Qdrant into a list of dictionaries that `ranx` can process.
# 
# Since we don’t have explicit relevance scores for documents, we use the ground truth retrieval order to assign **integer relevance ranks**:
# - For the **top-20 results** returned by Qdrant in the ground truth:
#   - The **top-1 document** is assigned a rank of **20**.
#   - The **top-2 document** is assigned a rank of **19**, and so on, down to **1**.
# 
# In the next step, we’ll calculate quality metrics using `ranx` to determine if **max pooling** or **mean pooling** deliver decent retrieval performance relative to the original ColPali.

# %%
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

# %%
qrels_ufo = Qrels(prep_for_ranx(ufo_full_exact_search_result), name="ufo_original_ColPALI")
run_max_ufo = Run(prep_for_ranx(ufo_full_exact_search_result_prefetch_max), name="ufo_prefetch_ColPALI_maxpool")
run_mean_ufo = Run(prep_for_ranx(ufo_full_exact_search_result_prefetch_mean), name="ufo_prefetch_ColPALI_meanpool")

# %% [markdown]
# The processed Qrels and Runs have already been saved in the repository for reproducibility. Feel free to check them out!

# %% [markdown]
# ### Choosing Evaluation Metrics
# 
# To compare the results retrieved by our method with the original ColPali retrieval, we’ll use the following metrics:
# 
# 1. **`NDCG@20` (Normalized Discounted Cumulative Gain)**:  
#    This metric evaluates the ranking quality of the top-20 retrieved documents. If the NDCG score is close to 1, it indicates that the ranking of the results from the pooling method closely aligns with the original method.  
#    Learn more: [NDCG Documentation](https://amenra.github.io/ranx/metrics/#ndcg)
# 
# 2. **`Recall@20`**:  
#    Recall measures the overlap between the relevant documents retrieved by the pooling method and those retrieved by the original method.
#    Since all documents retrieved by the original ColPali are considered relevant in this experiment, `Recall` measures how many of those documents are found by the pooled-prefetching method.  
#    Learn more: [Recall Documentation](https://amenra.github.io/ranx/metrics/#recall)
# 
# If both **`NDCG@20`** and **`Recall@20`** are close to 1:
# - It means that the **top-20 results** retrieved by the pooling method are almost identical to those retrieved by the original ColPali method.
# - This would suggest that the pooling method can effectively replace the original method while significantly improving speed.
# 
# Next, we’ll calculate these metrics for both **mean pooling** and **max pooling** to determine which pooling strategy performs better.

# %%
report_ufo = compare(
    qrels=qrels_ufo,
    runs=[run_max_ufo, run_mean_ufo],
    metrics=["ndcg@20", "recall@20"]
)

print(report_ufo)

# %% [markdown]
# We observe that **mean pooling** performs well, maintaining retrieval quality close to the original ColPali method!
# 
# #### Next Step: Cutting `<pad>` Tokens & Binary Quantization
# To push the boundaries of speed, we’ll test other optimizations: **prefetching with queries where `<pad>` tokens are removed** (so to **reduce the number of multivectors per query**) and **prefetching with binary quantized vectors.**

# %%
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

# %%
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

# %%
run_mean_ufo_cut = Run(prep_for_ranx(ufo_cut_exact_search_result_prefetch_mean), name="ufo_prefetch_ColPALI_meanpool_cut")
run_mean_ufo_binary = Run(prep_for_ranx(binary_ufo_full_exact_search_result_prefetch_mean), name="ufo_prefetch_ColPALI_meanpool_binary")

# %% [markdown]
# The processed Runs have already been saved in the repository for reproducibility. Feel free to check them out!

# %%
report_ufo = compare(
    qrels=qrels_ufo,
    runs=[run_max_ufo, run_mean_ufo, run_mean_ufo_cut, run_mean_ufo_binary],
    metrics=["ndcg@20", "recall@20"]
)

print(report_ufo)

# %% [markdown]
# 1. **Cutting Queries**:  
#    Removing `<pad>` tokens from queries slightly improves search speed without significantly degrading results.
# 
# 2. **Binary Quantization**:  
#    While enabling binary quantization speeds up retrieval, it noticeably affects quality.
# 
# ## Conclusion
# ### What We’ve Tested
# In this notebook, we explored:
# - **Max pooling vs. mean pooling** of image grid rows for prefetch.
# - **Cut queries** (removing `<pad>` tokens) vs. **full queries** for prefetch.
# - **Binary quantized vectors** vs. **original vectors** for prefetch.
# 
# ### Future Directions
# Additional experiments that could be done include:
# - Testing **mean pooling** of image grid **columns**.
# - Rescoring with **half-precision vectors (`float16`)**.
# - Omitting the **6 special multivectors** for prefetch.
# - Combining **binary quantization with oversampling**.
# 
# These optimizations show that **ColPali can now be used in Qdrant up to 10 times faster**! Have fun testing and building faster, more efficient retrieval pipelines with ColPali and Qdrant!


