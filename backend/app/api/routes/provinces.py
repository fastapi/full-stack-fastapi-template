"""API routes for Vietnamese administrative data (provinces, wards)."""
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import (
    AdministrativeRegion,
    AdministrativeRegionPublic,
    AdministrativeUnit,
    AdministrativeUnitPublic,
    Province,
    ProvincePublic,
    ProvincePublicWithDetails,
    ProvincesPublic,
    Ward,
    WardPublic,
    WardPublicWithDetails,
    WardsPublic,
)

router = APIRouter(prefix="/provinces", tags=["provinces"])


# =============================================================================
# Administrative Regions
# =============================================================================


@router.get("/regions", response_model=list[AdministrativeRegionPublic])
def read_administrative_regions(session: SessionDep) -> Any:
    """Get all administrative regions."""
    statement = select(AdministrativeRegion)
    regions = session.exec(statement).all()
    return regions


# =============================================================================
# Administrative Units
# =============================================================================


@router.get("/units", response_model=list[AdministrativeUnitPublic])
def read_administrative_units(session: SessionDep) -> Any:
    """Get all administrative units."""
    statement = select(AdministrativeUnit)
    units = session.exec(statement).all()
    return units


# =============================================================================
# Provinces
# =============================================================================


@router.get("/", response_model=ProvincesPublic)
def read_provinces(
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> Any:
    """Get all provinces with pagination."""
    statement = select(Province).offset(skip).limit(limit)
    provinces = session.exec(statement).all()
    
    count_statement = select(Province)
    total_count = len(session.exec(count_statement).all())
    
    return ProvincesPublic(data=provinces, count=total_count)


@router.get("/{province_code}", response_model=ProvincePublicWithDetails)
def read_province(session: SessionDep, province_code: str) -> Any:
    """Get a specific province by code with administrative unit details."""
    statement = select(Province).where(Province.code == province_code)
    province = session.exec(statement).first()
    
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    
    return province


# =============================================================================
# Wards (Districts/Communes)
# =============================================================================


@router.get("/{province_code}/wards", response_model=WardsPublic)
def read_wards_by_province(
    session: SessionDep,
    province_code: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
) -> Any:
    """Get all wards for a specific province."""
    # First check if province exists
    province_statement = select(Province).where(Province.code == province_code)
    province = session.exec(province_statement).first()
    
    if not province:
        raise HTTPException(status_code=404, detail="Province not found")
    
    # Get wards for this province
    statement = (
        select(Ward)
        .where(Ward.province_code == province_code)
        .offset(skip)
        .limit(limit)
    )
    wards = session.exec(statement).all()
    
    # Count total wards for this province
    count_statement = select(Ward).where(Ward.province_code == province_code)
    total_count = len(session.exec(count_statement).all())
    
    return WardsPublic(data=wards, count=total_count)


@router.get("/wards/{ward_code}", response_model=WardPublicWithDetails)
def read_ward(session: SessionDep, ward_code: str) -> Any:
    """Get a specific ward by code with details."""
    statement = select(Ward).where(Ward.code == ward_code)
    ward = session.exec(statement).first()
    
    if not ward:
        raise HTTPException(status_code=404, detail="Ward not found")
    
    return ward
