"""File uploads router"""
import os
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models import Users
from app.schemas.uploads import FileUploadResponse, FileListResponse
from app.dependencies import get_current_active_user

router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".doc", ".docx"}


def ensure_upload_dir():
    """Ensure upload directory exists"""
    os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/images", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    patient_id: int | None = Query(None),
    notes: str | None = Query(None),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload an image or document file

    Args:
        file: File to upload
        patient_id: Associated patient ID (optional)
        notes: Additional notes (optional)
        current_user: Current authenticated user
        db: Database session

    Returns:
        File upload response

    Raises:
        HTTPException: If file type not allowed or size exceeds limit
    """
    ensure_upload_dir()

    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024*1024)}MB"
        )

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, filename)

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    return FileUploadResponse(
        filename=filename,
        file_path=file_path,
        file_size=len(contents),
        content_type=file.content_type or "application/octet-stream",
        uploaded_at=datetime.now(),
        uploaded_by=current_user.user_id,
        associated_patient_id=patient_id,
        notes=notes
    )


@router.get("/images/{filename}")
async def download_image(
    filename: str,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download/retrieve an uploaded file

    Raises:
        HTTPException: If file not found or access denied
    """
    file_path = os.path.join(settings.upload_dir, filename)

    # Security check: ensure file is within upload directory
    real_path = os.path.realpath(file_path)
    upload_dir_path = os.path.realpath(settings.upload_dir)

    if not real_path.startswith(upload_dir_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )

    return {
        "filename": filename,
        "file_path": file_path,
        "exists": True
    }


@router.get("/images")
async def list_images(
    patient_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List uploaded files with optional pagination

    Returns:
        List of uploaded files
    """
    ensure_upload_dir()

    files = []
    try:
        for filename in os.listdir(settings.upload_dir):
            file_path = os.path.join(settings.upload_dir, filename)
            if os.path.isfile(file_path):
                file_info = {
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": os.path.getsize(file_path),
                    "uploaded_at": datetime.fromtimestamp(os.path.getmtime(file_path)),
                    "content_type": "image" if any(
                        filename.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]
                    ) else "file"
                }
                files.append(file_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )

    # Sort by date, newest first
    files.sort(key=lambda x: x["uploaded_at"], reverse=True)

    # Apply pagination
    files = files[skip:skip + limit]

    return FileListResponse(
        files=files,
        total_count=len(files)
    )


@router.delete("/images/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    filename: str,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file

    Raises:
        HTTPException: If file not found or access denied
    """
    file_path = os.path.join(settings.upload_dir, filename)

    # Security check
    real_path = os.path.realpath(file_path)
    upload_dir_path = os.path.realpath(settings.upload_dir)

    if not real_path.startswith(upload_dir_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {filename} not found"
        )

    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
