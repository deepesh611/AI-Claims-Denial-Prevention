import os
import numpy as np


rag = "/Volumes/main/gold/rag"
INDEX_DIR  = f"{rag}/index"

embeddings = np.load(os.path.join(INDEX_DIR, "embeddings.npy"))
print(embeddings.shape)
