from fastapi import APIRouter, File, UploadFile, HTTPException
import cloudinary
import cloudinary.uploader
import os

router = APIRouter(prefix="/upload", tags=["upload"])

# Initialize Cloudinary utilizing environment variables:
# CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
# Ensure this variable is set in your Render dashboard environment config.
try:
    cloudinary.config(secure=True)
except Exception as e:
    print(f"Cloudinary config error: {e}")

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    """Uploads an image to Cloudinary and returns the secure URL."""
    try:
        # Read the file bytes
        contents = await file.read()
        
        # Upload directly to Cloudinary
        upload_result = cloudinary.uploader.upload(
            contents,
            folder="routeconnect",
            resource_type="auto"
        )
        return {
            "url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
