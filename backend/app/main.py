from fastapi import FastAPI

app = FastAPI(
    title="intervu",
    description="Real-time AI interview and post-session analysis platform",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.get("/")
async def root():
    return {
        "message": "intervu"
    }