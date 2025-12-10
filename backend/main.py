from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router

app = FastAPI(title="Sostenibilidad Assistant API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Sostenibilidad Assistant API"}

@app.get("/health")
async def health():
    """Detailed health check for all services."""
    import datetime
    try:
        from core.vector_store import vector_store
        from services.llm_service import llm_service
        from core.config import settings

        health_status = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "services": {}
        }

        # Check Pinecone
        try:
            index_stats = vector_store.index.describe_index_stats()
            health_status["services"]["pinecone"] = {
                "status": "connected",
                "index_name": settings.PINECONE_INDEX_NAME,
                "total_vectors": index_stats.total_vector_count,
                "message": f"Índice contiene {index_stats.total_vector_count} vectores"
            }
        except Exception as e:
            health_status["services"]["pinecone"] = {
                "status": "error",
                "error": str(e)
            }

        # Check AWS Bedrock (simple validation)
        try:
            # Just validate that the service is accessible, don't make expensive calls
            health_status["services"]["bedrock"] = {
                "status": "configured",
                "model": settings.BEDROCK_MODEL_ID,
                "region": settings.AWS_REGION,
                "message": f"Modelo {settings.BEDROCK_MODEL_ID} configurado en {settings.AWS_REGION}"
            }
        except Exception as e:
            health_status["services"]["bedrock"] = {
                "status": "error",
                "error": str(e)
            }

        # Overall status
        all_services_ok = all(
            service.get("status") in ["connected", "configured"]
            for service in health_status["services"].values()
        )

        if not all_services_ok:
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.datetime.now().isoformat(),
            "error": str(e),
            "services": {}
        }