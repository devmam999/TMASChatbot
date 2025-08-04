"""
File utility functions for handling uploads, media, and file operations
"""
import os
import base64
import uuid
from typing import Optional, Tuple
from PIL import Image
import io
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def generate_unique_filename(extension: str = ".mp4") -> str:
    """Generate a unique filename with UUID"""
    return f"{uuid.uuid4().hex}{extension}"


def save_base64_image(base64_string: str, upload_dir: str) -> Tuple[str, str]:
    """
    Save a base64 encoded image to disk
    
    Args:
        base64_string: Base64 encoded image string
        upload_dir: Directory to save the image
    
    Returns:
        Tuple of (file_path, filename)
    """
    # Ensure upload directory exists
    ensure_directory_exists(upload_dir)
    
    # Generate unique filename
    filename = generate_unique_filename(".png")
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            # Extract the base64 part after the comma
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 and save image
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        
        # Save image
        image.save(file_path)
        
        return file_path, filename
    
    except Exception as e:
        raise ValueError(f"Failed to save base64 image: {str(e)}")


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    return os.path.getsize(file_path) / (1024 * 1024)


def is_valid_image_file(file_path: str) -> bool:
    """Check if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> None:
    """Clean up old files in a directory"""
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to remove old file {file_path}: {e}")


def get_media_url(filename: str) -> str:
    """Generate a URL for a media file"""
    return f"/media/{filename}" 