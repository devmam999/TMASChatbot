"""
File utility functions
"""
import os
import time
import shutil
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, create it if it doesn't"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def generate_unique_filename(base_name: str, extension: str = "") -> str:
    """Generate a unique filename with timestamp"""
    timestamp = int(time.time())
    if extension and not extension.startswith('.'):
        extension = f".{extension}"
    return f"{base_name}_{timestamp}{extension}"


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> None:
    """Clean up files older than max_age_hours"""
    if not os.path.exists(directory):
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up old files: {e}")
