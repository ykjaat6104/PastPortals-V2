"""FastAPI routers for the PastPortals backend.

This module keeps the existing business logic but exposes it through
FastAPI routers instead of Flask blueprints.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from werkzeug.utils import secure_filename

try:  # Prefer package-relative imports when available.
    from .utils.ai_utils import generate_content, is_gemini_configured
    from .utils.crag_utils import apply_crag
    from .utils.history_utils import (
        generate_fallback_response,
        generate_history_prompt,
        is_historical_question,
    )
    from .utils.museum_utils import get_smithsonian_object, search_multiple_museums
    from .utils.multimodal_utils import (
        extract_multimodal_content,
        generate_multimodal_fallback_response,
    )
    from .utils.vector_utils import get_vector_db_stats, load_vector_db, search_vector_db
    from .utils.wikipedia_utils import (
        get_related_articles,
        get_wikipedia_summary,
        search_and_summarize,
    )
    from .config import get_config
except ImportError:  # pragma: no cover - fallback for direct module execution
    from utils.ai_utils import generate_content, is_gemini_configured
    from utils.crag_utils import apply_crag
    from utils.history_utils import (
        generate_fallback_response,
        generate_history_prompt,
        is_historical_question,
    )
    from utils.museum_utils import get_smithsonian_object, search_multiple_museums
    from utils.multimodal_utils import (
        extract_multimodal_content,
        generate_multimodal_fallback_response,
    )
    from utils.vector_utils import get_vector_db_stats, load_vector_db, search_vector_db
    from utils.wikipedia_utils import (
        get_related_articles,
        get_wikipedia_summary,
        search_and_summarize,
    )
    from config import get_config


qa_router = APIRouter(prefix="/api", tags=["qa"])
translate_router = APIRouter(prefix="/api", tags=["translate"])
summarize_router = APIRouter(prefix="/api", tags=["summarize"])
config_router = APIRouter(prefix="/api", tags=["config"])
museum_router = APIRouter(prefix="/api/museum", tags=["museum"])
multimodal_router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])


vector_index = None
text_map = None
smithsonian_api_key = None


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)


class ConfigureRequest(BaseModel):
    api_key: str = Field(..., min_length=1)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    length: str = "medium"


class KeyPointsRequest(BaseModel):
    text: str = Field(..., min_length=1)
    max_points: int = 5


class MuseumSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = 10
    sources: list[str] = Field(default_factory=lambda: ["smithsonian"])


class DetectLanguageRequest(BaseModel):
    text: str = Field(..., min_length=1)


def set_vector_db(index, t_map):
    global vector_index, text_map
    vector_index = index
    text_map = t_map


def set_museum_api_key(key):
    global smithsonian_api_key
    smithsonian_api_key = key


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _build_related_topics(search_term: str) -> list[dict]:
    topics: list[dict] = []
    if not search_term:
        return topics

    try:
        result = search_and_summarize(search_term)
        if isinstance(result, dict):
            summary = result.get("summary") or result.get("extract") or ""
            if summary:
                topics.append({
                    "query": result.get("query", search_term),
                    "title": result.get("title", search_term),
                    "extract": summary,
                    "description": result.get("description", ""),
                    "url": result.get("url", ""),
                    "search_results": result.get("search_results", []),
                })
    except Exception:
        pass

    return topics


async def _save_upload(uploaded_file: UploadFile) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="pastportals_multimodal_"))
    filename = secure_filename(uploaded_file.filename or "upload")
    file_path = temp_dir / filename
    content = await uploaded_file.read()
    file_path.write_bytes(content)
    return file_path


def _cleanup_path(file_path: Path) -> None:
    try:
        if file_path.exists():
            file_path.unlink()
        if file_path.parent.exists() and not any(file_path.parent.iterdir()):
            file_path.parent.rmdir()
    except Exception:
        pass


async def get_ai_response(question: str) -> dict:
    if not is_historical_question(question):
        return {
            "response": (
                "I specialize in world history and historical topics. Please ask about historical events, "
                "figures, civilizations, wars, cultural movements, or historical places from any time period and region."
            ),
            "source": "filter",
            "wikipedia_info": None,
            "museum_data": None,
        }

    lookup_tasks: list[asyncio.Future] = []
    has_vector_db = bool(vector_index and text_map)

    if has_vector_db:
        lookup_tasks.append(asyncio.to_thread(search_vector_db, question, vector_index, text_map, 2))
    lookup_tasks.append(asyncio.to_thread(search_and_summarize, question))
    lookup_tasks.append(asyncio.to_thread(search_multiple_museums, question, api_key=smithsonian_api_key, limit_per_source=2))

    lookup_results = await asyncio.gather(*lookup_tasks, return_exceptions=True)

    result_offset = 0
    relevant_context = None
    if has_vector_db:
        vector_result = lookup_results[0]
        result_offset = 1
        if not isinstance(vector_result, Exception) and vector_result:
            relevant_context = "\n\n".join(vector_result)

    wikipedia_result = lookup_results[result_offset]
    museum_result = lookup_results[result_offset + 1]

    wikipedia_info = wikipedia_result if not isinstance(wikipedia_result, Exception) else None

    museum_data = None
    if not isinstance(museum_result, Exception) and museum_result and museum_result.get("total_count", 0) > 0:
        museum_data = museum_result
    elif isinstance(museum_result, Exception):
        print(f"Museum search failed: {museum_result}")

    if is_gemini_configured():
        try:
            prompt = generate_history_prompt(question, relevant_context, wikipedia_info, museum_data)
            ai_response = await asyncio.to_thread(generate_content, prompt, 0.7, 3072)

            if ai_response and _word_count(ai_response) < 700:
                expand_prompt = (
                    f"Expand and deepen this answer to approximately 900-1100 words. Keep markdown headings and improve detail, chronology, and analysis.\n\n"
                    f"Original question: {question}\n\n"
                    f"Current answer:\n{ai_response}"
                )
                expanded_response = await asyncio.to_thread(generate_content, expand_prompt, 0.6, 3072)
                if expanded_response and _word_count(expanded_response) > _word_count(ai_response):
                    ai_response = expanded_response

            if not ai_response and wikipedia_info:
                short_prompt = (
                    f"Provide a detailed markdown answer about: {question}. Target around 900-1100 words and include sections: "
                    f"Overview, Historical Context, Key Facts, Cultural Impact, Interesting Details, Modern Legacy, Related Topics. "
                    f"Reference this context: {wikipedia_info.get('extract', '')}"
                )
                ai_response = await asyncio.to_thread(generate_content, short_prompt, 0.5, 2048)

            if ai_response:
                return {
                    "response": ai_response,
                    "source": "ai",
                    "wikipedia_info": wikipedia_info,
                    "museum_data": museum_data,
                    "context_used": relevant_context is not None,
                }
        except Exception as exc:
            print(f"AI response error: {exc}")

    related_summaries: list[dict] = []
    if wikipedia_info:
        try:
            seed_title = wikipedia_info.get("title") or question
            related_titles = await asyncio.to_thread(get_related_articles, seed_title, 5)
            for title in related_titles[:5]:
                summary = await asyncio.to_thread(get_wikipedia_summary, title)
                if summary and summary.get("extract"):
                    related_summaries.append({
                        "title": summary.get("title", title),
                        "extract": summary.get("extract", ""),
                    })
        except Exception as related_error:
            print(f"Related summary fallback warning: {related_error}")

    fallback = generate_fallback_response(
        question,
        relevant_context,
        wikipedia_info,
        related_summaries=related_summaries,
    )
    return {
        "response": fallback,
        "source": "fallback",
        "wikipedia_info": wikipedia_info,
        "museum_data": museum_data,
        "context_used": relevant_context is not None,
    }


@qa_router.post("/ask")
async def ask_question(payload: QuestionRequest):
    result = await get_ai_response(payload.question.strip())
    return {
        "question": payload.question.strip(),
        "answer": result["response"],
        "source": result["source"],
        "wikipedia_info": result.get("wikipedia_info"),
        "museum_data": result.get("museum_data"),
        "context_used": result.get("context_used", False),
        "timestamp": datetime.now().isoformat(),
    }


@qa_router.get("/quick-facts/{topic}")
async def quick_facts(topic: str):
    wikipedia_info = await asyncio.to_thread(search_and_summarize, topic)
    if not wikipedia_info:
        raise HTTPException(status_code=404, detail=f"No information found for topic: {topic}")

    return {
        "topic": topic,
        "query": wikipedia_info.get("query", topic),
        "summary": wikipedia_info.get("extract", ""),
        "description": wikipedia_info.get("description", ""),
        "thumbnail": wikipedia_info.get("thumbnail", ""),
        "url": wikipedia_info.get("url", ""),
        "search_results": wikipedia_info.get("search_results", []),
        "top_result": wikipedia_info.get("top_result", {}),
        "timestamp": datetime.now().isoformat(),
    }


@qa_router.get("/related/{topic}")
async def related_topics(topic: str):
    related = await asyncio.to_thread(get_related_articles, topic, 5)
    detailed_related = []
    for related_topic in related:
        result = await asyncio.to_thread(search_and_summarize, related_topic)
        if isinstance(result, dict):
            detailed_related.append({
                "title": result.get("title", related_topic),
                "extract": result.get("extract", ""),
                "description": result.get("description", ""),
                "url": result.get("url", ""),
                "search_results": result.get("search_results", []),
            })
        else:
            detailed_related.append({
                "title": related_topic,
                "extract": "",
                "description": "",
                "url": "",
                "search_results": [],
            })
    return {
        "topic": topic,
        "related_topics": related,
        "related_topics_detail": detailed_related,
        "count": len(related),
        "timestamp": datetime.now().isoformat(),
    }


SUPPORTED_LANGUAGES = {
    "english": "English",
    "spanish": "Spanish (Español)",
    "french": "French (Français)",
    "german": "German (Deutsch)",
    "italian": "Italian (Italiano)",
    "portuguese": "Portuguese (Português)",
    "russian": "Russian (Русский)",
    "chinese": "Chinese (中文)",
    "japanese": "Japanese (日本語)",
    "korean": "Korean (한국어)",
    "arabic": "Arabic (العربية)",
    "hindi": "Hindi (हिंदी)",
    "bengali": "Bengali (বাংলা)",
    "urdu": "Urdu (اردو)",
    "tamil": "Tamil (தமிழ்)",
    "telugu": "Telugu (తెలుగు)",
    "marathi": "Marathi (मराठी)",
    "gujarati": "Gujarati (ગુજરાતી)",
    "kannada": "Kannada (ಕನ್ನಡ)",
    "malayalam": "Malayalam (മലയാളം)",
}


@translate_router.post("/translate")
async def translate_text(payload: TranslateRequest):
    text = payload.text.strip()
    target_language = payload.language.strip().lower()

    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    if not target_language:
        raise HTTPException(status_code=400, detail="Target language is required")
    if target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Unsupported language: {target_language}",
                "supported_languages": list(SUPPORTED_LANGUAGES.keys()),
            },
        )

    if target_language == "english":
        return {
            "original_text": text,
            "translated_text": text,
            "target_language": SUPPORTED_LANGUAGES[target_language],
            "timestamp": datetime.now().isoformat(),
        }

    if not is_gemini_configured():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "AI translation requires API configuration",
                "suggestion": "Please configure your Gemini API key first",
            },
        )

    language_name = SUPPORTED_LANGUAGES[target_language]
    prompt = f"""
