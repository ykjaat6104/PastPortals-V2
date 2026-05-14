"""PastPortals backend application entrypoint using FastAPI."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_404_NOT_FOUND

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    from .config import get_config
    from .fastapi_routes import (
        config_router,
        museum_router,
        multimodal_router,
        qa_router,
        set_museum_api_key,
        set_vector_db,
        summarize_router,
        translate_router,
    )
except ImportError:  # pragma: no cover - fallback for direct execution
    from config import get_config
    from fastapi_routes import (
        config_router,
        museum_router,
        multimodal_router,
        qa_router,
        set_museum_api_key,
        set_vector_db,
        summarize_router,
        translate_router,
    )


def create_app() -> FastAPI:
    config = get_config()
    app = FastAPI(
        title="PastPortals API",
        version="2.0.0",
        description="Worldwide historical and museum exploration powered by AI",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
    Path(config.GENERATED_IMAGES_DIR).mkdir(parents=True, exist_ok=True)

    @app.on_event("startup")
    async def startup_event() -> None:
        print("\n" + "=" * 60)
        print("PASTPORTALS - Backend Server")
        print("=" * 60)
        print(f"\nEnvironment: {config.ENV}")

        if config.ENV == "production":
            print("   Mode: Production (lightweight)")
            print("   AI Models: Using Gemini API only")
            print("   Vector DB: Disabled (uses Wikipedia API)")
            set_vector_db(None, None)
        else:
            try:
                from .utils.vector_utils import load_vector_db
                from .utils.ai_utils import get_embeddings_model
            except ImportError:  # pragma: no cover - direct execution fallback
                from utils.vector_utils import load_vector_db
                from utils.ai_utils import get_embeddings_model

            embeddings_model = get_embeddings_model(config.EMBEDDING_MODEL)
            embeddings_status = "Loaded" if embeddings_model else "Failed"
            print(f"   Embeddings Model: {embeddings_status}")

            vector_index, text_map = load_vector_db(config.FAISS_INDEX_FILE, config.TEXT_MAP_FILE)
            vector_status = f"Loaded ({vector_index.ntotal} vectors)" if vector_index and text_map else "Empty (will use online sources)"
            print(f"   Vector Database: {vector_status}")
            set_vector_db(vector_index, text_map)

        try:
            from .utils.ai_utils import setup_gemini
        except ImportError:  # pragma: no cover - direct execution fallback
            from utils.ai_utils import setup_gemini

        if getattr(config, 'SKIP_GEMINI_SETUP', False):
            ai_status = "Skipped (APP_SKIP_GEMINI_SETUP=true)"
        else:
            if config.GEMINI_API_KEY:
                ai_configured = setup_gemini(config.GEMINI_API_KEY)
                ai_status = "Configured" if ai_configured else "Configuration failed"
            else:
                ai_status = "Not configured (use /api/configure endpoint)"
        print(f"   Gemini AI: {ai_status}")

        if config.SMITHSONIAN_API_KEY:
            set_museum_api_key(config.SMITHSONIAN_API_KEY)
            museum_status = "Configured"
        else:
            museum_status = "No API key (public access only)"
        print(f"   Museum APIs: {museum_status}")
        print("   Wikipedia API: Ready")
        print("=" * 60)
        print(f"Server Ready - http://{config.HOST}:{config.PORT}")
        print(f"Environment: {config.ENV}")
        print(f"CORS Origins: {', '.join(config.CORS_ORIGINS)}")
        print("=" * 60 + "\n")

    @app.get("/")
    async def index() -> dict:
        return {
            "name": "PastPortals API",
            "version": "2.0.0",
            "description": "Worldwide historical and museum exploration powered by AI",
            "endpoints": {
                "health": "/api/health",
                "configure": "/api/configure",
                "ask": "/api/ask",
                "translate": "/api/translate",
                "summarize": "/api/summarize",
                "museum_search": "/api/museum/search",
                "collections": "/api/museum/collections",
            },
            "documentation": "https://github.com/ykjaat6104/Ai-Museum-Guide",
            "status": "operational",
        }

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException):
        if exc.status_code == HTTP_404_NOT_FOUND:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Endpoint not found",
                    "message": "The requested resource does not exist",
                    "available_endpoints": [
                        "/api/health",
                        "/api/configure",
                        "/api/ask",
                        "/api/translate",
                        "/api/summarize",
                        "/api/museum/search",
                    ],
                },
            )

        status_code = exc.status_code if isinstance(exc.status_code, int) else 500
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(
            status_code=status_code,
            content={"error": detail, "message": detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again.",
            },
        )

    app.include_router(config_router)
    app.include_router(qa_router)
    app.include_router(multimodal_router)
    app.include_router(translate_router)
    app.include_router(summarize_router)
    app.include_router(museum_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    uvicorn.run(app, host=config.HOST, port=config.PORT, reload=config.DEBUG)
