from fastapi import APIRouter, Query, UploadFile, File
import csv
from pathlib import Path
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/csv", tags=["csv"])

@router.get("/get-data")
def read_csv_data(
    start_utc: str = Query(..., description="起始时间戳，如20130912011417"),
    end_utc: str = Query(..., description="结束时间戳，如20130912042835")
):
    csv_path = Path("data/csv/pair_converted_jn0912.csv")
    if not csv_path.exists():
        return JSONResponse(status_code=404, content={"error": "CSV文件未找到"})
    results = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            utc = row.get("ONUTC", "")
            if start_utc <= utc <= end_utc:
                results.append(row)
                if len(results) >= 5:
                    break
    return results

@router.post("/upload-csv")
def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return JSONResponse(status_code=400, content={"error": "请上传csv文件"})
    save_path = Path("data/csv") / file.filename
    with open(save_path, "wb") as f:
        f.write(file.file.read())
    return {"message": f"文件已保存到 {save_path}"} 