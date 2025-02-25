import pytest
from app.services.analyzer_service import AnalyzerService
from unittest.mock import patch, Mock
import json

# Mock data for testing
MOCK_PATENT = {
    "publication_number": "US123",
    "title": "Test Patent",
    "abstract": "Test Abstract",
    "claims": json.dumps([
        {"num": 1, "text": "Test claim 1"},
        {"num": 2, "text": "Test claim 2"}
    ])
}

MOCK_PRODUCTS = [
    {"name": "Product 1", "description": "Test product 1"},
    {"name": "Product 2", "description": "Test product 2"}
]

@pytest.fixture
def analyzer_service():
    """Fixture to create an AnalyzerService instance"""
    return AnalyzerService()

def test_analyze_multiple_products(analyzer_service):
    """Test analyze_multiple_products method"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": json.dumps({
            "products": [
                {
                    "product_name": "Product 1",
                    "infringement_score": 85,
                    "infringement_likelihood": "High",
                    "relevant_claims": ["1"],
                    "explanation": "Test",
                    "specific_features": ["feature1"]
                },
                {
                    "product_name": "Product 2",
                    "infringement_score": 45,
                    "infringement_likelihood": "Moderate",
                    "relevant_claims": ["2"],
                    "explanation": "Test",
                    "specific_features": ["feature2"]
                }
            ]
        })
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.post', return_value=mock_response):
        result = analyzer_service.analyze_multiple_products(MOCK_PATENT, MOCK_PRODUCTS)
        
        assert result["status_code"] == 200
        assert len(result["data"]) == 2
        assert result["data"][0]["infringement_score"] == 85
        assert result["data"][1]["infringement_score"] == 45

def test_analyze_single_product(analyzer_service):
    """Test analyze_single_product method"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": json.dumps({
            "product_name": "Product 1",
            "infringement_score": 85,
            "infringement_likelihood": "High",
            "relevant_claims": ["1"],
            "explanation": "Test",
            "specific_features": ["feature1"]
        })
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.post', return_value=mock_response):
        result = analyzer_service.analyze_single_product(MOCK_PATENT, MOCK_PRODUCTS[0])
        
        assert result["status_code"] == 200
        assert result["data"]["infringement_score"] == 85
        assert result["data"]["infringement_likelihood"] == "High"

def test_analyze_single_product_error(analyzer_service):
    """Test analyze_single_product method with error"""
    with patch('requests.post', side_effect=Exception("Test error")):
        result = analyzer_service.analyze_single_product(MOCK_PATENT, MOCK_PRODUCTS[0])
        
        assert result["status_code"] == 500
        assert "error" in result 