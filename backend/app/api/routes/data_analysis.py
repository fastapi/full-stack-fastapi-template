from fastapi import APIRouter, Query
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import csv

router = APIRouter(prefix="/analysis", tags=["analysis"])

def parse_utc_timestamp(utc_str: str) -> datetime:
    """解析UTC时间戳格式：YYYYMMDDHHMMSS"""
    return datetime.strptime(utc_str, "%Y%m%d%H%M%S")

def get_time_range_data(start_utc: str, minutes: int = 15) -> list:
    """获取指定时间戳后minutes分钟内的数据"""
    csv_path = Path("/app/data/csv/pair_converted_jn0912.csv")
    if not csv_path.exists():
        return []
    
    start_time = parse_utc_timestamp(start_utc)
    end_time = start_time + timedelta(minutes=minutes)
    
    results = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            utc = row.get("ONUTC", "")
            if utc:
                try:
                    row_time = parse_utc_timestamp(utc)
                    if start_time <= row_time <= end_time:
                        # 提取经纬度
                        lat = row.get("ONLAT")
                        lng = row.get("ONLON")
                        if lat and lng:
                            try:
                                lat_float = float(lat)
                                lng_float = float(lng)
                                results.append({
                                    "lat": lat_float,
                                    "lng": lng_float,
                                    "utc": utc
                                })
                            except ValueError:
                                continue
                except ValueError:
                    continue
    
    return results

@router.get("/dbscan-clustering")
def dbscan_clustering(
    start_utc: str = Query(..., description="起始时间戳，如20130912011417"),
    eps: float = Query(0.01, description="DBSCAN的eps参数，控制聚类半径"),
    min_samples: int = Query(3, description="DBSCAN的min_samples参数，最小样本数")
):
    """
    使用DBSCAN算法对上车点进行聚类分析，提取热门上客点
    
    参数:
    - start_utc: 起始时间戳
    - eps: 聚类半径（度）
    - min_samples: 最小样本数
    
    返回:
    - hot_spots: 热门上客点列表，每个点包含经纬度和count值
    """
    try:
        # 获取时间范围内的数据
        data = get_time_range_data(start_utc, 15)
        
        if not data:
            return JSONResponse(
                status_code=404, 
                content={"error": f"在时间戳 {start_utc} 后15分钟内没有找到数据"}
            )
        
        # 转换为numpy数组
        coordinates = np.array([[point["lat"], point["lng"]] for point in data])
        
        if len(coordinates) < min_samples:
            return JSONResponse(
                status_code=400,
                content={"error": f"数据点数量({len(coordinates)})少于最小样本数({min_samples})"}
            )
        
        # 标准化数据（可选，取决于你的数据范围）
        scaler = StandardScaler()
        coordinates_scaled = scaler.fit_transform(coordinates)
        
        # 执行DBSCAN聚类
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(coordinates_scaled)
        
        # 分析聚类结果，提取热门上客点
        unique_labels = set(cluster_labels)
        hot_spots = []
        
        for label in unique_labels:
            if label == -1:  # 噪声点，跳过
                continue
                
            # 获取该聚类的所有点
            cluster_points = coordinates[cluster_labels == label]
            
            # 计算聚类中心（均值）
            center_lat = np.mean(cluster_points[:, 0])
            center_lng = np.mean(cluster_points[:, 1])
            
            # 统计该聚类的样本数量作为count值
            count = len(cluster_points)
            
            # 只保留样本数量达到最小要求的聚类
            if count >= min_samples:
                hot_spots.append({
                    "lng": float(center_lng),
                    "lat": float(center_lat),
                    "count": count
                })
        
        # 按count值降序排序，最热门的排在前面
        hot_spots.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "start_utc": start_utc,
            "total_points": len(data),
            "hot_spots_found": len(hot_spots),
            "noise_points": int(np.sum(cluster_labels == -1)),
            "parameters": {
                "eps": eps,
                "min_samples": min_samples
            },
            "hot_spots": hot_spots  # 热门上客点列表
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"聚类分析失败: {str(e)}"}
        )

@router.get("/test-data")
def test_data_analysis():
    """测试接口，返回一些示例数据用于调试"""
    test_utc = "20130912011417"
    data = get_time_range_data(test_utc, 15)
    
    return {
        "test_utc": test_utc,
        "data_points_found": len(data),
        "sample_data": data[:5] if data else []
    } 