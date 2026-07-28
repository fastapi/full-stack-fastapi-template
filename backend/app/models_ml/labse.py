from app.core import labse_client, langid_client
from pydantic import BaseModel
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
from openai import OpenAI
import numpy as np
import faiss
import time

# Define request and response models
class LaBSERequestInput(BaseModel):
    src: str  # Source text
    ref: str   # Human translation (reference)

class LaBSERequestOutput(BaseModel):
    src: str
    ref: str
    score: float  # Single quality score

class LaBSERequestResponse(BaseModel):
    system_score: float  # Overall average score
    estimates: list[LaBSERequestOutput]

class AlignmentInput(BaseModel):
    src: list[str]
    ref: list[str]

class AlignmentOutput(BaseModel):
    src: str
    ref: str

class AlignmentResponse(BaseModel):
    message: str
    sentences: list[AlignmentOutput]

# Define request models
class AlignmentInputSingle(BaseModel):
    src: list[str]  # Single list of source strings


def find_invalid_xml_characters(text):
    for char in text:
        # Check if the character is a valid XML character
        if not (0x20 <= ord(char) <= 0xD7FF or 0xE000 <= ord(char) <= 0xFFFD or 0x10000 <= ord(char) <= 0x10FFFF):
            return True
    return False

def generate_tmx(data: list[AlignmentOutput]) -> str:

    # Create the TMX root element
    tmx = ET.Element("tmx", version="1.4")

    # Create the header element
    header = ET.SubElement(tmx, "header",
        creationtool="BTB LS Platform",
        creationtoolversion="1.0",
        attrib={'o-tmf': "BTB TM Format"},
        datatype="xml",
        segtype="sentence",
        adminlang="en-ca",
        srclang="en-ca",
        creationdate=datetime.now(timezone.utc).strftime("%Y%m%d"),
        creationid="PWGSC-TPSGC-EM\\MrAI"
    )

    # Add properties to the header
    properties = [
        ("x-ID et No de demande:MultipleString", ""),
        ("x-Description:SinglePicklist", "AI System Generated"),
        ("x-Recognizers", "RecognizeAll"),
        ("x-IncludesContextContent", "True"),
        ("x-TMName", "AI System Generated"),
        ("x-TokenizerFlags", "DefaultFlags"),
        ("x-WordCountFlags", "DefaultFlags")
    ]

    for prop_type, prop_value in properties:
        prop = ET.SubElement(header, "prop", type=prop_type)
        prop.text = prop_value

    body = ET.SubElement(tmx, "body")

    # Loop through the list of AlignmentInput objects
    for alignment in data:

        if find_invalid_xml_characters(alignment.src) :
            print(alignment.src) 
            continue
        if find_invalid_xml_characters(alignment.ref):
            print(alignment.ref) 
            continue

        tu = ET.SubElement(body, "tu")
        
        tuv_source = ET.SubElement(tu, 'tuv', attrib={'xml:lang' : "en-ca"})
        seg_source = ET.SubElement(tuv_source, "seg")
        seg_source.text = saxutils.escape(alignment.src)  # Escape the source text
        
        tuv_target = ET.SubElement(tu, 'tuv', attrib={'xml:lang' : "fr-ca"})
        seg_target = ET.SubElement(tuv_target, "seg")
        seg_target.text = saxutils.escape(alignment.ref)

    # Convert the XML tree to a string
    return ET.tostring(tmx, encoding="unicode", method="xml")


########  Functions to find and score candidates
def score(x, y, fwd_mean, bwd_mean, margin):
    return margin(x.dot(y), (fwd_mean + bwd_mean) / 2)

def score_candidates(x, y, candidate_inds, fwd_mean, bwd_mean, margin):
    scores = np.zeros(candidate_inds.shape)
    for i in range(scores.shape[0]):
        for j in range(scores.shape[1]):
            k = candidate_inds[i, j]
            scores[i, j] = score(x[i], y[k], fwd_mean[i], bwd_mean[k], margin)
    return scores

def kNN(x, y, k, use_ann_search=False, ann_num_clusters=32768, ann_num_cluster_probe=3):
    start_time = time.time()
    if use_ann_search:
        print("Perform approx. kNN search")
        n_cluster = min(ann_num_clusters, int(y.shape[0] / 1000))
        quantizer = faiss.IndexFlatIP(y.shape[1])
        index = faiss.IndexIVFFlat(quantizer, y.shape[1], n_cluster, faiss.METRIC_INNER_PRODUCT)
        index.nprobe = ann_num_cluster_probe
        index.train(y)
        index.add(y)
        sim, ind = index.search(x, k)
    else:
        print("Perform exact search")
        idx = faiss.IndexFlatIP(y.shape[1])
        idx.add(y)
        sim, ind = idx.search(x, k)

    print(f"Done: {time.time() - start_time:.2f} sec")
    return sim, ind


async def calculate_labse(data: list[LaBSERequestInput]) -> LaBSERequestResponse:

    sources = [item.src.strip() for item in data]
    targets = [item.ref.strip() for item in data]  # Ensure trimming whitespace

    # Scored service-side: only the diagonal of the full matmul was ever used,
    # so N scores cross the wire instead of 2N embeddings.
    scores, _ = await labse_client.similarity(sources, targets)

    results = []
    for idx in range(len(data)):
        single_score = round(scores[idx], 4)
        results.append(LaBSERequestOutput(src=sources[idx], ref=targets[idx], score=single_score))

    # Optionally calculate a corpus score (e.g., average of individual scores)
    system_score = round(sum(result.score for result in results) / len(results), 4)

    return LaBSERequestResponse(system_score=system_score, estimates=results)


