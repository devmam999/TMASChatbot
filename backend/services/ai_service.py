"""
AI service for communicating with OpenRouter API
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
    """Service for interacting with OpenRouter API"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
    
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
- Use clear colors and readable text
- Include proper imports and scene class definition
- Create SUBSTANTIAL animations with multiple steps, not just static text
- Show step-by-step processes with visual transitions
- Use animations like Create(), Write(), Transform(), MoveTo(), etc.
- Include at least 5-10 animation steps for complex algorithms
- Make sure animations are engaging and educational

CRITICAL MANIM GRAPH REQUIREMENTS:
- When creating graphs, use proper edge format: edges = [(node1, node2), ...]
- For Graph() constructor, edges must be tuples: (node1, node2) without weights
- Use vertices = [1, 2, 3, ...] for node labels
- Use edges = [(1, 2), (1, 3), ...] for edges (no weights in tuples)
- For edge labels, use: edge_labels = {(1, 2): "7", (1, 3): "9", ...}
- Graph constructor should be: Graph(vertices, edges, labels=True, edge_labels=edge_labels)
- DO NOT use edge_type=LabeledArrow or edge_labels as a direct parameter
- DO NOT use edge_labels=edge_labels in the constructor - this is WRONG
- The correct syntax is: Graph(vertices, edges, labels=True, edge_labels=edge_labels)
- Always test your graph creation before adding animations
- Create SUBSTANTIAL animations with multiple steps and visual effects
- Make sure animations are at least 10-30 seconds long with multiple steps
- Show the algorithm working step by step, not just static text
- Use colors, highlights, and movements to demonstrate the concept
- Include at least 3-5 animation steps for complex algorithms

RESPONSE FORMAT:
1. First provide a detailed explanation (2-3 paragraphs)
2. Then provide the complete Manim Python code in a code block

Example Manim code structure:
```python
from manim import *

class ConceptAnimation(Scene):
    def construct(self):
        # Create substantial animation with multiple steps
        title = Text("Concept Title", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        
        # Step 1: Show initial state
        step1 = Text("Step 1: Initial Setup", font_size=24).next_to(title, DOWN)
        self.play(Write(step1))
        self.wait(0.5)
        
        # Step 2: Create and animate objects
        circle = Circle(color=RED, radius=0.5).shift(LEFT * 2)
        square = Square(color=GREEN, side_length=1).shift(RIGHT * 2)
        self.play(Create(circle), Create(square))
        self.wait(0.5)
        
        # Step 3: Show transformation
        self.play(
            circle.animate.scale(1.5).set_color(PURPLE),
            square.animate.rotate(PI/4).set_color(ORANGE)
        )
        self.wait(0.5)
        
        # Step 4: Add connecting elements
        line = Line(circle.get_center(), square.get_center(), color=WHITE)
        self.play(Create(line))
        self.wait(0.5)
        
        # Step 5: Final state
        final_text = Text("Process Complete!", font_size=28, color=GREEN)
        self.play(Write(final_text))
        self.wait(1)
        
        # Clean up
        self.play(FadeOut(VGroup(title, step1, circle, square, line, final_text)))
        self.wait(0.5)
```

