from fastapi import APIRouter, HTTPException, Query
from typing import List
from uuid import uuid4, UUID
from datetime import datetime
from app.database.models import SavedReport
from app.services.report_service import ReportService
from app.services.data_service import DataService

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Initialize services
report_service = ReportService()
data_service = DataService()

@router.post("/", response_model=SavedReport)
async def save_report(analysis_result: dict):
    """Save analysis result as a report"""
    # Get full patent info
    patent = data_service.get_patent(analysis_result["patent_id"])
    # print(patent["publication_number"])
    # print(patent["title"])
    # print(patent["abstract"])
    # company = data_service.get_company(analysis_result["company_name"])
    
    report = {
        "id": analysis_result["id"],
        "created_at": analysis_result["created_at"],
        "patent_id": patent["publication_number"],
        "patent_title": patent["title"],
        "patent_abstract": patent["abstract"],
        "company_name": analysis_result["company_name"],
        "top_infringing_products": [
            {
                "product_name": p["product_name"],
                "infringement_score": p["infringement_score"],
                "infringement_likelihood": p["infringement_likelihood"],
                "relevant_claims": p["relevant_claims"],
                "explanation": p["explanation"],
                "specific_features": p["specific_features"]
            }
            for p in analysis_result["top_infringing_products"]
        ],
        "overall_risk_assessment": analysis_result["overall_risk_assessment"]
    }
    
    return await report_service.save_report(report)

@router.get("/", response_model=List[SavedReport])
async def list_reports(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=50)
):
    """Get list of saved reports"""
    return await report_service.list_reports(skip, limit)

@router.get("/{report_id}", response_model=SavedReport)
async def get_report(report_id: UUID):
    """Get specific report by ID"""
    report = await report_service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report 