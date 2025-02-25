from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from app.database.models import (
    InfringementRequest,
    InfringementAnalysis,
    SingleProductRequest,
    InfringingProduct
)
from app.services.analyzer_service import AnalyzerService, AnalyzerError
from app.services.data_service import DataService
from app.services.fuzzy_matcher import FuzzyMatcher
from typing import List
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Initialize services
data_service = DataService()
analyzer_service = AnalyzerService()
matcher = FuzzyMatcher(data_service)

@router.post("/company", response_model=InfringementAnalysis)
def analyze_patent_infringement(
    request: InfringementRequest = Body(
        example={
            "patent_id": "US-RE49889-E1",
            "company_name": "Walmart Inc."
        }
    )
):
    """
    Analyze potential patent infringement for a company's products.
    Returns top 2 potentially infringing products with detailed analysis.
    """
    try:
        patent = data_service.get_patent(request.patent_id)
        if not patent:
            return JSONResponse(
                status_code=404,
                content={"error": f"Patent with ID {request.patent_id} not found"}
            )
            
        company = data_service.get_company(request.company_name)
        if not company:
            return JSONResponse(
                status_code=404,
                content={"error": f"Company {request.company_name} not found"}
            )
            
        result = analyzer_service.analyze_multiple_products(patent, company["products"])
        
        if "error" in result:
            return JSONResponse(
                status_code=result["status_code"],
                content={"error": result["error"]}
            )
            
        return JSONResponse(
            status_code=200,
            content={
                "analysis_id": str(uuid.uuid4()),
                "patent_id": request.patent_id,
                "company_name": request.company_name,
                "analysis_date": datetime.now().isoformat(),
                "top_infringing_products": result["data"],
                "overall_risk_assessment": "High risk" if any(
                    p["infringement_likelihood"] == "High" 
                    for p in result["data"]
                ) else "Moderate risk"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"}
        )

@router.post("/product", response_model=InfringingProduct)
def analyze_product_infringement(
    request: SingleProductRequest = Body(
        example={
            "patent_id": "US-RE49889-E1",
            "product": {
                "name": "Walmart Shopping App",
                "description": "Mobile application with integrated shopping list and advertisement features"
            }
        }
    )
):
    """
    Analyze potential patent infringement for a single product.
    Returns detailed analysis of infringement likelihood.
    """
    try:
        patent = data_service.get_patent(request.patent_id)
        if not patent:
            return JSONResponse(
                status_code=404,
                content={"error": f"Patent with ID {request.patent_id} not found"}
            )
            
        result = analyzer_service.analyze_single_product(patent, request.product)
        
        if "error" in result:
            return JSONResponse(
                status_code=result["status_code"],
                content={"error": result["error"]}
            )
            
        if not result["data"]:
            return JSONResponse(
                status_code=500,
                content={"error": "Analysis failed to produce results"}
            )
            
        return JSONResponse(
            status_code=200,
            content=result["data"]  # Return the analysis result directly
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"}
        )