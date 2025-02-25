from app.database.database import JsonDatabase
from app.database.models import SavedReport

class ReportService:
    def __init__(self):
        self.db = JsonDatabase()
    
    async def save_report(self, report_data: dict) -> SavedReport:
        report = await self.db.save_report(report_data)
        return SavedReport(**report)
    
    async def get_report(self, report_id: str) -> SavedReport:
        report = await self.db.get_report(report_id)
        if report:
            return SavedReport(**report)
        return None
    
    async def list_reports(self, skip: int = 0, limit: int = 10) -> list:
        reports = await self.db.list_reports(skip, limit)
        return [SavedReport(**report) for report in reports] 