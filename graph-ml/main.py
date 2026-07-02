from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {
        "service": "graph_ml",
        "status": "healthy"
    }


@app.post("/graph-ml")
def graph_ml():
    return {
        "gnn_score": 0.0,
        "embeddings": []
    }