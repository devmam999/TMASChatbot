"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class InputType(str, Enum):
    """Enum for different input types"""
    TEXT_ONLY = "text_only"
    IMAGE_ONLY = "image_only"
    TEXT_AND_IMAGE = "text_and_image"


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint
    Handles text and/or image input
    """
    text: Optional[str] = Field(None, description="Text input from user")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "text": "Explain how a binary search tree works",
                "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
            }
        }


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint
    Returns explanation and animation video
    """
    success: bool = Field(..., description="Whether the request was successful")
    explanation: str = Field(..., description="AI-generated explanation")
    animation_url: Optional[str] = Field(None, description="URL to the generated animation video")
    error_message: Optional[str] = Field(None, description="Error message if something went wrong")
    input_type: InputType = Field(..., description="Type of input processed")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "explanation": "A binary search tree is a hierarchical data structure...",
                "animation_url": "/media/animations/bst_animation.mp4",
                "error_message": None,
                "input_type": "text_and_image"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code") 