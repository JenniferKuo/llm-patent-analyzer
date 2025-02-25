from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID

class Claim(BaseModel):
    """Patent claim model"""
    num: str
    text: str

class Inventor(BaseModel):
    """Patent inventor model"""
    first_name: str
    last_name: str

class Patent(BaseModel):
    """Patent information model"""
    id: int
    publication_number: str
    title: str
    abstract: Optional[str] = None
    claims: List[Claim]
    assignee: Optional[str] = None
    inventors: List[Inventor]
    priority_date: Optional[datetime] = None
    grant_date: Optional[datetime] = None
    description: Optional[str] = None

class Product(BaseModel):
    """Product information model"""
    name: str
    description: str

class SingleProductRequest(BaseModel):
    """Request model for single product analysis"""
    patent_id: str
    product: Dict

class InfringingProduct(BaseModel):
    """Model for product infringement analysis results"""
    product_name: str
    infringement_likelihood: str
    infringement_score: int
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]

class InfringementRequest(BaseModel):
    """
    Request model for analyzing all products of a company.
    
    Attributes:
        patent_id: Identifier of the patent to analyze against
        company_name: Name of the company whose products will be analyzed
    """
    patent_id: str
    company_name: str

class InfringementAnalysis(BaseModel):
    """
    Complete analysis result for a company's products.
    
    Attributes:
        analysis_id: Unique identifier for this analysis
        patent_id: Identifier of the analyzed patent
        company_name: Name of the analyzed company
        analysis_date: Timestamp of the analysis
        top_infringing_products: List of most likely infringing products
        overall_risk_assessment: Overall risk level assessment
    """
    analysis_id: str
    patent_id: str
    company_name: str
    analysis_date: datetime
    top_infringing_products: List[Dict]  # List[InfringingProduct]
    overall_risk_assessment: str
    
class SearchMatch(BaseModel):
    """Single search result"""
    confidence: float
    is_exact: bool
    data: Dict

class SearchResponse(BaseModel):
    """Search response"""
    query: str
    matches: List[SearchMatch]
    suggestion: Optional[str] = None

class SavedProduct(BaseModel):
    """Product in analysis result"""
    product_name: str
    infringement_score: int
    infringement_likelihood: str
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]

class SavedReport(BaseModel):
    """Saved analysis report"""
    id: UUID
    created_at: datetime
    patent_id: str
    patent_title: str
    patent_abstract: str
    company_name: str
    top_infringing_products: List[SavedProduct]
    overall_risk_assessment: str