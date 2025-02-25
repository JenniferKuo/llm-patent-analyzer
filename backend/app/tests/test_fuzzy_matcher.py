import pytest
from app.services.fuzzy_matcher import FuzzyMatcher
from app.services.data_service import DataService
from unittest.mock import Mock

@pytest.fixture
def mock_data_service():
    """Create mock data service"""
    service = Mock(spec=DataService)
    service.get_patents.return_value = [
        {
            "publication_number": "US-12345-A1",
            "title": "Test Patent 1",
            "abstract": "First test patent"
        },
        {
            "publication_number": "US-67890-B2",
            "title": "Test Patent 2",
            "abstract": "Second test patent"
        },
        {
            "publication_number": "EP-11111-A1",
            "title": "Different Patent",
            "abstract": "Another patent"
        }
    ]
    
    service.get_companies.return_value = [
        {
            "name": "Apple Inc.",
            "products": []
        },
        {
            "name": "Microsoft Corporation",
            "products": []
        },
        {
            "name": "Amazon.com, Inc.",
            "products": []
        }
    ]
    return service

@pytest.fixture
def matcher(mock_data_service):
    """Create FuzzyMatcher instance with mock data service"""
    return FuzzyMatcher(mock_data_service)

class TestFuzzyMatcher:
    def test_exact_patent_match(self, matcher):
        """Test exact patent number match"""
        results = matcher.find_patent("US-12345-A1")
        assert len(results) == 1
        assert results[0]["confidence"] == 100
        assert results[0]["is_exact"] == True
        assert results[0]["patent"]["publication_number"] == "US-12345-A1"

    def test_partial_patent_match(self, matcher):
        """Test partial patent number match"""
        results = matcher.find_patent("12345")
        assert len(results) >= 1
        assert results[0]["confidence"] >= 90
        assert results[0]["patent"]["publication_number"] == "US-12345-A1"

    def test_fuzzy_patent_match(self, matcher):
        """Test fuzzy patent number match"""
        results = matcher.find_patent("US-12344-A1")  # One character different
        assert len(results) >= 1
        assert 80 <= results[0]["confidence"] < 100
        assert results[0]["patent"]["publication_number"] == "US-12345-A1"

    def test_no_patent_match(self, matcher):
        """Test no matching patents found"""
        results = matcher.find_patent("NONEXISTENT")
        assert len(results) == 0

    def test_exact_company_match(self, matcher):
        """Test exact company name match"""
        results = matcher.find_company("Apple Inc.")
        assert len(results) >= 1
        assert results[0]["confidence"] == 100
        assert results[0]["is_exact"] == True
        assert results[0]["company"]["name"] == "Apple Inc."

    def test_fuzzy_company_match(self, matcher):
        """Test fuzzy company name match"""
        results = matcher.find_company("Microsoft Corp")  # Abbreviated name
        assert len(results) >= 1
        assert results[0]["confidence"] >= 80
        assert results[0]["company"]["name"] == "Microsoft Corporation"

    def test_threshold_filter(self, matcher):
        """Test threshold filtering"""
        results = matcher.find_patent("US-99999-A1", threshold=95)
        assert all(r["confidence"] >= 95 for r in results)

    def test_case_insensitive_match(self, matcher):
        """Test case insensitive matching"""
        results = matcher.find_company("apple inc")
        assert len(results) >= 1
        assert results[0]["company"]["name"] == "Apple Inc."

    def test_whitespace_handling(self, matcher):
        """Test whitespace handling"""
        results = matcher.find_patent("US 12345 A1")
        assert len(results) >= 1
        assert results[0]["patent"]["publication_number"] == "US-12345-A1"

    def test_find_patent_by_title(self, matcher):
        """Test finding patents by title"""
        # Exact title match
        results = matcher.find_patent_by_title("Test Patent 1")
        assert len(results) >= 1
        assert results[0]["confidence"] == 100
        assert results[0]["is_exact"] == True
        assert results[0]["patent"]["title"] == "Test Patent 1"

    def test_fuzzy_title_match(self, matcher):
        """Test fuzzy title matching"""
        # Partial title match with lower threshold
        results = matcher.find_patent_by_title("Test Pat", threshold=60)
        assert len(results) >= 1
        assert results[0]["confidence"] >= 60
        assert "Test Patent" in results[0]["patent"]["title"]

    def test_title_threshold_filtering(self, matcher):
        """Test threshold filtering for title search"""
        # Should not match with high threshold
        results = matcher.find_patent_by_title("Completely Different", threshold=90)
        assert len(results) == 0

    def test_multiple_title_matches(self, matcher):
        """Test multiple title matches are returned and sorted"""
        results = matcher.find_patent_by_title("Test")
        assert len(results) > 1
        # Verify results are sorted by confidence
        confidences = [r["confidence"] for r in results]
        assert confidences == sorted(confidences, reverse=True) 