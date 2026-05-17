# pipeline/rag.py
import os
import pickle
import numpy as np
from openai import OpenAI
from google.cloud import storage

BUCKET    = os.environ.get("GCS_BUCKET", "ai-claims-denial-data")
INDEX_DIR = "rag/index"

client_oai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
client_gcs = storage.Client()

def download_from_gcs(gcs_path, local_path):
    bucket = client_gcs.bucket(BUCKET)
    blob   = bucket.blob(gcs_path)
    blob.download_to_filename(local_path)

def load_index():
    os.makedirs("/tmp/rag_index", exist_ok=True)

    download_from_gcs(f"{INDEX_DIR}/embeddings.npy", "/tmp/rag_index/embeddings.npy")
    download_from_gcs(f"{INDEX_DIR}/chunks.pkl",     "/tmp/rag_index/chunks.pkl")
    download_from_gcs(f"{INDEX_DIR}/sources.pkl",    "/tmp/rag_index/sources.pkl")

    embeddings = np.load("/tmp/rag_index/embeddings.npy")

    with open("/tmp/rag_index/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    with open("/tmp/rag_index/sources.pkl", "rb") as f:
        sources = pickle.load(f)

    return chunks, embeddings, sources

def get_embedding(text: str) -> np.ndarray:
    response = client_oai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(vec_a, vec_b):
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def retrieve_policy(query, chunks, embeddings, sources, top_k=1):
    query_vec    = get_embedding(query)
    similarities = [cosine_similarity(query_vec, embeddings[i]) for i in range(len(chunks))]
    top_indices  = np.argsort(similarities)[::-1][:top_k]
    return [{"policy_source": sources[i], "policy_text": chunks[i]} for i in top_indices]

def run_rag(shap_results: dict):
    chunks, embeddings, sources = load_index()
    results = {}

    for claim_id, reasons in shap_results.items():
        query  = f"{reasons.get('reason_1', '')}. {reasons.get('reason_2', '')}".strip()
        top    = retrieve_policy(query, chunks, embeddings, sources, top_k=1)
        results[claim_id] = {
            "policy_source": top[0]["policy_source"],
            "policy_text"  : top[0]["policy_text"]
        }

    return results