Example for graph algorithms (like Dijkstra's):
```python
from manim import *

class DijkstraAnimation(Scene):
    def construct(self):
        # Title
        title = Text("Dijkstra's Algorithm", font_size=36, color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        
        # Create vertices and edges properly
        vertices = [1, 2, 3, 4, 5, 6]
        edges = [(1, 2), (1, 3), (1, 6), (2, 3), (2, 4), (3, 4), (3, 6), (4, 5), (5, 6)]
        
        # Create graph with proper format (no weights in edges)
        g = Graph(vertices, edges, layout="kamada_kawai")
        g.scale(1.5)
        g.to_edge(LEFT)
        
        # Show initial graph
        self.play(Create(g))
        self.wait(1)
        
        # Initialize distances display
        distance_panel = VGroup()
        for v in vertices:
            dist_text = Text(f"d({v}) = ∞", font_size=20, color=RED)
            distance_panel.add(dist_text)
        distance_panel.arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)
        self.play(Write(distance_panel))
        self.wait(0.5)
        
        # Step 1: Start with node 1
        start_node = g.vertices[1]
        self.play(start_node.animate.set_color(YELLOW))
        self.wait(0.5)
        
        # Update distance for start node
        new_dist_text = Text("d(1) = 0", font_size=20, color=GREEN)
        new_dist_text.move_to(distance_panel[0])
        self.play(Transform(distance_panel[0], new_dist_text))
        self.wait(0.5)
        
        # Step 2: Process neighbors of node 1
        neighbors = [(2, 7), (3, 9), (6, 14)]
        for neighbor, weight in neighbors:
            edge = g.edges[(1, neighbor)]
            neighbor_node = g.vertices[neighbor]
            
            # Highlight edge being considered
            self.play(edge.animate.set_color(RED).set_stroke_width(8))
            self.wait(0.3)
            
            # Update distance
            new_dist_text = Text(f"d({neighbor}) = {weight}", font_size=20, color=GREEN)
            new_dist_text.move_to(distance_panel[neighbor-1])
            self.play(Transform(distance_panel[neighbor-1], new_dist_text))
            self.wait(0.3)
            
            # Reset edge color
            self.play(edge.animate.set_color(WHITE).set_stroke_width(4))
            self.wait(0.2)
        
        # Step 3: Select node 2 (smallest distance)
        self.play(start_node.animate.set_color(BLUE))  # Mark as processed
        self.play(g.vertices[2].animate.set_color(YELLOW))
        self.wait(0.5)
        
        # Process neighbors of node 2
        node2_neighbors = [(3, 10), (4, 15)]
        for neighbor, weight in node2_neighbors:
            edge = g.edges[(2, neighbor)]
            neighbor_node = g.vertices[neighbor]
            
            self.play(edge.animate.set_color(RED).set_stroke_width(8))
            self.wait(0.3)
            
            # Update distance if better
            if neighbor == 3:  # Keep existing distance (9 < 10)
                new_dist_text = Text(f"d(3) = 9 (unchanged)", font_size=20, color=ORANGE)
            else:
                new_dist_text = Text(f"d(4) = 15", font_size=20, color=GREEN)
            
            new_dist_text.move_to(distance_panel[neighbor-1])
            self.play(Transform(distance_panel[neighbor-1], new_dist_text))
            self.wait(0.3)
            
            self.play(edge.animate.set_color(WHITE).set_stroke_width(4))
            self.wait(0.2)
        
        # Continue with more steps...
        self.play(g.vertices[2].animate.set_color(BLUE))
        self.play(g.vertices[3].animate.set_color(YELLOW))
        self.wait(0.5)
        
        # Show final shortest path
        shortest_path_edges = [(1, 2), (2, 4), (4, 5)]
        for edge in shortest_path_edges:
            edge_obj = g.edges[edge]
            self.play(edge_obj.animate.set_color(YELLOW).set_stroke_width(8))
            self.wait(0.5)
        
        # Final summary
        summary = Text("Shortest Path Found!", font_size=28, color=GREEN)
        summary.next_to(title, DOWN)
        self.play(Write(summary))
        self.wait(2)
        
        # Clean up
        self.play(FadeOut(VGroup(title, summary, g, distance_panel)))
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
        """Make the actual API request to OpenRouter"""
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "http://localhost:5173",
                            "X-Title": "TMAS Chatbot"
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "max_tokens": 4000,
                            "temperature": 0.7
                        },
                        timeout=120.0  # Increased from 60.0 to match main.py timeout
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"API request failed: {response.status_code} - {response.text}")
                    
                    return response.json()
                    
            except httpx.TimeoutException:
                if attempt < max_retries:
                    print(f"API request timed out, retrying... (attempt {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise Exception("API request timed out after all retries")
            except Exception as e:
                if attempt < max_retries:
                    print(f"API request failed, retrying... (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def _parse_response(self, api_response: Dict[str, Any]) -> Tuple[str, str]:
        """Parse the API response to extract explanation and Manim code"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            print(f"[AIService] Raw API response length: {len(content)}")
            print(f"[AIService] Raw API response preview: {content[:200]}...")

            # Use regex to extract the first python code block
            code_match = re.search(r"```python(.*?)(```|$)", content, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                explanation = content.split("```python")[0].strip()
                print(f"[AIService] Found code block, code length: {len(code)}")
                print(f"[AIService] Code preview: {code[:100]}...")
                print(f"[AIService] Explanation length: {len(explanation)}")
                return explanation, code
            else:
                # No code block found, return entire response as explanation
                print(f"[AIService] No code block found in response")
                return content.strip(), ""
        except Exception as e:
            print(f"[AIService] Error parsing response: {str(e)}")
            raise Exception(f"Failed to parse API response: {str(e)}")
    
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
                    f"{self.base_url}/chat/completions",
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