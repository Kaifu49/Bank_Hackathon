from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {
        "service": "explainer",
        "status": "healthy"
    }


@app.post("/explain")
def explain():
    return {
        "narrative": "placeholder"
    }