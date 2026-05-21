# pipeline/rag.py

import os
import logging
import requests
from openai import OpenAI

logger = logging.getLogger(__name__)

# ── Databricks Vector Search Configuration ──────────────────────────────────
DATABRICKS_TOKEN = os.environ["DATABRICKS_TOKEN"]
DATABRICKS_VECTOR_SEARCH_URL = os.environ["DATABRICKS_VECTOR_SEARCH_URL"]

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def get_embedding(text: str) -> list:
    """
    Generate client-side embedding for the query using OpenAI.
    """
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def retrieve_policy(query: str, top_k: int = 1):
    """
    Queries the Databricks Vector Search endpoint via direct REST API using a query vector.
    """
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        logger.error(f"Error generating embedding via OpenAI: {e}")
        return [{
            "policy_source": "Unknown Policy",
            "policy_text": f"Error generating embedding: {str(e)}"
        }]

    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query_vector": query_vector,
        "columns": ["source", "text"],
        "num_results": top_k
    }

    try:
        response = requests.post(
            DATABRICKS_VECTOR_SEARCH_URL,
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        search_response = response.json()
    except Exception as e:
        logger.error(f"Error querying Vector Search REST endpoint: {e}")
        return [{
            "policy_source": "Unknown Policy",
            "policy_text": f"Error retrieving policy: {str(e)}"
        }]

    data = search_response.get("result", {}).get("data_array", [])

    results = []
    if data:
        for row in data:
            # row order follows the columns list: [source, text]
            results.append({
                "policy_source": row[0],
                "policy_text":   row[1]
            })
    else:
        logger.warning(f"No results from Vector Search for query: {query[:80]}...")
        results.append({
            "policy_source": "Unknown Policy",
            "policy_text":   "No matching policy text found."
        })

    return results


def run_rag(shap_results: dict):
    """
    Input  : shap_results — dict of claim_id -> {reason_1, reason_2}
    Output : dict of claim_id -> {policy_source, policy_text}
    """
    results = {}
    for claim_id, reasons in shap_results.items():
        reason_1 = reasons.get("reason_1", "")
        reason_2 = reasons.get("reason_2", "")
        query    = f"{reason_1}. {reason_2}".strip()

        top = retrieve_policy(query, top_k=1)

        results[claim_id] = {
            "policy_source": top[0]["policy_source"],
            "policy_text":   top[0]["policy_text"]
        }

    return results