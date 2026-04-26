import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import requests
from bs4 import BeautifulSoup
import os
from validators_utils import valid_format, site_live

# Paths
DATA_PATH = "data/website_classification.csv"
EMBED_PATH = "embeddings/dataset_embeddings.npy"

# Load dataset & embeddings
df = pd.read_csv(DATA_PATH)
embeddings = np.load(EMBED_PATH)

# Prepare text
if 'cleaned_website_text' in df.columns:
    df['text'] = df['cleaned_website_text']
    df['text'] = df['text'].str.lower()
else:
    # fallback (just use URL)
    df['text'] = df['website_url'].str.replace(r'\.com|\.org|\.net', '', regex=True)
    df['text'] = df['text'].str.replace(r'[^a-zA-Z0-9 ]', ' ', regex=True)

# Load embedding model
model = SentenceTransformer('all-mpnet-base-v2')

# Label encoding for categories
le = LabelEncoder()
df['Category_encoded'] = le.fit_transform(df['Category'])

# Train small KNN classifier for category detection
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(embeddings, df['Category_encoded'])

# Scrape website for text
def scrape_website(url):
    try:
        response = requests.get("https://" + url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else ''

        description_tag = soup.find('meta', attrs={'name':'description'})
        description = description_tag['content'] if description_tag else ''

        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs[:10]])

        text = (url + " " + title + " " + description + " " + content).lower()

        return text

    except:
        return url.lower()
    
# Predict category automatically
def predict_category(text):
    vec = model.encode([text])
    
    distances, indices = knn.kneighbors(vec)
    
    # average distance (lower = better)
    avg_distance = distances.mean()

    cat_encoded = knn.predict(vec)[0]
    category = le.inverse_transform([cat_encoded])[0]

    return category, avg_distance

# Find similar websites
def find_similar_websites(user_url, top_n=5, user_category=None):

    # STEP 1 Validation
    if not valid_format(user_url):
        return "Invalid URL format"

    if not site_live(user_url):
        return "Website inactive or unreachable"
    
    # Step 1: scrape better text
    user_text = scrape_website(user_url).lower()

    # Step 2: encode user
    user_vec = model.encode([user_text])

    # Step 3: use FULL dataset (no category filtering)
    similarities = cosine_similarity(user_vec, embeddings)[0]

    # Step 4: get top matches
    top_indices = similarities.argsort()[-top_n:][::-1]

    return df.iloc[top_indices][['website_url', 'Category']]