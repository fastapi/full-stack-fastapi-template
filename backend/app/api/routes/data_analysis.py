from fastapi import APIRouter, Query, UploadFile, File
import csv
from pathlib import Path
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/data_analysis", tags=["data_analysis"])

@router.get("/get-data")
def read_csv_data(
    start_utc: str = Query(..., description="起始时间戳，如20130912011417"),
    end_utc: str = Query(..., description="结束时间戳，如20130912042835")
):
    # 使用绝对路径，确保在Docker容器内能正确找到文件
    csv_path = Path("/app/data/csv/pair_converted_jn0912.csv")
    if not csv_path.exists():
        return JSONResponse(status_code=404, content={"error": f"CSV文件未找到: {csv_path}"})
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

@router.get("/count")
def count_csv_rows():
    # 使用绝对路径，确保在Docker容器内能正确找到文件
    csv_path = Path("/app/data/csv/pair_converted_jn0912.csv")
    if not csv_path.exists():
        return JSONResponse(status_code=404, content={"error": f"CSV文件未找到: {csv_path}"})
    
    try:
        with open(csv_path, encoding="utf-8") as f:
            # 使用csv.reader来准确计算行数（包括标题行）
            reader = csv.reader(f)
            row_count = sum(1 for row in reader)
            return {"total_rows": row_count}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"读取文件失败: {str(e)}"})

# @router.post("/upload-csv")
# def upload_csv(file: UploadFile = File(...)):
#     if not file.filename.endswith('.csv'):
#         return JSONResponse(status_code=400, content={"error": "请上传csv文件"})
#     save_path = Path("data/csv") / file.filename
#     with open(save_path, "wb") as f:
#         f.write(file.file.read())
#     return {"message": f"文件已保存到 {save_path}"} 