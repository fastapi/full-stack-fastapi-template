"""
Serves generated diff/impact reports to the frontend.
Mount path: backend/app/routes/reports.py
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/reports", tags=["reports"])
REPORTS_DIR = Path("contractguard/reports")


@router.get("/")
def list_reports():
    """Summary list for the report viewer's landing page."""
    reports = []
    for file in sorted(REPORTS_DIR.glob("impact_report_*.json")):
        data = json.loads(file.read_text())
        reports.append({
            "change_id": data.get("change_id"),
            "severity": data.get("severity"),
            "verify_status": data.get("verify_status"),
        })
    return reports


@router.get("/{change_id}")
def get_report(change_id: str):
    """Full detail for one scenario, e.g. GET /api/reports/field_renamed"""
    file = REPORTS_DIR / f"impact_report_{change_id}.json"
    if not file.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return json.loads(file.read_text())
