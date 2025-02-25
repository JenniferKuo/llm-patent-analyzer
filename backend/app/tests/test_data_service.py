import pytest
from app.services.data_service import DataService
from unittest.mock import mock_open, patch
import json

# Mock data for testing
MOCK_PATENTS = [
    {"publication_number": "US123", "title": "Test Patent 1"},
    {"publication_number": "US456", "title": "Test Patent 2"}
]

MOCK_COMPANIES = [
    {"name": "Company A", "products": ["Product 1"]},
    {"name": "Company B", "products": ["Product 2"]}
]

@pytest.fixture
def data_service():
    """Fixture to create a DataService instance"""
    with patch("builtins.open", mock_open()):
        with patch("json.load") as mock_json_load:
            mock_json_load.side_effect = [MOCK_PATENTS, MOCK_COMPANIES]
            service = DataService()
            return service

def test_get_patent(data_service):
    """Test get_patent method"""
    patent = data_service.get_patent("US123")
    assert patent is not None
    assert patent["publication_number"] == "US123"
    
    patent = data_service.get_patent("NONEXISTENT")
    assert patent is None

def test_get_company(data_service):
    """Test get_company method"""
    company = data_service.get_company("Company A")
    assert company is not None
    assert company["name"] == "Company A"
    
    company = data_service.get_company("Nonexistent Company")
    assert company is None

def test_get_patents(data_service):
    """Test get_patents method"""
    patents = data_service.get_patents()
    assert len(patents) == 2
    assert patents == MOCK_PATENTS

def test_get_companies(data_service):
    """Test get_companies method"""
    companies = data_service.get_companies()
    assert len(companies) == 2
    assert companies == MOCK_COMPANIES 