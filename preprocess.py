import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Paths
DATA_PATH = "data/website_classification.csv"
EMBED_PATH = "embeddings/dataset_embeddings.npy"

# Create embeddings folder if it doesn't exist
os.makedirs("embeddings", exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Prepare text: use 'cleaned_website_text'
if 'cleaned_website_text' in df.columns:
    df['text'] = (
    df['website_url'].fillna('') + " " +
    df['cleaned_website_text'].fillna('') + " " +
    df['Category'].fillna('')
)
else:
    # fallback: use URL without .com/.org/.net
    df['text'] = df['website_url'].str.replace(r'\.com|\.org|\.net', '', regex=True)
    df['text'] = df['text'].str.replace(r'[^a-zA-Z0-9 ]', ' ', regex=True)

# Load embedding model
model = SentenceTransformer('all-mpnet-base-v2')

# Precompute embeddings
print("Encoding dataset texts...")
embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)
np.save(EMBED_PATH, embeddings)

print("Embeddings precomputed and saved to", EMBED_PATH)