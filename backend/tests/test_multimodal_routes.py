"""
Unit tests for FastAPI multimodal and search routes.
"""
from __future__ import annotations

import io
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from backend.app import app


@pytest.fixture()
def client(monkeypatch):
    """Provide a FastAPI client with deterministic utility behavior."""
    monkeypatch.setattr("backend.utils.ai_utils.setup_gemini", lambda *args, **kwargs: True)
    monkeypatch.setattr("backend.fastapi_routes.is_gemini_configured", lambda: False)

    monkeypatch.setattr(
        "backend.fastapi_routes.search_and_summarize",
        lambda term: {
            "query": term,
            "normalized_query": term.strip(),
            "search_results": [
                {
                    "rank": 1,
                    "title": f"{term} article",
                    "pageid": 123,
                    "snippet": f"Snippet for {term}",
                    "size": 1000,
                    "wordcount": 250,
                    "timestamp": "2026-05-14T00:00:00",
                    "url": f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}",
                }
            ],
            "top_result": {
                "rank": 1,
                "title": f"{term} article",
                "pageid": 123,
                "snippet": f"Snippet for {term}",
                "size": 1000,
                "wordcount": 250,
                "timestamp": "2026-05-14T00:00:00",
                "url": f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}",
            },
            "title": f"{term} article",
            "extract": f"Detailed extract for {term}",
            "description": f"Description for {term}",
            "thumbnail": "https://example.com/thumb.jpg",
            "url": f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}",
            "timestamp": "2026-05-14T00:00:00",
        },
    )
    monkeypatch.setattr(
        "backend.fastapi_routes.get_related_articles",
        lambda topic, limit=5: [f"{topic} related 1", f"{topic} related 2"],
    )
    monkeypatch.setattr(
        "backend.fastapi_routes.search_multiple_museums",
        lambda query, api_key=None, limit_per_source=5: {
            "query": query,
            "smithsonian": [
                {
                    "rank": 1,
                    "id": "si-1",
                    "title": f"{query} artifact",
                    "type": "artifact",
                    "description": "Artifact description",
                    "summary": "Artifact summary",
                    "date": ["2024"],
                    "culture": ["Test culture"],
                    "images": [{"url": "https://example.com/artifact.jpg", "thumbnail": "https://example.com/thumb.jpg"}],
                    "url": "https://www.si.edu/object/si-1",
                    "source": "Smithsonian",
                    "detail": {
                        "record_id": "si-1",
                        "title": f"{query} artifact",
                        "type": "artifact",
                        "date": ["2024"],
                        "culture": ["Test culture"],
                    },
                }
            ],
            "europeana": [],
            "total_count": 1,
            "search_details": [
                {
                    "source": "Smithsonian",
                    "count": 1,
                    "query": query,
                    "sample_titles": [f"{query} artifact"],
                }
            ],
        },
    )
    monkeypatch.setattr(
        "backend.fastapi_routes.extract_multimodal_content",
        lambda path, filename, input_mode: {
            "text": "Extracted historical content",
            "method": "text-file",
            "notes": ["Plain-text document extracted successfully"],
            "metadata": {
                "filename": filename,
                "extension": ".txt",
                "mode": input_mode,
                "size_bytes": 28,
            },
        },
    )
    monkeypatch.setattr(
        "backend.fastapi_routes.generate_multimodal_fallback_response",
        lambda **kwargs: "Fallback response with detailed context",
    )
    monkeypatch.setattr("backend.fastapi_routes.load_vector_db", lambda *args, **kwargs: (None, None))
    monkeypatch.setattr("backend.fastapi_routes.apply_crag", lambda *args, **kwargs: {"final_response": "CRAG response", "crag_applied": False, "validation_passed": True, "stage_3_validation": {"confidence_score": 1.0, "issues": []}})

    with TestClient(app) as test_client:
        yield test_client


class TestFastAPIMultimodalRoutes:
    def test_analyze_multimodal_text_file(self, client):
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": "What is this document about?", "mode": "document"},
            files={"file": ("test.txt", io.BytesIO(b"This is a historical document."), "text/plain")},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["metadata"]["filename"] == "test.txt"
        assert result["metadata"]["extension"] == ".txt"
        assert result["method"] == "text-file"
        assert result["response"]
        assert result["related_topics"]
        assert result["related_topics"][0]["search_results"]

    def test_analyze_multimodal_no_file_no_question(self, client):
        response = client.post("/api/multimodal/analyze", data={"mode": "document"})

        assert response.status_code == 400
        result = response.json()
        assert result["error"] == "Provide a question, a file upload, or both."
        assert result["message"] == "Provide a question, a file upload, or both."

    def test_analyze_multimodal_with_question_only(self, client):
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": "Tell me about ancient Egypt", "mode": "voice"},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["mode"] == "voice"
        assert result["response"] == "Fallback response with detailed context"

    def test_analyze_multimodal_metadata(self, client):
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": "Test", "mode": "document"},
            files={"file": ("document.txt", io.BytesIO(b"Test document\nWith multiple lines\n"), "text/plain")},
        )

        result = response.json()
        assert result["metadata"]["filename"] == "document.txt"
        assert result["metadata"]["extension"] == ".txt"
        assert result["metadata"]["mode"] == "document"
        assert result["metadata"]["size_bytes"] == 28

    def test_analyze_multimodal_notes(self, client):
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": "Test", "mode": "document"},
            files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        )

        result = response.json()
        assert isinstance(result["notes"], list)
        assert result["notes"]

    def test_analyze_multimodal_related_topics(self, client):
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": "ancient rome", "mode": "voice"},
        )

        result = response.json()
        assert "related_topics" in result
        assert isinstance(result["related_topics"], list)
        assert result["related_topics"][0]["query"] == "ancient rome"
        assert result["related_topics"][0]["search_results"]

    def test_search_quick_facts_returns_detailed_metadata(self, client):
        response = client.get("/api/quick-facts/Rome")

        assert response.status_code == 200
        result = response.json()
        assert result["query"] == "Rome"
        assert result["summary"] == "Detailed extract for Rome"
        assert result["search_results"]
        assert result["top_result"]["title"] == "Rome article"

    def test_related_topics_route_returns_details(self, client):
        response = client.get("/api/related/Julius_Caesar")

        assert response.status_code == 200
        result = response.json()
        assert result["topic"] == "Julius_Caesar"
        assert result["count"] == 2
        assert result["related_topics_detail"]
        assert result["related_topics_detail"][0]["search_results"]

    def test_search_museums_returns_detailed_payload(self, client):
        response = client.post(
            "/api/museum/search",
            json={"query": "ancient rome", "limit": 5},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["query"] == "ancient rome"
        assert result["total_count"] == 1
        assert result["results"]["search_details"]
        assert result["results"]["smithsonian"][0]["detail"]["record_id"] == "si-1"


class TestFastAPIMultimodalErrorScenarios:
    def test_analyze_multimodal_invalid_mode(self, client):
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": "Test", "mode": "invalid_mode"},
            files={"file": ("test.txt", io.BytesIO(b"Content"), "text/plain")},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_analyze_multimodal_malformed_request(self, client):
        response = client.post("/api/multimodal/analyze", data="invalid", headers={"Content-Type": "text/plain"})
        assert response.status_code in [400, 415]

    def test_analyze_multimodal_large_question(self, client):
        large_question = "x" * 10000
        response = client.post(
            "/api/multimodal/analyze",
            data={"question": large_question, "mode": "voice"},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