Translate the following historical text to {language_name} while preserving:
1. All proper names, places, and historical terms (keep original or transliterate)
2. Dates and numbers exactly as they appear
3. The formal, educational tone
4. Cultural context and meaning
5. Markdown formatting if present

Text to translate:
{text}

Provide only the translation without any additional commentary or explanations.
"""

    translated = await asyncio.to_thread(generate_content, prompt, 0.3, 2048)
    if not translated:
        raise HTTPException(status_code=500, detail="Translation failed - empty response from AI")

    return {
        "original_text": text,
        "translated_text": translated,
        "target_language": language_name,
        "timestamp": datetime.now().isoformat(),
    }


@translate_router.get("/languages")
async def get_languages():
    return {"languages": SUPPORTED_LANGUAGES, "count": len(SUPPORTED_LANGUAGES)}


@translate_router.post("/detect-language")
async def detect_language(payload: DetectLanguageRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    if not is_gemini_configured():
        raise HTTPException(status_code=400, detail="Language detection requires AI configuration")

    prompt = f"""
Detect the language of the following text and respond with ONLY the language name in English (e.g., "English", "Spanish", "Hindi", etc.):

{text[:500]}

Language:
"""

    detected = await asyncio.to_thread(generate_content, prompt, 0.1, 50)
    if detected:
        language_name = detected.strip()
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "detected_language": language_name,
            "confidence": "high" if len(text) > 50 else "medium",
        }

    raise HTTPException(status_code=500, detail="Failed to detect language")


@summarize_router.post("/summarize")
async def summarize_text(payload: SummarizeRequest):
    text = payload.text.strip()
    length = payload.length.lower()
    if not text:
        raise HTTPException(status_code=400, detail="Text to summarize is required")
    if length not in ["short", "medium", "long"]:
        length = "medium"
    if not is_gemini_configured():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "AI summarization requires API configuration",
                "suggestion": "Please configure your Gemini API key first",
            },
        )

    sentence_limits = {
        "short": "2-3 sentences",
        "medium": "4-5 sentences",
        "long": "8-10 sentences",
    }

    prompt = f"""
