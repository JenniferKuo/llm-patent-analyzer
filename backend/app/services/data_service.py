from typing import List, Dict, Optional
import json
from pathlib import Path
import os

class DataService:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self._load_data()
        
    def _load_data(self):
        """Load all data files"""
        try:
            with open(self.data_dir / "patents.json") as f:
                self.patents = json.load(f)
            with open(self.data_dir / "company_products.json") as f:
                self.companies = json.load(f)
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.patents = []
            self.companies = []
            
    def get_patents(self) -> List[Dict]:
        """Get all patents"""
        return self.patents
            
    def get_companies(self) -> List[Dict]:
        """Get all companies"""
        return self.companies
        
    def get_patent(self, patent_id: str) -> Optional[Dict]:
        """Get patent by ID"""
        try:
            return next(
                (p for p in self.patents if p["publication_number"] == patent_id),
                None
            )
        except Exception as e:
            print(f"Error finding patent: {str(e)}")
            return None
            
    def get_company(self, company_name: str) -> Optional[Dict]:
        """Get company and its products"""
        try:
            # Check if data is in correct format
            if not isinstance(self.companies, dict) or 'companies' not in self.companies:
                print("Warning: Invalid companies data format")
                return None
            
            # Get the companies array
            companies_list = self.companies['companies']
            
            company = next(
                (c for c in companies_list if c["name"].lower() == company_name.lower()),
                None
            )
            
            return company
            
        except Exception as e:
            print(f"Error finding company: {str(e)}")
            return None