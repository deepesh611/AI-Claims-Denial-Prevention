import os
import pickle
import time
import pdfplumber
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()
GCS_BUCKET   = "ai-claims-denial-data"
POLICY_DIR   = "data/policies/"         # local folder where your 6 PDFs are
INDEX_DIR    = "/tmp/rag_index/"   # build locally first, then upload

client_oai   = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
client_gcs   = storage.Client()

def upload_to_gcs(local_path, gcs_path):
    bucket = client_gcs.bucket(GCS_BUCKET)
    blob   = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} to gs://{GCS_BUCKET}/{gcs_path}")

def get_embedding(text, retries=3):
    for attempt in range(retries):
        try:
            response = client_oai.embeddings.create(
                input=text,
                model="text-embedding-3-small",
                timeout=30
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  Retry {attempt+1}/{retries} — {e}")
            time.sleep(3)
    raise Exception(f"Failed after {retries} retries")

def extract_text_from_pdf(fpath):
    full_text = ""
    with pdfplumber.open(fpath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

def chunk_text(text, chunk_size=100):
    words  = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
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
        print(f"  Embedding chunk {i+1}/{len(all_chunks)}")
        embeddings.append(get_embedding(chunk))
    embeddings = np.array(embeddings)

    print("Saving index locally...")
    os.makedirs(INDEX_DIR, exist_ok=True)
    np.save(os.path.join(INDEX_DIR, "embeddings.npy"), embeddings)
    with open(os.path.join(INDEX_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)
    with open(os.path.join(INDEX_DIR, "sources.pkl"), "wb") as f:
        pickle.dump(all_sources, f)

    print("Uploading index to GCS...")
    upload_to_gcs(os.path.join(INDEX_DIR, "embeddings.npy"), "rag/index/embeddings.npy")
    upload_to_gcs(os.path.join(INDEX_DIR, "chunks.pkl"),     "rag/index/chunks.pkl")
    upload_to_gcs(os.path.join(INDEX_DIR, "sources.pkl"),    "rag/index/sources.pkl")

    print("Done.")

build_index()