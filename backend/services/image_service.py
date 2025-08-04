"""
Image processing service for handling uploaded images
"""
import os
import pytesseract
from PIL import Image
from typing import Optional
from utils.file_utils import save_base64_image, is_valid_image_file


class ImageService:
    """Service for processing uploaded images"""
    
    def __init__(self):
        self.upload_dir = "./uploads"
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    async def process_image(self, image_base64: str) -> tuple[str, Optional[str]]:
        """
        Process uploaded image and extract text content
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Tuple of (file_path, extracted_text)
        """
        try:
            # Save the image to disk
            file_path, filename = save_base64_image(image_base64, self.upload_dir)
            
            # Validate the image
            if not is_valid_image_file(file_path):
                raise ValueError("Invalid image file")
            
            # Extract text from image using OCR
            extracted_text = self._extract_text_from_image(file_path)
            
            return file_path, extracted_text
            
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")
    
    def _extract_text_from_image(self, image_path: str) -> Optional[str]:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text or None if no text found
        """
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            cleaned_text = self._clean_extracted_text(text)
            
            return cleaned_text if cleaned_text.strip() else None
            
        except Exception as e:
            print(f"OCR extraction failed: {str(e)}")
            return None
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean up extracted OCR text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace and normalize
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are likely noise (very short or all caps)
            if len(line) < 2 or (line.isupper() and len(line) < 3):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get information about the image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image information
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
        except Exception as e:
            return {'error': str(e)}
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if the image format is supported"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    def cleanup_uploaded_images(self, max_age_hours: int = 1) -> None:
        """Clean up old uploaded images"""
        from ..utils.file_utils import cleanup_old_files
        cleanup_old_files(self.upload_dir, max_age_hours) 