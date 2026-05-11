# pipelines/rag_index/build_rag_index.py

import os
import pickle
import pdfplumber
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv() 

# Paths
POLICY_DIR = "/Volumes/main/gold/rag/policies/"
INDEX_DIR  = "/Volumes/main/gold/rag/index/"

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def extract_text_from_pdf(fpath: str) -> str:
    full_text = ""
    with pdfplumber.open(fpath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

def chunk_text(text: str, chunk_size: int = 100) -> list:
    words  = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def build_index():
    all_chunks  = []
    all_sources = []

    print("Loading PDFs...")
    for fname in os.listdir(POLICY_DIR):
        if not fname.endswith(".pdf"):
            continue

        fpath  = os.path.join(POLICY_DIR, fname)
        source = fname.replace(".pdf", "").replace("_", " ").title()

        print(f"  Processing: {fname}")
        text   = extract_text_from_pdf(fpath)
        chunks = chunk_text(text)

        all_chunks.extend(chunks)
        all_sources.extend([source] * len(chunks))

    print(f"\nTotal chunks: {len(all_chunks)}")

    print("Building embeddings via OpenAI...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        print(f"  Embedding chunk {i + 1}/{len(all_chunks)}")
        embedding = get_embedding(chunk)
        embeddings.append(embedding)

    embeddings = np.array(embeddings)

    print("Saving index to Volume...")
    os.makedirs(INDEX_DIR, exist_ok=True)

    np.save(os.path.join(INDEX_DIR, "embeddings.npy"), embeddings)

    with open(os.path.join(INDEX_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)

    with open(os.path.join(INDEX_DIR, "sources.pkl"), "wb") as f:
        pickle.dump(all_sources, f)

    print("Index built and saved successfully.")
    print(f"  Chunks    : {len(all_chunks)}")
    print(f"  Embeddings: {embeddings.shape}")

# Run
build_index()