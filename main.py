from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from similarity import find_similar_websites

app = FastAPI(title="Website Recommendation API")

# allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message":"API running"
    }


@app.get("/recommend")
def recommend(
    url:str,
    category:str=None
):

    results = find_similar_websites(
        user_url=url,
        user_category=category
    )

    if isinstance(results,str):
        return {
            "error":results
        }

    return {
        "recommendations":
        results.to_dict(
            orient="records"
        )
    }