Create a concise summary of this historical content:

Guidelines:
- Keep all essential facts, dates, and names
- Maintain historical accuracy
- Length: {sentence_limits[length]}
- Preserve the most important information
- Use clear, educational language
- Maintain markdown formatting if needed

Content to summarize:
{text}

Provide only the summary without additional commentary or preamble.
"""

    summary = await asyncio.to_thread(generate_content, prompt, 0.5, 1024)
    if not summary:
        raise HTTPException(status_code=500, detail="Summarization failed - empty response from AI")

    original_words = len(text.split())
    summary_words = len(summary.split())
    compression_ratio = summary_words / original_words if original_words > 0 else 0

    return {
        "original_length": original_words,
        "summary": summary,
        "summary_length": summary_words,
        "compression_ratio": round(compression_ratio, 2),
        "length_type": length,
        "timestamp": datetime.now().isoformat(),
    }


@summarize_router.post("/key-points")
async def extract_key_points(payload: KeyPointsRequest):
    text = payload.text.strip()
    max_points = payload.max_points
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    if not isinstance(max_points, int) or max_points < 1 or max_points > 10:
        max_points = 5
    if not is_gemini_configured():
        raise HTTPException(status_code=400, detail="Key point extraction requires AI configuration")

    prompt = f"""
Extract the {max_points} most important key points from this historical content.