async def align_sentences(request: AlignmentInput) -> AlignmentResponse:

    # Only consider sentences that are between min_sent_len and max_sent_len characters long
    min_sent_len = 10
    max_sent_len = 200

    # We base the scoring on k nearest neighbors for each element
    knn_neighbors = 4

    # Min score for text pairs. Note, score can be larger than 1
    min_threshold = 1.1

    # Do we want to use exact search of approximate nearest neighbor search (ANN)
    # Exact search: Slower, but we don't miss any parallel sentences
    # ANN: Faster, but the recall will be lower
    use_ann_search = False

    # Number of clusters for ANN. Each cluster should have at least 10k entries
    ann_num_clusters = 32768

    # How many cluster to explorer for search. Higher number = better recall, slower
    ann_num_cluster_probe = 3

    source_sentences = list()
    target_sentences = list()

    print("Processing source sentences")
    for line in request.src:
        line = line.strip()
        if min_sent_len <= len(line) <= max_sent_len:
            source_sentences.append(line)

    print("Processing target sentences")
    for line in request.ref:
        line = line.strip()
        if min_sent_len <= len(line) <= max_sent_len:
            target_sentences.append(line)

    print("Source Sentences:", len(source_sentences))
    print("Target Sentences:", len(target_sentences))

    ### Encode source sentences
    print("Encode source sentences")
    source_embeddings = await labse_client.embed(source_sentences)

    ### Encode target sentences
    print("Encode target sentences")
    target_embeddings = await labse_client.embed(target_sentences)

    # Normalize embeddings
    x = source_embeddings
    x = x / np.linalg.norm(x, axis=1, keepdims=True)

    y = target_embeddings
    y = y / np.linalg.norm(y, axis=1, keepdims=True)

    # Perform kNN in both directions
    x2y_sim, x2y_ind = kNN(x, y, knn_neighbors, use_ann_search, ann_num_clusters, ann_num_cluster_probe)
    x2y_mean = x2y_sim.mean(axis=1)

    y2x_sim, y2x_ind = kNN(y, x, knn_neighbors, use_ann_search, ann_num_clusters, ann_num_cluster_probe)
    y2x_mean = y2x_sim.mean(axis=1)

    # Compute forward and backward scores
    margin = lambda a, b: a / b
    fwd_scores = score_candidates(x, y, x2y_ind, x2y_mean, y2x_mean, margin)
    bwd_scores = score_candidates(y, x, y2x_ind, y2x_mean, x2y_mean, margin)
    fwd_best = x2y_ind[np.arange(x.shape[0]), fwd_scores.argmax(axis=1)]
    bwd_best = y2x_ind[np.arange(y.shape[0]), bwd_scores.argmax(axis=1)]

    indices = np.stack(
        [np.concatenate([np.arange(x.shape[0]), bwd_best]), np.concatenate([fwd_best, np.arange(y.shape[0])])], axis=1
    )

    scores = np.concatenate([fwd_scores.max(axis=1), bwd_scores.max(axis=1)])

    seen_src, seen_trg = set(), set()
    results = {}

    # Extract list of parallel sentences
    print("Write sentences to disc")

    for i in np.argsort(-scores):
        src_ind, trg_ind = indices[i]
        src_ind = int(src_ind)
        trg_ind = int(trg_ind)

        if scores[i] < min_threshold:
            break

        if src_ind not in seen_src and trg_ind not in seen_trg:
            seen_src.add(src_ind)
            seen_trg.add(trg_ind)
            #score = scores[i]

            results[src_ind] = AlignmentOutput(
                src=source_sentences[src_ind],
                ref=target_sentences[trg_ind]
            )

    sorted_results = dict(sorted(results.items()))
    return AlignmentResponse(message="Alignment complete", sentences=list(sorted_results.values()))


async def align_sentences_uni(request: AlignmentInputSingle) -> AlignmentResponse:

    # Initialize lists to hold sentences based on detected language
    source_sentences = list()
    target_sentences = list()

    sentences = list()

    for line in request.src:
        line = line.strip()
        if 1 <= len(line) <= 200:
            sentences.append(line)

    # Detected by langid-svc, in one batched call.
    detections = await langid_client.detect(sentences)

    # Iterate over the predicted languages for each sentence
    for i in range(len(sentences)):
        detected_language, confidence = detections[i]

        # Note on the 0.2 gate: lingua normalises confidence across en and fr
        # only, so anything it decides on scores >= 0.5. In practice this now
        # filters exactly the undecidable rows (digits, symbols), which come
        # back as (None, 0.0).

        # Append English sentences to source_sentences
        if detected_language == "en" and confidence > 0.2:
            source_sentences.append(sentences[i])  # Add English sentence to source

        # Append French sentences to target_sentences
        elif detected_language == "fr" and confidence > 0.2:
            target_sentences.append(sentences[i])  # Add French sentence to target

    # Prepare the output response with separated source and target sentences
    return await align_sentences(AlignmentInput(src=source_sentences, ref=target_sentences))


async def align_sentences_special(sentences: AlignmentInputSingle):
    
    prompt = ""

    # Create a prompt for OpenAI to align the sentences
    for s in sentences.src:
        prompt += f"Source: {s}\n"

    # Call OpenAI's API
    client = OpenAI(
        api_key="REDACTED-OPENAI-KEY-SEE-OPENAI_API_KEY-SETTING"
    )

    #You are an experienced translator that is very efficient with bitext extraction. Extract all bitext data for each pair of English and French sentences found.
    # Set your OpenAI API key from environment variable
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract all key terminologies in both English and French from the following text. Only list each English term followed by its French equivalent if both found in the document:"},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=16383,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format=AlignmentResponse
    )

    aligned_text = response.choices[0].message.parsed

    print(aligned_text)

    return aligned_text

# Run the server with: uvicorn your_file_name:app --reload