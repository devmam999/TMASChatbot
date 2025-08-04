"""
Main FastAPI application for the TMAS Chatbot
"""
import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from typing import Optional
import re
import asyncio
import uuid
import types
from fastapi import Response

# Import our models and services
from models import ChatRequest, ChatResponse, HealthResponse, InputType
from services.ai_service import AIService
from services.manim_service import ManimService
from services.image_service import ImageService
from utils.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="TMAS Chatbot API",
    description="AI-powered chatbot with Manim animations",
    version="1.0.0"
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Global exception handler caught: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "explanation": "",
            "video_base64": None,
            "error_message": f"Internal server error: {str(exc)}",
            "input_type": "TEXT_ONLY"
        }
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()
manim_service = ManimService()
image_service = ImageService()

# Mount static files for serving media
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Validate configuration
        settings.validate_config()
        print("✅ Configuration validated successfully")
        
        # Ensure directories exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.MEDIA_DIR, exist_ok=True)
        
        # Clean up any old temporary files
        manim_service.cleanup_temp_files()
        
        print("🚀 Application started successfully")
        print("ℹ️ AI service connection will be tested on first request")
        
    except Exception as e:
        print(f"❌ Startup failed: {str(e)}")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health/ai")
async def ai_health_check():
    """AI service health check endpoint"""
    try:
        if await asyncio.wait_for(ai_service.test_connection(), timeout=30):
            return {
                "status": "healthy",
                "ai_service": "connected",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "degraded",
                "ai_service": "failed",
                "timestamp": datetime.now().isoformat()
            }
    except asyncio.TimeoutError:
        return {
            "status": "degraded",
            "ai_service": "timeout",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "ai_service": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/chat")
async def chat_endpoint(
    text: Optional[str] = Form(None, description="Text input from user"),
    image: Optional[UploadFile] = File(None, description="Image file upload")
):
    try:
        if not text and not image:
            raise HTTPException(status_code=400, detail="Either text or image must be provided")
        if text and image:
            input_type = InputType.TEXT_AND_IMAGE
        elif text:
            input_type = InputType.TEXT_ONLY
        else:
            input_type = InputType.IMAGE_ONLY
        image_path = None
        if image:
            if not image_service.is_supported_format(image.filename):
                raise HTTPException(status_code=400, detail="Unsupported image format. Supported: JPG, PNG, BMP, TIFF")
            image_content = await image.read()
            image_base64 = f"data:image/{image.content_type};base64,{image_content.hex()}"
            image_path, extracted_text = await image_service.process_image(image_base64)
            if text and extracted_text:
                text = f"{text}\n\nImage content: {extracted_text}"
            elif extracted_text:
                text = extracted_text
        print("Calling AI service for /chat...")
        start_time = time.time()
        
        # Test connection on first request
        if not hasattr(ai_service, '_connection_tested'):
            try:
                print("Testing AI service connection...")
                if await asyncio.wait_for(ai_service.test_connection(), timeout=10):
                    print("✅ AI service connection successful")
                else:
                    print("⚠️ AI service connection failed, but continuing...")
                ai_service._connection_tested = True
            except Exception as e:
                print(f"⚠️ AI service connection test failed: {str(e)}, but continuing...")
                ai_service._connection_tested = True
        
        try:
            explanation, manim_code = await asyncio.wait_for(
                ai_service.generate_response(text=text, image_path=image_path),
                timeout=120  # seconds - increased from 60
            )
            elapsed_time = time.time() - start_time
            print(f"AI service returned for /chat in {elapsed_time:.2f} seconds.")
        except asyncio.TimeoutError:
            print("AI service timed out for /chat, trying fallback mode...")
            try:
                # Fallback: try with a simpler prompt that can still generate animations
                fallback_prompt = f"Please provide a clear explanation and create a simple animation that specifically demonstrates: {text}"
                explanation, manim_code = await asyncio.wait_for(
                    ai_service.generate_simple_animation_response(fallback_prompt),
                    timeout=60  # shorter timeout for fallback
                )
                print("Fallback AI service returned for /chat.")
            except asyncio.TimeoutError:
                print("Fallback AI service also timed out for /chat.")
                raise HTTPException(status_code=504, detail="AI service timed out after 120 seconds. Please try a simpler question or try again later.")
        except Exception as e:
            print(f"AI service error for /chat: {str(e)}")
            # Try fallback even for other errors
            try:
                fallback_prompt = f"Please provide a clear explanation and create a simple animation that specifically demonstrates: {text}"
                explanation, manim_code = await asyncio.wait_for(
                    ai_service.generate_simple_animation_response(fallback_prompt),
                    timeout=60
                )
                print("Fallback AI service returned for /chat after error.")
            except Exception as fallback_error:
                print(f"Fallback also failed: {str(fallback_error)}")
                raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Failed to clean up image file: {e}")
        # If Manim code is present, return base64 video
        video_base64 = None
        if manim_code:
            match = re.search(r'class\s+(\w+)\(Scene\):', manim_code)
            class_name = match.group(1) if match else "ConceptAnimation"
            try:
                video_base64 = await asyncio.wait_for(
                    manim_service.generate_animation_base64(manim_code, class_name=class_name),
                    timeout=180  # 3 minutes for Manim generation
                )
            except asyncio.TimeoutError:
                print("Manim generation timed out, returning explanation only")
                video_base64 = None
        return {
            "success": True,
            "explanation": explanation,
            "video_base64": video_base64,
            "error_message": None,
            "input_type": input_type
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "explanation": "",
            "video_base64": None,
            "error_message": str(e),
            "input_type": input_type if 'input_type' in locals() else InputType.TEXT_ONLY
        }

@app.post("/chat/stream")
async def chat_stream_endpoint(
    text: Optional[str] = Form(None, description="Text input from user"),
    image: Optional[UploadFile] = File(None, description="Image file upload")
):
    try:
        if not text and not image:
            raise HTTPException(status_code=400, detail="Either text or image must be provided")
        if text and image:
            input_type = InputType.TEXT_AND_IMAGE
        elif text:
            input_type = InputType.TEXT_ONLY
        else:
            input_type = InputType.IMAGE_ONLY
        image_path = None
        if image:
            if not image_service.is_supported_format(image.filename):
                raise HTTPException(status_code=400, detail="Unsupported image format. Supported: JPG, PNG, BMP, TIFF")
            image_content = await image.read()
            image_base64 = f"data:image/{image.content_type};base64,{image_content.hex()}"
            image_path, extracted_text = await image_service.process_image(image_base64)
            if text and extracted_text:
                text = f"{text}\n\nImage content: {extracted_text}"
            elif extracted_text:
                text = extracted_text
        print("Calling AI service for /chat/stream...")
        start_time = time.time()
        
        # Test connection on first request
        if not hasattr(ai_service, '_connection_tested'):
            try:
                print("Testing AI service connection...")
                if await asyncio.wait_for(ai_service.test_connection(), timeout=10):
                    print("✅ AI service connection successful")
                else:
                    print("⚠️ AI service connection failed, but continuing...")
                ai_service._connection_tested = True
            except Exception as e:
                print(f"⚠️ AI service connection test failed: {str(e)}, but continuing...")
                ai_service._connection_tested = True
        
        try:
            explanation, manim_code = await asyncio.wait_for(
                ai_service.generate_response(text=text, image_path=image_path),
                timeout=120  # seconds - increased from 60
            )
            elapsed_time = time.time() - start_time
            print(f"AI service returned for /chat/stream in {elapsed_time:.2f} seconds.")
            print(f"[Main] Explanation length: {len(explanation)}")
            print(f"[Main] Manim code length: {len(manim_code) if manim_code else 0}")
            if manim_code:
                print(f"[Main] Manim code starts with: {manim_code[:100]}...")
            else:
                print("[Main] No Manim code generated by AI service")
        except asyncio.TimeoutError:
            print("AI service timed out for /chat/stream, trying fallback mode...")
            try:
                # Fallback: try with a simpler prompt that can still generate animations
                fallback_prompt = f"Please provide a clear explanation and create a simple animation that specifically demonstrates: {text}"
                explanation, manim_code = await asyncio.wait_for(
                    ai_service.generate_simple_animation_response(fallback_prompt),
                    timeout=60  # shorter timeout for fallback
                )
                print("Fallback AI service returned for /chat/stream.")
                print(f"[Main] Fallback explanation length: {len(explanation)}")
                print(f"[Main] Fallback Manim code length: {len(manim_code) if manim_code else 0}")
                if manim_code:
                    print(f"[Main] Fallback Manim code starts with: {manim_code[:100]}...")
                else:
                    print("[Main] No Manim code generated by fallback AI service")
            except asyncio.TimeoutError:
                print("Fallback AI service also timed out for /chat/stream.")
                raise HTTPException(status_code=504, detail="AI service timed out after 120 seconds. Please try a simpler question or try again later.")
        except Exception as e:
            print(f"AI service error for /chat/stream: {str(e)}")
            # Try fallback even for other errors
            try:
                fallback_prompt = f"Please provide a clear explanation and create a simple animation that specifically demonstrates: {text}"
                explanation, manim_code = await asyncio.wait_for(
                    ai_service.generate_simple_animation_response(fallback_prompt),
                    timeout=60
                )
                print("Fallback AI service returned for /chat/stream after error.")
            except Exception as fallback_error:
                print(f"Fallback also failed: {str(fallback_error)}")
                raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Failed to clean up image file: {e}")
        request_id = str(uuid.uuid4())
        print(f"[Main] Generated request_id: {request_id}")
        print(f"[Main] manim_code is None: {manim_code is None}")
        print(f"[Main] manim_code length: {len(manim_code) if manim_code else 0}")
        
        if manim_code:
            print(f"[Main] Manim code found, processing...")
            try:
                match = re.search(r'class\s+(\w+)\(Scene\):', manim_code)
                class_name = match.group(1) if match else "ConceptAnimation"
                print(f"[Main] Manim code detected, class_name: {class_name}")
                print(f"[Main] Manim code preview: {manim_code[:200]}...")

                async def run_manim_task():
                    try:
                        print(f"[Main] Starting Manim task for request_id: {request_id}")
                        max_attempts = 3
                        attempt = 0
                        current_code = manim_code
                        last_error = None
                        while attempt < max_attempts:
                            print(f"[Main] Manim attempt {attempt+1} for request_id: {request_id}")
                            video_path, error, code_used = await manim_service.render_and_store_video(current_code, class_name, request_id)
                            if error is None:
                                print(f"[Main] Manim succeeded on attempt {attempt+1} for request_id: {request_id}")
                                break
                            else:
                                print(f"[Main] Manim failed on attempt {attempt+1} with error: {error}")
                                last_error = error
                                try:
                                    fixed_code = await ai_service.debug_manim_code(code_used, error)
                                    print(f"[Main] AI debugger returned fixed code on attempt {attempt+1}. Retrying...")
                                    current_code = fixed_code
                                except Exception as debug_exc:
                                    print(f"[Main] AI debugger failed on attempt {attempt+1}: {debug_exc}")
                                    manim_service.no_video_requests.add(request_id)
                                    return
                            attempt += 1
                        else:
                            print(f"[Main] All Manim attempts failed for request_id: {request_id}. Marking as no video.")
                            manim_service.no_video_requests.add(request_id)
                    except Exception as e:
                        print(f"[Main] Manim task failed for request_id {request_id}: {str(e)}")
                        import traceback
                        print(f"[Main] Full traceback: {traceback.format_exc()}")
                        manim_service.no_video_requests.add(request_id)

                task = asyncio.create_task(run_manim_task())
                print(f"[Main] Created Manim task for request_id: {request_id}, task: {task}")
            except Exception as e:
                print(f"Failed to start Manim task: {str(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
                manim_service.no_video_requests.add(request_id)
        else:
            print(f"[Main] No Manim code found, skipping animation generation")
            manim_service.no_video_requests.add(request_id)
            print(f"[Main] Marked request {request_id} as no video")
        async def text_streamer():
            try:
                for word in explanation.split():
                    yield word + " "
                    await asyncio.sleep(0.03)
                yield f"\n[REQUEST_ID:{request_id}]\n"
            except Exception as e:
                # If streaming fails, yield the error message
                yield f"\nError during streaming: {str(e)}\n"
        return StreamingResponse(text_streamer(), media_type="text/plain")
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        async def error_stream():
            yield f"Sorry, I encountered an error: {error_message}"
        return StreamingResponse(error_stream(), media_type="text/plain")

@app.get("/chat/video/{request_id}")
async def get_video(request_id: str):
    video_path = manim_service.get_video_path(request_id)
    if video_path and os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4")
    else:
        return Response(status_code=202)  # 202 Accepted, not ready yet
@app.get("/chat/video_base64/{request_id}")
async def get_video_base64(request_id: str):
    video_path = manim_service.get_video_path(request_id)
    print(f"[Main] Video polling for request_id: {request_id}, video_path: {video_path}")
    
    # Check if this request_id has been marked as "no video will be created"
    if request_id in manim_service.no_video_requests:
        print(f"[Main] Request {request_id} marked as no video - returning 404")
        return Response(status_code=404, content="No video will be created for this request")
    
    if video_path and os.path.exists(video_path):
        print(f"[Main] Video found and exists: {video_path}")
        print(f"[Main] Video file size: {os.path.getsize(video_path)} bytes")
        with open(video_path, "rb") as f:
            import base64
            video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode("utf-8")
            print(f"[Main] Video base64 length: {len(video_base64)}")
            print(f"[Main] Video base64 preview: {video_base64[:100]}...")
        # Optionally, delete the file after serving
        try:
            os.remove(video_path)
        except Exception:
            pass
        
        # Clean up temp_manim directory after successful video generation
        try:
            import shutil
            temp_manim_dir = os.path.join(os.getcwd(), "temp_manim")
            if os.path.exists(temp_manim_dir):
                shutil.rmtree(temp_manim_dir)
                print(f"[Main] Cleaned up temp_manim directory")
        except Exception as e:
            print(f"[Main] Failed to clean up temp_manim: {e}")
        return JSONResponse({"video_base64": video_base64})
    else:
        print(f"[Main] Video not ready yet for request_id: {request_id}")
        # Debug: Print all video mappings
        print(f"[Main] All video mappings: {manim_service.video_map}")
        print(f"[Main] All no_video_requests: {manim_service.no_video_requests}")
        return Response(status_code=202)


@app.post("/chat-json", response_model=ChatResponse)
async def chat_json_endpoint(request: ChatRequest):
    """
    Alternative chat endpoint that accepts JSON with base64 image
    
    This endpoint accepts:
    - text: Optional string
    - image_base64: Optional base64 encoded image
    """
    try:
        # Validate input
        if not request.text and not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="Either text or image_base64 must be provided"
            )
        
        # Determine input type
        if request.text and request.image_base64:
            input_type = InputType.TEXT_AND_IMAGE
        elif request.text:
            input_type = InputType.TEXT_ONLY
        else:
            input_type = InputType.IMAGE_ONLY
        
        # Process image if provided
        image_path = None
        if request.image_base64:
            # Process base64 image
            image_path, extracted_text = await image_service.process_image(request.image_base64)
            
            # Combine text if both provided
            if request.text and extracted_text:
                text = f"{request.text}\n\nImage content: {extracted_text}"
            elif extracted_text:
                text = extracted_text
            else:
                text = request.text
        else:
            text = request.text
        
        # Generate AI response
        explanation, manim_code = await ai_service.generate_response(
            text=text,
            image_path=image_path
        )
        
        # Generate animation if Manim code was provided
        animation_url = None
        if manim_code:
            video_path = await manim_service.generate_animation(manim_code)
            if video_path:
                animation_url = manim_service.get_video_url(video_path)
        
        # Clean up temporary files
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Failed to clean up image file: {e}")
        
        return ChatResponse(
            success=True,
            explanation=explanation,
            animation_url=animation_url,
            error_message=None,
            input_type=input_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(
            success=False,
            explanation="",
            animation_url=None,
            error_message=str(e),
            input_type=input_type if 'input_type' in locals() else InputType.TEXT_ONLY
        )


@app.get("/media/{filename}")
async def serve_media(filename: str):
    """Serve media files (videos, images)"""
    file_path = os.path.join(settings.MEDIA_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    # Disable reload to prevent conflicts with Manim temp files
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disabled to prevent conflicts with Manim temp files
    ) 