from typing import List, Dict, Tuple
from rapidfuzz import fuzz, process
import json
from pathlib import Path
from app.services.data_service import DataService

class FuzzyMatcher:
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        self.patents = self.data_service.get_patents()
        self.companies = self.data_service.get_companies()

    def find_patent(self, query: str, threshold: int = 80) -> List[Dict]:
        """Find patents matching the query"""
        # Normalize query
        query = query.upper().replace(" ", "")
        
        matches = []
        for patent in self.patents:
            patent_id = patent["publication_number"]
            
            # Exact match
            if query == patent_id:
                matches.append((patent, 100))
                continue
                
            # Partial match
            if query in patent_id:
                matches.append((patent, 90))
                continue
                
            # Fuzzy match
            ratio = fuzz.ratio(query, patent_id)
            if ratio >= threshold:
                matches.append((patent, ratio))
        
        # Sort and return results
        return [
            {
                "patent": patent,
                "confidence": score,
                "is_exact": score == 100
            }
            for patent, score in sorted(matches, key=lambda x: x[1], reverse=True)
        ]

    def find_company(self, query: str, threshold: int = 80) -> List[Dict]:
        """Find companies matching the query"""
        # Check if companies is a dictionary and has a "companies" key
        if isinstance(self.companies, dict) and "companies" in self.companies:
            companies = self.companies["companies"]
        else:
            companies = self.companies
        
        company_names = [company["name"] for company in companies]
        
        # Make comparison case insensitive
        matches = process.extract(
            query.lower(),  # Convert query to lowercase
            [name.lower() for name in company_names],  # Convert company names to lowercase
            scorer=fuzz.WRatio,
            limit=5
        )
        
        results = []
        for match in matches:
            name, score = match[0], match[1]
            if score >= threshold:
                # Find company using original name (preserving case)
                company = next(c for c in companies if c["name"].lower() == name)
                results.append({
                    "company": company,
                    "confidence": score,
                    "is_exact": score == 100
                })
                
        return results

    def find_patent_by_title(self, query: str, threshold: int = 80) -> List[Dict]:
        """
        Find patents by matching title using token_ratio for balanced matching
        that handles both partial and complete matches
        """
        patent_titles = [(p["title"].lower(), p) for p in self.patents]
        
        # Use process.extract with token_ratio
        matches = process.extract(
            query.lower(),
            [title for title, _ in patent_titles],
            scorer=fuzz.token_ratio,  # Better balance between partial and complete matching
            limit=10
        )
        
        results = []
        for match in matches:
            title, score = match[0], match[1]
            if score >= threshold:
                patent = next(p for t, p in patent_titles if t == title)
                results.append({
                    "patent": patent,
                    "confidence": score,
                    "is_exact": score == 100
                })
        
        return sorted(results, key=lambda x: x["confidence"], reverse=True)