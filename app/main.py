from fastapi import FastAPI

from app.api.ticket_routes import router as ticket_router


app = FastAPI(
    title="Fintech Multi-Agent Support System",
    description=(
        "AI-powered fintech customer support system "
        "using five specialized AI agents."
    ),
    version="1.0.0",
)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "Fintech Multi-Agent Support System",
    }


app.include_router(ticket_router)
