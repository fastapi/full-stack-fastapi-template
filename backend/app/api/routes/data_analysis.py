from fastapi import APIRouter, Query
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import csv
from typing import Literal
from sqlmodel import Session, select
from app.core.db import engine
from app.models import GPSRecord
import math
from typing import List, Tuple, Optional
from fastapi.responses import FileResponse

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

@router.get("/passenger-count-distribution")
def passenger_count_distribution(
    interval: Literal["15min", "1h"] = Query("15min", description="统计间隔，可选15min或1h")
):
    """
    统计全量数据，按15分钟或1小时为间隔，统计每个时间段的乘客数量分布
    """
    csv_path = Path("/app/data/csv/pair_converted_jn0912.csv")
    if not csv_path.exists():
        return JSONResponse(status_code=404, content={"error": "数据文件不存在"})
    # 设定时间间隔
    delta = timedelta(minutes=15) if interval == "15min" else timedelta(hours=1)
    # 读取所有UTC时间
    time_counts = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            utc = row.get("ONUTC", "")
            if not utc:
                continue
            try:
                dt = parse_utc_timestamp(utc)
                # 计算该时间属于哪个区间
                if interval == "15min":
                    bucket = dt.replace(minute=(dt.minute // 15) * 15, second=0)
                else:
                    bucket = dt.replace(minute=0, second=0)
                key = bucket.strftime("%Y%m%d%H%M%S")
                time_counts[key] = time_counts.get(key, 0) + 1
            except Exception:
                continue
    # 排序输出
    result = []
    for k in sorted(time_counts.keys()):
        start_dt = parse_utc_timestamp(k)
        end_dt = start_dt + delta
        result.append({
            "interval_start": k,
            "interval_end": end_dt.strftime("%Y%m%d%H%M%S"),
            "count": time_counts[k]
        })
    return result 

@router.post("/import-gps-data")
def import_gps_data():
    """
    从CSV文件导入GPS数据到GPSRecord表
    """
    filepath = "/app/data/csv/converted_jn0912.csv"
    batch_size = 1000
    total = 0
    max_rows = 3000  # 限制导入前3000条
    try:
        with Session(engine) as session:
            with open(filepath, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                batch = []
                for row in reader:
                    if total >= max_rows:
                        break
                    record = GPSRecord(
                        commaddr=row["COMMADDR"],
                        utc=row["UTC"],
                        lat=float(row["LAT"]),
                        lon=float(row["LON"]),
                        head=float(row["HEAD"]),
                        speed=float(row["SPEED"]),
                        tflag=int(row["TFLAG"]),
                    )
                    batch.append(record)
                    if len(batch) >= batch_size:
                        session.add_all(batch)
                        session.commit()
                        total += len(batch)
                        batch.clear()
                # 导入最后一批
                if batch and total < max_rows:
                    remain = min(len(batch), max_rows - total)
                    session.add_all(batch[:remain])
                    session.commit()
                    total += remain
        return {"message": f"成功导入{total}条GPS数据"}
    except Exception as e:
        return {"error": str(e)} 

@router.get("/gps-records")
def get_gps_records(
    commaddr: str = Query(..., description="车牌号"),
    start_utc: str = Query(..., description="起始时间戳，格式YYYYMMDDHHMMSS"),
    end_utc: str = Query(..., description="结束时间戳，格式YYYYMMDDHHMMSS")
):
    """
    从数据库查询指定车牌在时间范围内的GPS数据
    """
    try:
        with Session(engine) as session:
            # 构建查询条件
            query = select(GPSRecord).where(
                GPSRecord.commaddr == commaddr,
                GPSRecord.utc >= start_utc,
                GPSRecord.utc <= end_utc
            )
            records = session.exec(query).all()
            
            # 转换为字典格式返回
            result = []
            for record in records:
                result.append({
                    "id": record.id,
                    "commaddr": record.commaddr,
                    "utc": record.utc,
                    "lat": record.lat,
                    "lon": record.lon,
                    "head": record.head,
                    "speed": record.speed,
                    "tflag": record.tflag
                })
            
            return {
                "commaddr": commaddr,
                "start_utc": start_utc,
                "end_utc": end_utc,
                "count": len(result),
                "records": result
            }
    except Exception as e:
        return {"error": str(e)} 

def coordinate_transform(lat: float, lon: float, from_system: str = "WGS84", to_system: str = "BD09") -> Tuple[float, float]:
    """
    坐标系转换函数
    支持WGS84、GCJ02、BD09坐标系之间的转换
    """
    if from_system == to_system:
        return lat, lon
    
    # WGS84 -> GCJ02
    def wgs84_to_gcj02(lat: float, lon: float) -> Tuple[float, float]:
        a = 6378245.0
        ee = 0.00669342162296594323
        
        def transform_lat(x: float, y: float) -> float:
            ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
            ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
            ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
            ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
            return ret
        
        def transform_lon(x: float, y: float) -> float:
            ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
            ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
            ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
            ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
            return ret
        
        dlat = transform_lat(lon - 105.0, lat - 35.0)
        dlon = transform_lon(lon - 105.0, lat - 35.0)
        radlat = lat / 180.0 * math.pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
        dlon = (dlon * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
        mglat = lat + dlat
        mglon = lon + dlon
        return mglat, mglon
    
    # GCJ02 -> BD09
    def gcj02_to_bd09(lat: float, lon: float) -> Tuple[float, float]:
        z = math.sqrt(lon * lon + lat * lat) + 0.00002 * math.sin(lat * math.pi)
        theta = math.atan2(lat, lon) + 0.000003 * math.cos(lon * math.pi)
        bd_lon = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return bd_lat, bd_lon
    
    # WGS84 -> BD09
    def wgs84_to_bd09(lat: float, lon: float) -> Tuple[float, float]:
        gcj_lat, gcj_lon = wgs84_to_gcj02(lat, lon)
        return gcj02_to_bd09(gcj_lat, gcj_lon)
    
    if from_system == "WGS84" and to_system == "BD09":
        return wgs84_to_bd09(lat, lon)
    elif from_system == "WGS84" and to_system == "GCJ02":
        return wgs84_to_gcj02(lat, lon)
    elif from_system == "GCJ02" and to_system == "BD09":
        return gcj02_to_bd09(lat, lon)
    else:
        # 其他转换暂不支持，返回原坐标
        return lat, lon

def filter_gps_noise(points: List[dict], max_speed: float = 50.0, max_acceleration: float = 10.0) -> List[dict]:
    """
    过滤GPS噪声点
    基于速度和加速度异常值检测
    """
    if len(points) < 2:
        return points
    
    filtered_points = [points[0]]  # 保留第一个点
    
    for i in range(1, len(points)):
        current = points[i]
        previous = points[i-1]
        
        # 计算时间差（秒）
        try:
            current_time = datetime.strptime(current['utc'], "%Y%m%d%H%M%S")
            previous_time = datetime.strptime(previous['utc'], "%Y%m%d%H%M%S")
            time_diff = (current_time - previous_time).total_seconds()
        except:
            time_diff = 1.0  # 默认1秒
        
        if time_diff <= 0:
            continue
        
        # 计算距离（米）
        lat1, lon1 = previous['lat'], previous['lon']
        lat2, lon2 = current['lat'], current['lon']
        
        # 使用Haversine公式计算距离
        R = 6371000  # 地球半径（米）
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        # 计算实际速度（m/s）
        actual_speed = distance / time_diff if time_diff > 0 else 0
        
        # 检查速度是否合理（转换为km/h）
        speed_kmh = actual_speed * 3.6
        if speed_kmh > max_speed:
            print(f"过滤异常速度点: {speed_kmh:.1f} km/h")
            continue
        
        # 检查加速度（如果有点数足够）
        if len(filtered_points) > 1:
            prev_speed = float(previous.get('speed', 0)) / 100  # 转换为m/s
            acceleration = abs(actual_speed - prev_speed) / time_diff if time_diff > 0 else 0
            if acceleration > max_acceleration:
                print(f"过滤异常加速度点: {acceleration:.1f} m/s²")
                continue
        
        filtered_points.append(current)
    
    return filtered_points

def smooth_trajectory(points: List[dict], window_size: int = 3) -> List[dict]:
    """
    轨迹平滑处理
    使用移动平均窗口平滑坐标
    """
    if len(points) < window_size:
        return points
    
    smoothed_points = []
    
    for i in range(len(points)):
        # 计算窗口范围
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(points), i + window_size // 2 + 1)
        
        # 计算窗口内坐标的平均值
        window_lats = [points[j]['lat'] for j in range(start_idx, end_idx)]
        window_lons = [points[j]['lon'] for j in range(start_idx, end_idx)]
        
        avg_lat = sum(window_lats) / len(window_lats)
        avg_lon = sum(window_lons) / len(window_lons)
        
        # 创建平滑后的点
        smoothed_point = points[i].copy()
        smoothed_point['lat'] = avg_lat
        smoothed_point['lon'] = avg_lon
        smoothed_points.append(smoothed_point)
    
    return smoothed_points

@router.get("/gps-records-corrected")
def get_gps_records_corrected(
    commaddr: str = Query(..., description="车牌号"),
    start_utc: str = Query(..., description="起始时间戳，格式YYYYMMDDHHMMSS"),
    end_utc: str = Query(..., description="结束时间戳，格式YYYYMMDDHHMMSS"),
    coordinate_system: str = Query("BD09", description="目标坐标系：WGS84, GCJ02, BD09")
):
    """
    获取坐标系转换后的GPS数据
    将WGS84坐标转换为指定坐标系（推荐BD09用于百度地图）
    """
    try:
        with Session(engine) as session:
            # 构建查询条件
            query = select(GPSRecord).where(
                GPSRecord.commaddr == commaddr,
                GPSRecord.utc >= start_utc,
                GPSRecord.utc <= end_utc
            ).order_by(GPSRecord.utc)
            records = session.exec(query).all()
            
            if not records:
                return {
                    "commaddr": commaddr,
                    "start_utc": start_utc,
                    "end_utc": end_utc,
                    "count": 0,
                    "records": [],
                    "correction_info": {
                        "original_count": 0,
                        "coordinate_system": coordinate_system
                    }
                }
            
            # 转换为字典格式并应用坐标系转换
            corrected_points = []
            for record in records:
                point = {
                    "id": record.id,
                    "commaddr": record.commaddr,
                    "utc": record.utc,
                    "lat": record.lat,
                    "lon": record.lon,
                    "head": record.head,
                    "speed": record.speed,
                    "tflag": record.tflag
                }
                
                # 坐标系转换
                if coordinate_system != "WGS84":
                    point['lat'], point['lon'] = coordinate_transform(
                        point['lat'], point['lon'], 
                        from_system="WGS84", 
                        to_system=coordinate_system
                    )
                
                corrected_points.append(point)
            
            return {
                "commaddr": commaddr,
                "start_utc": start_utc,
                "end_utc": end_utc,
                "count": len(corrected_points),
                "records": corrected_points,
                "correction_info": {
                    "original_count": len(records),
                    "coordinate_system": coordinate_system
                }
            }
    except Exception as e:
        return {"error": str(e)} 

@router.get("/jinan-geojson")
def get_jinan_geojson():
    """
    返回济南市geojson地图数据
    """
    geojson_path = Path("app/data/json/370100_full.json")
    if not geojson_path.exists():
        return JSONResponse(status_code=404, content={"error": "济南市geojson文件不存在"})
    return FileResponse(str(geojson_path), media_type="application/json") 