Guidelines:
- Each point should be concise (1-2 sentences max)
- Focus on facts, dates, and significance
- Number each point (1., 2., 3., etc.)
- Preserve historical accuracy

Content:
{text}

Key Points:
"""

    response = await asyncio.to_thread(generate_content, prompt, 0.3, 512)
    if not response:
        raise HTTPException(status_code=500, detail="Key point extraction failed")

    import re

    points = re.findall(r"\d+\.\s*(.+?)(?=\n\d+\.|\Z)", response, re.DOTALL)
    points = [point.strip() for point in points if point.strip()]

    return {"key_points": points, "count": len(points), "timestamp": datetime.now().isoformat()}


@museum_router.post("/search")
async def search_museums(payload: MuseumSearchRequest):
    query = payload.query.strip()
    limit = payload.limit
    if not query:
        raise HTTPException(status_code=400, detail="Search query is required")
    if not isinstance(limit, int) or limit < 1 or limit > 50:
        limit = 10

    results = await asyncio.to_thread(
        search_multiple_museums,
        query,
        api_key=smithsonian_api_key,
        limit_per_source=limit,
    )

    return {
        "query": query,
        "results": results,
        "total_count": results["total_count"],
        "sources_used": ["smithsonian"],
        "timestamp": datetime.now().isoformat(),
    }


@museum_router.get("/artifact/{artifact_id}")
async def get_artifact(artifact_id: str):
    artifact = await asyncio.to_thread(get_smithsonian_object, artifact_id, api_key=smithsonian_api_key)
    if not artifact:
        raise HTTPException(status_code=404, detail=f"Artifact not found: {artifact_id}")

    return {"artifact": artifact, "timestamp": datetime.now().isoformat()}


@museum_router.get("/collections")
async def get_collections():
    collections = {
        "smithsonian": {
            "name": "Smithsonian Institution",
            "description": "World's largest museum, education, and research complex",
            "collections": [
                "National Museum of Natural History",
                "National Air and Space Museum",
                "National Museum of American History",
                "Smithsonian American Art Museum",
                "National Portrait Gallery",
                "And 14 more museums",
            ],
            "total_items": "155 million+",
            "open_access": True,
            "api_docs": "https://api.si.edu/openaccess",
        },
        "europeana": {
            "name": "Europeana",
            "description": "European cultural heritage collections",
            "collections": ["Art", "Archaeology", "Fashion", "Music", "Photography"],
            "total_items": "50 million+",
            "open_access": True,
            "api_docs": "https://pro.europeana.eu/page/apis",
            "status": "Requires API key registration",
        },
    }

    return {"collections": collections, "available_count": len(collections), "timestamp": datetime.now().isoformat()}


@museum_router.get("/categories")
async def get_categories():
    categories = {
        "art": "Paintings, Sculptures, Art Objects",
        "archaeology": "Ancient Artifacts, Excavation Finds",
        "history": "Historical Objects, Documents",
        "cultural": "Cultural Heritage, Traditional Items",
        "natural_history": "Fossils, Minerals, Specimens",
        "technology": "Inventions, Tools, Machines",
        "decorative_arts": "Furniture, Textiles, Ceramics",
        "photography": "Historical Photographs",
        "manuscripts": "Historical Documents, Letters",
        "numismatics": "Coins, Currency, Medals",
    }

    return {"categories": categories, "count": len(categories)}


@config_router.get("/health")
async def health():
    cfg = get_config()
    vector_db_exists = vector_index is not None and text_map is not None
    vector_count = vector_index.ntotal if vector_db_exists else 0
    embeddings_enabled = cfg.ENV != "production"

    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "ai_configured": is_gemini_configured(),
        "services": {
            "gemini_ai": is_gemini_configured(),
            "wikipedia": True,
            "embeddings": embeddings_enabled,
            "vector_db": vector_db_exists,
            "vector_count": vector_count,
            "museum_api": True,
        },
        "version": "2.0.0",
        "environment": cfg.ENV,
    }


@config_router.post("/configure")
async def configure_api(payload: ConfigureRequest):
    from .utils.ai_utils import setup_gemini
    try:
        success = setup_gemini(payload.api_key.strip())
        if success:
            return {
                "message": "API configured successfully",
                "ai_enabled": True,
                "timestamp": datetime.now().isoformat(),
            }
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Failed to configure API. Please check your API key.",
                "ai_enabled": False,
                "suggestion": "Verify your Gemini API key at https://makersuite.google.com/app/apikey",
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Configuration error: {exc}")


@config_router.get("/status")
async def get_status():
    try:
        config = get_config()
        vector_stats = get_vector_db_stats(vector_index, text_map) if vector_index else {
            "total_vectors": 0,
            "dimension": 0,
            "text_entries": 0,
            "status": "not_initialized",
        }

        try:
            from .utils.ai_utils import get_embeddings_model
        except ImportError:
            from utils.ai_utils import get_embeddings_model

        embeddings = get_embeddings_model(config.EMBEDDING_MODEL) if config.ENV != "production" else None

        return {
            "system": {
                "status": "operational",
                "uptime": "N/A",
                "version": "2.0.0",
                "environment": config.ENV,
            },
            "ai": {
                "gemini_configured": is_gemini_configured(),
                "embeddings_loaded": embeddings is not None,
                "model": "all-mpnet-base-v2" if embeddings else None,
            },
            "database": {
                "vector_db": vector_stats,
                "total_documents": vector_stats["text_entries"],
            },
            "apis": {
                "wikipedia": {"status": "available", "rate_limit": None},
                "smithsonian": {"status": "available", "requires_key": False},
                "europeana": {"status": "requires_registration"},
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve status: {exc}")


@config_router.get("/capabilities")
async def get_capabilities():
    capabilities = {
        "core_features": {
            "historical_qa": {
                "enabled": True,
                "description": "AI-powered Q&A for worldwide history",
                "requires_ai": True,
            },
            "translation": {
                "enabled": is_gemini_configured(),
                "description": "Translate content to 18+ languages",
                "requires_ai": True,
                "languages_supported": 18,
            },
            "summarization": {
                "enabled": is_gemini_configured(),
                "description": "Summarize historical content",
                "requires_ai": True,
            },
            "museum_search": {
                "enabled": True,
                "description": "Search museum collections worldwide",
                "requires_ai": False,
                "museums": ["smithsonian"],
            },
            "wikipedia_integration": {
                "enabled": True,
                "description": "Real-time Wikipedia data",
                "requires_ai": False,
            },
            "vector_search": {
                "enabled": vector_index is not None,
                "description": "Semantic search in knowledge base",
                "requires_ai": False,
            },
        },
        "advanced_features": {
            "multi_source_search": True,
            "context_aware_responses": True,
            "fallback_mode": True,
            "batch_translation": False,
            "image_recognition": True,
            "voice_interface": True,
            "document_upload": True,
            "video_analysis": True,
        },
    }

    return {"capabilities": capabilities, "timestamp": datetime.now().isoformat()}


@multimodal_router.post("/analyze")
async def analyze_multimodal_input(
    question: str = Form(""),
    mode: str = Form("auto"),
    file: UploadFile | None = File(None),
    upload: UploadFile | None = File(None),
):
    question = (question or "").strip()
    input_mode = (mode or "auto").strip().lower()
    uploaded_file = file or upload

    if not question and not uploaded_file:
        raise HTTPException(status_code=400, detail="Provide a question, a file upload, or both.")

    file_details = {"filename": None, "mode": input_mode, "extension": None}
    extracted_text = ""
    extraction_notes: list[str] = []
    extraction_method = "text-only"

    saved_path: Path | None = None
    if uploaded_file and uploaded_file.filename:
        saved_path = await _save_upload(uploaded_file)
        file_details["filename"] = uploaded_file.filename
        file_details["extension"] = saved_path.suffix.lower()

        try:
            extraction = extract_multimodal_content(saved_path, uploaded_file.filename, input_mode)
            extracted_text = extraction.get("text", "") or ""
            extraction_notes = extraction.get("notes", []) or []
            extraction_method = extraction.get("method", "unknown")
            file_details.update(extraction.get("metadata", {}))
        finally:
            if saved_path is not None:
                _cleanup_path(saved_path)

    combined_context = extracted_text.strip() or question
    related_topics = _build_related_topics(question or extracted_text[:120])

    if is_gemini_configured():
        try:
            config = get_config()
            index_path = str(Path(config.DATA_DIR) / "faiss_index.bin")
            text_map_path = str(Path(config.DATA_DIR) / "faiss_text_map.json")
            index, t_map = load_vector_db(index_path, text_map_path)

            crag_results = apply_crag(
                query=question or "Analyze the uploaded material",
                index=index,
                text_map=t_map,
                extracted_text=extracted_text,
            )

            return {
                "success": True,
                "mode": input_mode,
                "method": extraction_method,
                "metadata": file_details,
                "extracted_text": extracted_text,
                "notes": extraction_notes,
                "response": crag_results.get("final_response", ""),
                "related_topics": related_topics,
                "crag": {
                    "applied": crag_results.get("crag_applied", False),
                    "validation_passed": crag_results.get("validation_passed", True),
                    "confidence_score": crag_results.get("stage_3_validation", {}).get("confidence_score", 0),
                    "validation_issues": crag_results.get("stage_3_validation", {}).get("issues", []),
                    "stages_completed": 4,
                },
            }
        except Exception as exc:
            print(f"CRAG pipeline error: {exc}")

    fallback = generate_multimodal_fallback_response(
        question=question or "Uploaded material analysis",
        input_mode=input_mode,
        extracted_text=combined_context,
        file_metadata=file_details,
        notes=extraction_notes,
        related_topics=related_topics,
    )

    return {
        "success": True,
        "mode": input_mode,
        "method": extraction_method,
        "metadata": file_details,
        "extracted_text": extracted_text,
        "notes": extraction_notes,
        "response": fallback,
        "related_topics": related_topics,
        "fallback": True,
        "crag": {
            "applied": False,
            "validation_passed": False,
            "confidence_score": 0,
            "validation_issues": ["CRAG pipeline unavailable, using fallback response"],
            "stages_completed": 0,
        },
    }
