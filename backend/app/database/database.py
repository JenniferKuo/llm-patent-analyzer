import os
import json
from datetime import datetime
from uuid import UUID
from pathlib import Path
from typing import List, Dict, Optional

class JsonDatabase:
    _instance = None
    data_dir: Path
    reports_file: Path
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize basic properties
            cls._instance.data_dir = Path(__file__).parent.parent / "data"
            cls._instance.reports_file = cls._instance.data_dir / "reports.json"
            cls._instance._init_storage()
        return cls._instance
    
    def __init__(self):
        """Do not initialize here, __new__ handles it"""
        pass
    
    def _init_storage(self):
        """Initialize storage file if not exists"""
        self.data_dir.mkdir(exist_ok=True)
        if not self.reports_file.exists():
            with open(self.reports_file, 'w') as f:
                json.dump([], f)
    
    async def save_report(self, report_data: dict) -> dict:
        """Save a report to JSON file"""
        if isinstance(report_data.get('id'), UUID):
            report_data['id'] = str(report_data['id'])
        
        if isinstance(report_data.get('created_at'), datetime):
            report_data['created_at'] = report_data['created_at'].isoformat()
        
        report = {
            "id": report_data['id'],
            "created_at": datetime.now().isoformat(),
            **report_data
        }
        
        reports = self._read_reports()
        reports.append(report)
        self._write_reports(reports)
        return report
    
    async def get_report(self, report_id: str) -> Optional[dict]:
        """Get a specific report by ID"""
        reports = self._read_reports()
        # Make sure report_id is a string
        report_id_str = str(report_id)
        return next((r for r in reports if str(r['id']) == report_id_str), None)
    
    async def list_reports(self, skip: int = 0, limit: int = 10) -> List[dict]:
        """List reports with pagination"""
        reports = self._read_reports()
        return reports[skip:skip + limit]
    
    def _read_reports(self) -> List[dict]:
        """Read all reports from file"""
        try:
            if not self.reports_file.exists():
                return []
            with open(self.reports_file, 'r') as f:
                content = f.read()
                return json.loads(content) if content else []
        except Exception as e:
            print(f"Error reading reports: {str(e)}")
            return []
    
    def _write_reports(self, reports: List[dict]):
        """Write reports to file"""
        try:
            with open(self.reports_file, 'w') as f:
                json.dump(reports, f, indent=2)
        except Exception as e:
            print(f"Error writing reports: {str(e)}") 
            
