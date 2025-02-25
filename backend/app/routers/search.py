from fastapi import APIRouter, Query
from app.services.fuzzy_matcher import FuzzyMatcher
from app.database.models import SearchResponse, SearchMatch
from app.services.data_service import DataService
from typing import List, Dict

router = APIRouter(prefix="/api/search", tags=["search"])
# Initialize services
data_service = DataService()
matcher = FuzzyMatcher(data_service)

@router.get("/patent/{query}")
async def search_patent(
    query: str,
    threshold: int = Query(default=80, ge=0, le=100)
) -> SearchResponse:
    """Search for patents by ID using fuzzy matching"""
    matches = matcher.find_patent(query, threshold)
    
    return SearchResponse(
        query=query,
        matches=[
            SearchMatch(
                confidence=m["confidence"],
                is_exact=m["is_exact"],
                data=m["patent"]
            )
            for m in matches
        ],
        suggestion=matches[0]["patent"]["publication_number"] if matches else None
    )

@router.get("/company/{query}")
async def search_company(
    query: str,
    threshold: int = Query(default=60, ge=0, le=100)
) -> SearchResponse:
    """Search for companies using fuzzy matching"""
    matches = matcher.find_company(query, threshold)
    
    return SearchResponse(
        query=query,
        matches=[
            SearchMatch(
                confidence=m["confidence"],
                is_exact=m["is_exact"],
                data=m["company"]
            )
            for m in matches
        ],
        suggestion=matches[0]["company"]["name"] if matches else None
    )

@router.get("/patent/suggest/{query}")
async def suggest_patents(
    query: str,
    limit: int = Query(default=5, ge=1, le=20),
    threshold: int = Query(default=60, ge=0, le=100)
) -> List[Dict]:
    """
    Suggest patents based on partial title input.
    Returns a list of potential matches with their confidence scores.
    """
    matches = matcher.find_patent_by_title(query, threshold)
    return [
        {
            "id": m["patent"]["publication_number"],
            "title": m["patent"]["title"],
            "confidence": m["confidence"],
            # "abstract": m["patent"].get("abstract", "")
        }
        for m in matches[:limit]
    ]

@router.get("/company/suggest/{query}")
async def suggest_companies(
    query: str,
    limit: int = Query(default=5, ge=1, le=20),
    threshold: int = Query(default=60, ge=0, le=100)
) -> List[Dict]:
    """
    Suggest companies based on partial input.
    Returns a list of potential matches with their confidence scores.
    """
    matches = matcher.find_company(query, threshold)
    return [
        {
            "name": m["company"]["name"],
            "confidence": m["confidence"]
        }
        for m in matches[:limit]
    ]

@router.get("/patent/title/{query}")
async def search_patent_by_title(
    query: str,
    limit: int = Query(default=5, ge=1, le=20),
    threshold: int = Query(default=60, ge=0, le=100)
) -> List[Dict]:
    """
    Search patents by title.
    Returns a list of potential matches with their confidence scores.
    """
    matches = matcher.find_patent_by_title(query, threshold)
    return [
        {
            "id": m["patent"]["publication_number"],
            "title": m["patent"]["title"],
            "confidence": m["confidence"],
            "abstract": m["patent"].get("abstract", "")
        }
        for m in matches[:limit]
    ] 