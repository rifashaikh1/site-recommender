import pandas as pd
import numpy as np
import requests
import re

from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Paths
# -----------------------------
DATA_PATH = "data/website_classification.csv"
EMBED_PATH = "embeddings/dataset_embeddings.npy"

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv(DATA_PATH)
embeddings = np.load(EMBED_PATH)

TEXT_COL = "cleaned_website_text"
URL_COL = "website_url"
CATEGORY_COL = "Category"

# -----------------------------
# Embedding model
# MUST match preprocess.py
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")


# =============================
# URL cleaning
# =============================
def clean_url(url):
    url = url.lower().strip()

    url = url.replace("https://","").replace("http://","")
    url = url.replace("www.","")
    url = url.split("/")[0]

    return url


# =============================
# Detect nonsense domains
# =============================
def is_gibberish_domain(domain):
    name = domain.split(".")[0]

    # too short nonsense
    if len(name) < 5:
        return True

    vowels = sum(c in "aeiou" for c in name)

    # suspicious random strings
    if vowels == 0:
        return True

    if vowels / len(name) < 0.15:
        return True

    return False


# =============================
# Check reachable
# =============================
def fetch_page(url):
    candidates = [
        f"https://{clean_url(url)}",
        f"http://{clean_url(url)}"
    ]

    for u in candidates:
        try:
            r = requests.get(
                u,
                timeout=6,
                headers={
                    "User-Agent":
                    "Mozilla/5.0"
                }
            )

            if r.status_code < 400:
                return r.text

        except:
            pass

    return None


# =============================
# parked domain detector
# =============================
def is_parked(html):
    if not html:
        return False

    html = html.lower()

    markers = [
        "domain for sale",
        "buy this domain",
        "parked free",
        "courtesy of godaddy",
        "this domain is parked",
        "parkingcrew"
    ]

    return any(x in html for x in markers)


# =============================
# scrape metadata
# =============================
def scrape_website(url):

    html = fetch_page(url)

    if not html:
        return None

    if is_parked(html):
        return "PARKED"

    try:
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        title = (
            soup.title.get_text(strip=True)
            if soup.title else ""
        )

        desc = ""

        meta = soup.find(
            "meta",
            attrs={"name":"description"}
        )

        if meta:
            desc = meta.get(
                "content",""
            )

        text = (title+" "+desc).strip()

        return text if len(text)>5 else None

    except:
        return None


# =============================
# URL intent inference
# only for meaningful dead URLs
# =============================
def infer_category_from_url(url):

    url = clean_url(url)

    if is_gibberish_domain(url):
        return None

    tokens = re.findall(
        r"[a-z]+",
        url.lower()
    )

    token_text = " ".join(tokens)

    keyword_map = {
        "Travel":[
            "travel","trip","flight",
            "hotel","booking","tour"
        ],

        "E-Commerce":[
            "shop","store","sale",
            "fashion","clearance",
            "buy","cart"
        ],

        "News":[
            "news","times",
            "journal","media"
        ],

        "Computers and Technology":[
            "tech","cloud",
            "software","code"
        ]
    }

    for cat,words in keyword_map.items():

        if any(
            w in token_text
            for w in words
        ):
            return cat

    return None


# =============================
# Recommend
# =============================
def find_similar_websites(
    user_url,
    top_n=5,
    user_category=None
):

    scraped = scrape_website(user_url)

    # parked domains -> reject
    if scraped == "PARKED":
        return pd.DataFrame({
            "Message":[
                "Parked/placeholder domain. No recommendations."
            ]
        })

    # reachable real site
    if scraped:

        user_vec = model.encode(
            [scraped]
        )

        sims = cosine_similarity(
            user_vec,
            embeddings
        )[0]

        top_idx = sims.argsort()[
            -top_n:
        ][::-1]

        return df.iloc[
            top_idx
        ][
            [URL_COL,CATEGORY_COL]
        ]


    # dead site -> try url inference
    if not user_category:
        user_category = infer_category_from_url(
            user_url
        )

    if not user_category:
        return pd.DataFrame({
            "Message":[
             "Invalid or meaningless domain. No recommendations."
            ]
        })


    filtered = df[
        df[CATEGORY_COL]==user_category
    ]

    if len(filtered)==0:
        return pd.DataFrame({
            "Message":[
             "No matches found."
            ]
        })

    return filtered.sample(
        min(top_n,len(filtered))
    )[
       [URL_COL,CATEGORY_COL]
    ]