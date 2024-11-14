from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os  # Import os to handle file path and directory creation

from app import crud
from app.models import GeoFile
from app.api import deps
from app.models import User

router = APIRouter()

# Dependency to get the current authenticated user
# This uses the get_current_user function from deps.py
# that decodes the JWT token, fetches the user from the database,
# and ensures the user is active.
@router.post("/upload", response_model=GeoFile)
def upload_geofile(
    file: UploadFile = File(...),  # Accepts an uploaded file
    description: str = None,  # Optional description for the file
    db: Session = Depends(deps.get_db),  # Database session dependency
    current_user: User = Depends(deps.get_current_user),  # Get the current authenticated user
):
    """
    Endpoint to upload a geospatial file. The file is saved to a designated directory, 
    and a record is created in the database associating the file with the current user.
    """
    # Directory where files will be stored
    upload_dir = "uploads"  
    os.makedirs(upload_dir, exist_ok=True)  # Create directory if it doesn't exist
    
    # Construct file path
    file_location = os.path.join(upload_dir, file.filename)
    
    # Write the file to the storage path
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # Create geofile record in the database with user ownership
    geofile = crud.create_geofile(
        db=db,
        owner_id=current_user.id,
        file_name=file.filename,
        file_path=file_location,
        description=description,
    )
    return geofile  # Return the created geofile record


# Dependency to get a list of geofiles uploaded by the current user
@router.get("/", response_model=List[GeoFile])
def list_geofiles(
    db: Session = Depends(deps.get_db),  # Database session dependency
    current_user: User = Depends(deps.get_current_user),  # Get the current authenticated user
):
    """
    Retrieve a list of geofiles uploaded by the current user.
    """
    return crud.get_user_geofiles(db=db, user_id=current_user.id)


# Dependency to retrieve details of a specific geofile by its ID.
# Access to geofile is restricted to the file's owner.
@router.get("/{geofile_id}", response_model=GeoFile)
def get_geofile(
    geofile_id: UUID,  # Unique identifier for the geofile
    db: Session = Depends(deps.get_db),  # Database session dependency
    current_user: User = Depends(deps.get_current_user),  # Get the current authenticated user
):
    """
    Retrieve details of a specific geofile by its ID. Access is restricted to the file's owner.
    """
    geofile = crud.get_geofile(db=db, geofile_id=geofile_id)
    
    # Check if geofile exists and if the user is the owner
    if not geofile or geofile.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Geofile not found")
    return geofile  # Return geofile details if access is allowed