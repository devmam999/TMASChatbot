"""
AI service for communicating with Anthropic Claude API
Handles text and image processing, generates explanations and Manim code
"""
import httpx
import json
import re
import base64
import asyncio
from typing import Dict, Any, Optional, Tuple
from utils.config import settings


class AIService:
    """Service for interacting with Anthropic Claude API"""
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
    
    async def generate_response(
        self, 
        text: Optional[str] = None, 
        image_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate AI response with explanation and Manim code
        
        Args:
            text: User's text input
            image_path: Path to uploaded image file
            
        Returns:
            Tuple of (explanation, manim_code)
        """
        try:
            # Build the prompt based on input type
            prompt = self._build_prompt(text, image_path)
            
            # Prepare messages for the API
            messages = self._prepare_messages(prompt, image_path)
            
            # Make API request
            response = await self._make_api_request(messages)
            
            # Parse the response to extract explanation and Manim code
            explanation, manim_code = self._parse_response(response)
            
            return explanation, manim_code
            
        except Exception as e:
            raise Exception(f"Failed to generate AI response: {str(e)}")
    
    async def generate_simple_response(self, prompt: str) -> Tuple[str, str]:
        """
        Generate a simple AI response without requiring Manim code
        
        Args:
            prompt: Simple text prompt
            
        Returns:
            Tuple of (explanation, "") - no Manim code
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful educational assistant. Provide clear, concise explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self._make_api_request(messages)
            content = response["choices"][0]["message"]["content"]
            
            return content.strip(), ""  # Return explanation only, no Manim code
            
        except Exception as e:
            raise Exception(f"Failed to generate simple AI response: {str(e)}")
    
    async def generate_simple_animation_response(self, prompt: str) -> Tuple[str, str]:
        """
        Generate a simple response with basic animation code that works on limited environments
        
        Args:
            prompt: User's question
            
        Returns:
            Tuple of (explanation, simple_animation_code)
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful educational assistant. When asked to explain concepts, provide:
1. A clear explanation (2-3 sentences)
2. Simple Manim animation code that specifically demonstrates the concept being asked about

CRITICAL: The animation MUST be directly related to the user's question. Do not create generic animations.

Use only basic Manim features that work in limited environments:
- Basic shapes (Circle, Square, Rectangle, Triangle)
- Text and MathTex
- Transformations (Create, FadeIn, FadeOut, MoveTo)
- Simple colors (RED, BLUE, GREEN, YELLOW, WHITE)

Avoid complex features like:
- LaTeX equations
- Custom fonts
- Complex animations
- External files

Keep animations under 10 seconds and make them directly relevant to the concept being explained.

Examples:
- If asked about sorting: Show elements being sorted step by step
- If asked about graphs: Show nodes and edges being created
- If asked about math: Show mathematical operations visually
- If asked about physics: Show forces, motion, or energy concepts
- If asked about algorithms: Show the algorithm working step by step"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self._make_api_request(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Split into explanation and code
            parts = content.split("```python")
            if len(parts) >= 2:
                explanation = parts[0].strip()
                code_part = parts[1].split("```")[0].strip()
                return explanation, code_part
            else:
                return content.strip(), ""
                
        except Exception as e:
            raise Exception(f"Failed to generate simple animation response: {str(e)}")
    
    def _build_prompt(self, text: Optional[str], image_path: Optional[str]) -> str:
        """Build the prompt based on input type"""
        base_prompt = """
You are an expert educator and Python programmer specializing in creating educational animations using the Manim library.

Your task is to:
1. Provide a clear, educational explanation of the concept
2. Write Python code using Manim to create an animation that visualizes the concept

IMPORTANT REQUIREMENTS:
- The Manim code must be complete and executable
- Use the latest Manim syntax (v0.19.0+)
- The animation should be educational and visually appealing
- Keep the animation duration reasonable (10-30 seconds for substantial content)
- Include multiple sequential animation steps (5–10 minimum for complex topics)
- Use clear colors (RED, GREEN, BLUE) and readable text (TEXT with font size 24+)
- Include proper imports and scene class definition (from manim import *, Scene subclasses, etc.)
- Show step-by-step processes with visual transitions
- Use animations like Create(), Write(), Transform(), MoveTo(), etc.
- Make sure animations are engaging and educational
- Use pauses (wait()) between important steps so the viewer can follow the reasoning

EDUCATIONAL STRUCTURE:

Each animation should include:

- Title introduction — show the concept name in a large, readable font

- Step-by-step buildup — introduce elements gradually and explain each stage visually

- Highlighting important parts — use color changes, scaling, and highlighting to show focus

- Transitions between states — avoid abrupt changes; show the process evolving

- Summary or conclusion — recap the key idea at the end with a short final statement


OUTPUT FORMAT
Educational Explanation — 2–3 paragraphs, simple and clear, describing the concept and its real-world relevance

Complete Manim Python Code — in a code block, ready to run

Example python code structure:

from manim import *

class ConceptAnimation(Scene):
    def construct(self):
        # Step 1: Title
        title = Text("Concept Name", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(1)

        # Step 2: First visual setup
        subtitle = Text("Step 1: Initial State", font_size=28).next_to(title, DOWN)
        self.play(Write(subtitle))
        self.wait(1)

        # Step 3: Create objects
        circle = Circle(color=RED).shift(LEFT*2)
        square = Square(color=GREEN).shift(RIGHT*2)
        self.play(Create(circle), Create(square))
        self.wait(1)

        # Step 4: Transform objects
        self.play(circle.animate.scale(1.5).set_color(PURPLE),
                  square.animate.rotate(PI/4).set_color(ORANGE))
        self.wait(1)

        # Step 5: Connect elements
        line = Line(circle.get_center(), square.get_center(), color=YELLOW)
        self.play(Create(line))
        self.wait(1)

        # Step 6: Final message
        final_text = Text("Concept Complete!", font_size=30, color=GREEN).shift(DOWN*2)
        self.play(Write(final_text))
        self.wait(2)

        # Step 7: Fade out
        self.play(FadeOut(VGroup(title, subtitle, circle, square, line, final_text)))
        self.wait(0.5)
```
"""
        
        if text and image_path:
            return f"{base_prompt}\n\nUSER INPUT:\nText: {text}\nImage: [User uploaded an image]\n\nPlease analyze both the text and image to provide a comprehensive explanation and animation."
        elif text:
            return f"{base_prompt}\n\nUSER INPUT:\nText: {text}\n\nPlease provide an explanation and create a Manim animation for this concept."
        elif image_path:
            return f"{base_prompt}\n\nUSER INPUT:\nImage: [User uploaded an image]\n\nPlease analyze the image content and provide an explanation with a relevant Manim animation."
        else:
            raise ValueError("Either text or image must be provided")
    
    def _prepare_messages(self, prompt: str, image_path: Optional[str]) -> list:
        """Prepare messages for the API request"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert educator and Python programmer specializing in Manim animations."
            }
        ]
        
        if image_path:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Add image message
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            })
        else:
            # Text-only message
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        return messages
    
    async def _make_api_request(self, messages: list) -> Dict[str, Any]:
        """Make the actual API request to Anthropic Claude"""
        anthropic_url = "https://api.anthropic.com/v1/messages"
        max_retries = 2

        # Extract system prompt separately (Claude expects it as its own field)
        system_prompt = ""
        if messages and messages[0]["role"] == "system":
            system_prompt = messages[0]["content"]
            messages = messages[1:]

        # Convert messages to Claude's block format
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({
                "role": msg["role"],
                "content": (
                    [{"type": "text", "text": msg["content"]}]
                    if isinstance(msg["content"], str)
                    else msg["content"]  # Already in Claude's block format
                )
            })

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        anthropic_url,
                        headers={
                            "x-api-key": self.api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                            "HTTP-Referer": "http://localhost:5173",
                            "X-Title": "TMAS Chatbot"
                        },
                        json={
                            "model": self.model,
                            "max_tokens": 4000,
                            "temperature": 0.7,
                            "system": system_prompt,
                            "messages": anthropic_messages
                        },
                        timeout=120.0
                    )

                    if response.status_code != 200:
                        raise Exception(
                            f"API request failed: {response.status_code} - {response.text}"
                        )

                    return response.json()

            except httpx.TimeoutException:
                if attempt < max_retries:
                    print(f"API request timed out, retrying... (attempt {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise Exception("API request timed out after all retries")

            except Exception as e:
                if attempt < max_retries:
                    print(f"API request failed, retrying... (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

    
    def _parse_response(self, api_response: Dict[str, Any]) -> Tuple[str, str]:
        """Parse Claude API response into explanation + Manim code"""
        try:
            if "content" not in api_response:
                raise Exception("Unexpected Claude API response format")

            content_text = "".join(
                block["text"] for block in api_response["content"] if block["type"] == "text"
            )

            # Extract code if present
            code_match = re.search(r"```python(.*?)(```|$)", content_text, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                explanation = content_text.split("```python")[0].strip()
                return explanation, code
            else:
                return content_text.strip(), ""
        except Exception as e:
            raise Exception(f"Failed to parse Claude API response: {str(e)}")
                
    async def debug_manim_code(self, code: str, error: str) -> str:
        """
        Given faulty Manim code and an error message, ask the LLM to debug and fix the code.
        Returns the fixed code as a string.
        """
        system_prompt = (
            "You are an expert Python and Manim debugger. "
            "Given code that fails with an error, your job is to fix the code so it works in Manim v0.19.0+. "
            "Return ONLY the fixed code, no explanation."
        )
        user_prompt = (
            f"The following Manim code fails with this error:\n"
            f"{error}\n"
            f"Please fix the code so it works in Manim v0.19.0+. Return only the fixed code.\n"
            f"\nCODE:\n{code}"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response = await self._make_api_request(messages)
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    
    async def test_connection(self) -> bool:
        """Test the API connection"""
        try:
            messages = [
                {"role": "user", "content": "Hello, this is a test message."}
            ]
            
            # Use a shorter timeout for connection test
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                                                    "X-Title": "TMAS Chatbot"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 5,  # Very short response for test
                        "temperature": 0.7
                    }
                )
                
                if response.status_code != 200:
                    print(f"Connection test failed with status code: {response.status_code}")
                    return False
                
                result = response.json()
                return "choices" in result and len(result["choices"]) > 0
                
        except httpx.TimeoutException:
            print("Connection test timed out")
            return False
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False 