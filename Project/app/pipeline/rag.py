# pipeline/rag.py

import os
import pickle
import tempfile
import numpy as np

from openai import OpenAI
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
    host=os.environ["DATABRICKS_HOST"],
    token=os.environ["DATABRICKS_TOKEN"],
    auth_type="pat"
)


def download_file(volume_path, local_path):

    response = w.files.download(volume_path)

    file_data = response.contents.read()

    with open(local_path, "wb") as f:
        f.write(file_data)

# Paths
INDEX_DIR  = "/Volumes/main/gold/rag/index/"

# OpenAI client
client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

def load_index():

    local_dir = tempfile.mkdtemp()

    emb_local = os.path.join(local_dir, "embeddings.npy")
    chunks_local = os.path.join(local_dir, "chunks.pkl")
    sources_local = os.path.join(local_dir, "sources.pkl")

    download_file(
        "/Volumes/main/gold/rag/index/embeddings.npy",
        emb_local
    )

    download_file(
        "/Volumes/main/gold/rag/index/chunks.pkl",
        chunks_local
    )

    download_file(
        "/Volumes/main/gold/rag/index/sources.pkl",
        sources_local
    )

    embeddings = np.load(emb_local)

    with open(chunks_local, "rb") as f:
        chunks = pickle.load(f)

    with open(sources_local, "rb") as f:
        sources = pickle.load(f)

    return chunks, embeddings, sources


def get_embedding(text: str) -> np.ndarray:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))


def retrieve_policy(query: str, chunks: list, embeddings: np.ndarray, sources: list, top_k: int = 1):
    query_vec    = get_embedding(query)
    similarities = [cosine_similarity(query_vec, embeddings[i]) for i in range(len(chunks))]
    top_indices  = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "policy_source": sources[idx],
            "policy_text"  : chunks[idx]
        })

    return results


def run_rag(shap_results: dict):
    """
    Input  : shap_results — dict of claim_id -> {reason_1, reason_2}
    Output : dict of claim_id -> {policy_source, policy_text}
    """
    chunks, embeddings, sources = load_index()

    results = {}
    for claim_id, reasons in shap_results.items():
        reason_1 = reasons.get("reason_1", "")
        reason_2 = reasons.get("reason_2", "")
        query    = f"{reason_1}. {reason_2}".strip()

        top = retrieve_policy(query, chunks, embeddings, sources, top_k=1)

        results[claim_id] = {
            "policy_source": top[0]["policy_source"],
            "policy_text"  : top[0]["policy_text"]
        }

    return results