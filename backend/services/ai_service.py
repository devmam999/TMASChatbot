"""
AI service for communicating with Anthropic Claude API
Handles text processing, generates explanations and Manim code
"""
import httpx
import json
import re
import base64
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from utils.config import settings
from google import genai
from google.genai import types


class AIService:
    """Service for interacting with Anthropic Claude API"""
    
    def __init__(self):
        self.claude_api_key = settings.ANTHROPIC_API_KEY
        self.claude_model = settings.ANTHROPIC_MODEL
        
        self.gemini_api_key =  settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL

        if not self.claude_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
    
    async def generate_response(
        self, 
        text: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Generate AI response with explanation (Gemini) and Manim code (Claude).
        Returns explanation even if Manim code generation fails.
        
        Args:
            text: User's text input
            
        Returns:
            Tuple of (explanation, manim_code)
        """
        if not text:
            raise ValueError("No input provided for AI request")

        try:
            # 1. Build Gemini prompt
            gemini_prompt = self._build_explanation_prompt(text)
            # 2. Get explanation from Gemini
            explanation = await self._get_gemini_explanation(gemini_prompt)

        except Exception as e:
            raise Exception(f"Failed to generate explanation: {str(e)}")

        manim_code = None
        try:
            # 3. Build Claude prompt using Gemini explanation
            claude_prompt = self._build_manim_prompt(text, explanation)
            # 4. Prepare messages for Claude
            messages = self._prepare_messages(claude_prompt, None)
            # 5. Get Manim code from Claude
            response = await self._make_api_request(messages)
            _, manim_code = self._parse_response(response)

        except Exception as e:
            # Log the error, but still return the explanation
            print(f"Claude API failed: {str(e)}")

        return explanation, manim_code
    
    # async def generate_simple_response(self, prompt: str) -> Tuple[str, str]:
    #     """
    #     Generate a simple AI response without requiring Manim code
        
    #     Args:
    #         prompt: Simple text prompt
            
    #     Returns:
    #         Tuple of (explanation, "") - no Manim code
    #     """
    #     try:
    #         messages = [
    #             {
    #                 "role": "system",
    #                 "content": "You are a helpful educational assistant. Provide clear, concise explanations."
    #             },
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             }
    #         ]
            
    #         response = await self._make_api_request(messages)
    #         content = response["choices"][0]["message"]["content"]
            
    #         return content.strip(), ""  # Return explanation only, no Manim code
            
    #     except Exception as e:
    #         raise Exception(f"Failed to generate simple AI response: {str(e)}")
    
#     async def generate_simple_animation_response(self, prompt: str) -> Tuple[str, str]:
#         """
#         Generate a simple response with basic animation code that works on limited environments
        
#         Args:
#             prompt: User's question
            
#         Returns:
#             Tuple of (explanation, simple_animation_code)
#         """
#         try:
#             messages = [
#                 {
#                     "role": "system",
#                     "content": """You are a helpful educational assistant. When asked to explain concepts, provide:
# 1. A clear explanation (2-3 sentences)
# 2. Simple Manim animation code that specifically demonstrates the concept being asked about

# CRITICAL: The animation MUST be directly related to the user's question. Do not create generic animations.

# Use only basic Manim features that work in limited environments:
# - Basic shapes (Circle, Square, Rectangle, Triangle)
# - Text and MathTex
# - Transformations (Create, FadeIn, FadeOut, MoveTo)
# - Simple colors (RED, BLUE, GREEN, YELLOW, WHITE)

# Avoid complex features like:
# - LaTeX equations
# - Custom fonts
# - Complex animations
# - External files

# Keep animations under 10 seconds and make them directly relevant to the concept being explained.

# Examples:
# - If asked about sorting: Show elements being sorted step by step
# - If asked about graphs: Show nodes and edges being created
# - If asked about math: Show mathematical operations visually
# - If asked about physics: Show forces, motion, or energy concepts
# - If asked about algorithms: Show the algorithm working step by step"""
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ]
            
#             response = await self._make_api_request(messages)
#             content = response["choices"][0]["message"]["content"]
            
#             # Split into explanation and code
#             parts = content.split("```python")
#             if len(parts) >= 2:
#                 explanation = parts[0].strip()
#                 code_part = parts[1].split("```")[0].strip()
#                 return explanation, code_part
#             else:
#                 return content.strip(), ""
                
#         except Exception as e:
#             raise Exception(f"Failed to generate simple animation response: {str(e)}")
    
    async def generate_quiz(self, explanation: str) -> List[Dict[str, Any]]:
        """
        Based on the given explanation, generate 3 practice quiz questions using Gemini.
        For each question, provide the question text, answer, and a hint.
        
        Args:
            explanation: The explanation text to base the quiz on
            
        Returns:
            List of dictionaries, each containing a question, answer, and hint
        """
        try:
            prompt = (

                f"You are an expert educator. Based on the following explanation, generate EXACTLY 3 multiple choice practice quiz questions that are SPECIFICALLY about the topic discussed.\n"
                f"Each question must be directly related to the concept explained above.\n"
                f"For each question, provide the output in **strict JSON format** as a list of objects with these keys:\n"
                f"- 'question': the question text\n"
                f"- 'options': a dictionary with keys 'A', 'B', 'C', 'D' and their respective option text\n"
                f"- 'correctAnswer': the correct letter ('A', 'B', 'C', or 'D')\n"
                f"- 'explanation': a brief explanation of why this answer is correct\n"
                f"- 'hint': a helpful hint\n"
                f"Do not include any extra text, comments, or formatting. Only output valid JSON.\n"
                f"\nTopic to create questions about:\n{explanation}"

            )

            # Use Gemini to generate quiz
            client = genai.Client(api_key=self.gemini_api_key)
            model = self.gemini_model

            parts = [types.Part.from_text(text=prompt)]
            contents = [
                types.Content(
                    role="user",
                    parts=parts,
                ),
            ]

            def run_gemini():
                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )
                return response.text

            response_text = await asyncio.to_thread(run_gemini)

            # Parse the response into quiz format

            # quiz = self._parse_gemini_quiz_response(response_text)
            cleaned = re.sub(r"^```json|```$", "", response_text.strip(), flags=re.MULTILINE).strip()

            # 2. Parse into Python object
            quiz = json.loads(cleaned)
            return quiz

        except Exception as e:
            print(f"Failed to generate quiz with Gemini: {str(e)}")
            # Return fallback questions if Gemini fails
            return self._create_fallback_questions(explanation)
        
    

    # def _parse_gemini_quiz_response(self, response_text: str) -> List[Dict[str, Any]]:
    #     """
    #     Parse the Gemini response into quiz questions format
        
    #     Args:
    #         response_text: Raw response text from Gemini
            
    #     Returns:
    #         List of dictionaries with question, answer, and hint
    #     """
    #     try:
    #         print(f"Raw Gemini quiz response: {type(response_text)}...")  # Debug log
            
    #         # Try multiple parsing strategies
    #         questions = []
            
    #         # Strategy 1: Look for structured format with "Question:" markers
    #         if "Question:" in response_text:
    #             parts = response_text.split("Question:")
    #             if len(parts) > 1:
    #                 for i, part in enumerate(parts[1:], 1):
    #                     try:
    #                         question_data = self._parse_structured_question(part)
    #                         if question_data:
    #                             questions.append(question_data)
    #                     except Exception as e:
    #                         print(f"Failed to parse structured question {i}: {e}")
    #                         continue
            
    #         # Strategy 2: Look for numbered questions (Q1, Q2, Q3)
    #         if not questions and any(marker in response_text for marker in ["Q1", "Q2", "Q3", "Question 1", "Question 2", "Question 3"]):
    #             questions = self._parse_numbered_questions(response_text)
            
    #         # Strategy 3: Look for any pattern that might be questions
    #         if not questions:
    #             questions = self._parse_flexible_format(response_text)
            
    #         # If still no questions, create fallback
    #         if not questions:
    #             print("All parsing strategies failed, using fallback questions")
    #             questions = self._create_fallback_questions(response_text)
            
    #         # Ensure exactly 3 questions
    #         questions = self._ensure_three_questions(questions)
            
    #         print(f"Successfully parsed {len(questions)} questions")
    #         return questions
            
    #     except Exception as e:
    #         print(f"Failed to parse Gemini quiz response: {e}")
    #         print("Using fallback questions due to parsing error")
    #         return self._create_fallback_questions(response_text)
    
    def _build_explanation_prompt(self, text):
        # Build a prompt for Gemini (focus on explanation only)
        base_prompt = """
You are an expert educator specializing in clear, structured explanations.

CRITICAL: You MUST format your response with exactly the structure shown below. Do not deviate from this format.

REQUIRED OUTPUT STRUCTURE:
1. Start with **Background** section
2. Follow with **Core Idea** section  
3. Then **How It Works** section
4. End with **Real-World Relevance** section
5. Each section must start with a **bolded heading** exactly as shown
6. Leave TWO blank lines after each section heading
7. Leave TWO blank lines after each section content

SECTION REQUIREMENTS:
- Each section: 2-4 short sentences
- Each section: Include one concrete example or analogy
- Use simple, accessible language
- Define technical terms in plain language

EXAMPLE FORMAT (follow this EXACTLY):
**Background**

[2-4 sentences with one example about what the concept is and its history]

**Core Idea** 

[2-4 sentences with one example explaining the main principle]

**How It Works**

[2-4 sentences with one example showing the mechanism or process]

**Real-World Relevance**

[2-4 sentences with one example of practical applications and why it matters]

EXAMPLE OUTPUT:
**Background**

Ohm's Law describes the relationship between voltage (V), current (I), and resistance (R) in electrical circuits. It was formulated by Georg Ohm and is fundamental for circuit analysis. Example: A 10V battery across a 5Ω resistor produces 2A of current.

**Core Idea**

Current through a conductor is proportional to voltage and inversely proportional to resistance. The mathematical relationship is V = I × R. Analogy: voltage is water pressure, current is flow rate, resistance is pipe narrowness.

**How It Works**

Engineers measure any two quantities and calculate the third using V = I × R. This works for most materials under constant conditions but not for nonlinear components like diodes. Example: Doubling voltage across a resistor doubles the current if resistance stays constant.

**Real-World Relevance**

Ohm's Law is essential for designing electronic devices, from LED circuits to power supplies. It prevents component damage by ensuring proper current flow. Example: Calculating resistor size for LED protection uses (V_source - V_LED) / desired_current.

IMPORTANT: Follow this exact format with bolded headings and TWO blank lines between sections. Do not write a continuous paragraph.
"""
        if text:
            return f"{base_prompt}\n\nUSER INPUT:\nText: {text}\n\nPlease provide an explanation for this concept."
        else:
            raise ValueError("Text input must be provided")
        
    def _build_manim_prompt(self, text, explanation):
        # Build a prompt for Claude (focus on Manim code only)
        """Build the prompt based on input type"""
        base_prompt = f"""
You are an expert educator and Python programmer specializing in creating educational animations using the Manim library.

Your task is to:
1. Write Python code using Manim to create an animation that visualizes the concept, 
with this explaination as context; Explanation:\n{explanation}\n\n
                
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
        
        if text:
            return f"{base_prompt}\n\nUSER INPUT:\nText: {text}\n\nPlease create a Manim animation for this concept."
        else:
            raise ValueError("Text input must be provided")
    
    async def _get_gemini_explanation(self, prompt: str) -> str:
        """Get explanation from Gemini"""
        client = genai.Client(api_key=self.gemini_api_key)
        model = self.gemini_model

        parts = [types.Part.from_text(text=prompt)]

        contents = [
            types.Content(
                role="user",
                parts=parts,
            ),
        ]

        def run_gemini():
            response = client.models.generate_content(
                model=model,
                contents=contents
            )
            return response.text

        explanation = await asyncio.to_thread(run_gemini)
        return self._format_explanation_response(explanation)
    
    def _format_explanation_response(self, response_text: str) -> str:
        """
        Format Gemini response to ensure proper section structure with line breaks.
        If the response already has proper formatting, enhance it with proper spacing.
        If it's a blob, attempt to structure it into sections.
        """
        # Check if response already has proper section formatting
        if "**Background**" in response_text and "**Core Idea**" in response_text:
            # Enhance existing formatting with proper line breaks
            return self._enhance_existing_formatting(response_text)
        
        # If it's a blob, try to structure it
        try:
            # Split into sentences
            sentences = [s.strip() for s in response_text.split('.') if s.strip()]
            
            # Create structured response
            sections = {
                "**Background**": [],
                "**Core Idea**": [],
                "**How It Works**": [],
                "**Real-World Relevance**": []
            }
            
            # Distribute sentences across sections
            total_sentences = len(sentences)
            sentences_per_section = max(2, total_sentences // 4)
            
            current_section = 0
            section_names = list(sections.keys())
            
            for i, sentence in enumerate(sentences):
                if sentence and not sentence.endswith('.'):
                    sentence += '.'
                
                if current_section < len(section_names):
                    sections[section_names[current_section]].append(sentence)
                    
                    # Move to next section if current one has enough sentences
                    if len(sections[section_names[current_section]]) >= sentences_per_section and current_section < len(section_names) - 1:
                        current_section += 1
            
            # Build formatted response with proper spacing
            formatted_response = ""
            for section_name, section_sentences in sections.items():
                if section_sentences:
                    formatted_response += f"{section_name}\n\n"
                    formatted_response += " ".join(section_sentences) + "\n\n"
            
            return formatted_response.strip()
            
        except Exception as e:
            # If formatting fails, return original response
            print(f"Failed to format explanation response: {e}")
            return response_text
    
    def _enhance_existing_formatting(self, response_text: str) -> str:
        """
        Enhance existing section formatting with proper line breaks.
        """
        import re
        
        # Split by section headers
        sections = re.split(r'(\*\*[^*]+\*\*)', response_text)
        
        formatted_response = ""
        for i, part in enumerate(sections):
            part = part.strip()
            if not part:
                continue
                
            # If this is a section header (starts with **)
            if part.startswith('**') and part.endswith('**'):
                formatted_response += f"{part}\n\n"
            else:
                # This is section content
                formatted_response += f"{part}\n\n"
        
        return formatted_response.strip()
    
#     def _build_prompt(self, text: Optional[str], image_path: Optional[str]) -> str:
#         """Build the prompt based on input type"""
#         base_prompt = """
# You are an expert educator and Python programmer specializing in creating educational animations using the Manim library.

# Your task is to:
# 1. Provide a clear, educational explanation of the concept
# 2. Write Python code using Manim to create an animation that visualizes the concept

# IMPORTANT REQUIREMENTS:
# - The Manim code must be complete and executable
# - Use the latest Manim syntax (v0.19.0+)
# - The animation should be educational and visually appealing
# - Keep the animation duration reasonable (10-30 seconds for substantial content)
# - Include multiple sequential animation steps (5–10 minimum for complex topics)
# - Use clear colors (RED, GREEN, BLUE) and readable text (TEXT with font size 24+)
# - Include proper imports and scene class definition (from manim import *, Scene subclasses, etc.)
# - Show step-by-step processes with visual transitions
# - Use animations like Create(), Write(), Transform(), MoveTo(), etc.
# - Make sure animations are engaging and educational
# - Use pauses (wait()) between important steps so the viewer can follow the reasoning

# EDUCATIONAL STRUCTURE:

# Each animation should include:

# - Title introduction — show the concept name in a large, readable font

# - Step-by-step buildup — introduce elements gradually and explain each stage visually

# - Highlighting important parts — use color changes, scaling, and highlighting to show focus

# - Transitions between states — avoid abrupt changes; show the process evolving

# - Summary or conclusion — recap the key idea at the end with a short final statement


# OUTPUT FORMAT
# Educational Explanation — 2–3 paragraphs, simple and clear, describing the concept and its real-world relevance

# Complete Manim Python Code — in a code block, ready to run

# Example python code structure:

# from manim import *

# class ConceptAnimation(Scene):
#     def construct(self):
#         # Step 1: Title
#         title = Text("Concept Name", font_size=36, color=BLUE)
#         self.play(Write(title))
#         self.wait(1)

#         # Step 2: First visual setup
#         subtitle = Text("Step 1: Initial State", font_size=28).next_to(title, DOWN)
#         self.play(Write(subtitle))
#         self.wait(1)

#         # Step 3: Create objects
#         circle = Circle(color=RED).shift(LEFT*2)
#         square = Square(color=GREEN).shift(RIGHT*2)
#         self.play(Create(circle), Create(square))
#         self.wait(1)

#         # Step 4: Transform objects
#         self.play(circle.animate.scale(1.5).set_color(PURPLE),
#                   square.animate.rotate(PI/4).set_color(ORANGE))
#         self.wait(1)

#         # Step 5: Connect elements
#         line = Line(circle.get_center(), square.get_center(), color=YELLOW)
#         self.play(Create(line))
#         self.wait(1)

#         # Step 6: Final message
#         final_text = Text("Concept Complete!", font_size=30, color=GREEN).shift(DOWN*2)
#         self.play(Write(final_text))
#         self.wait(2)

#         # Step 7: Fade out
#         self.play(FadeOut(VGroup(title, subtitle, circle, square, line, final_text)))
#         self.wait(0.5)
# ```
# """
        
#         if text and image_path:
#             return f"{base_prompt}\n\nUSER INPUT:\nText: {text}\nImage: [User uploaded an image]\n\nPlease analyze both the text and image to provide a comprehensive explanation and animation."
#         elif text:
#             return f"{base_prompt}\n\nUSER INPUT:\nText: {text}\n\nPlease provide an explanation and create a Manim animation for this concept."
#         elif image_path:
#             return f"{base_prompt}\n\nUSER INPUT:\nImage: [User uploaded an image]\n\nPlease analyze the image content and provide an explanation with a relevant Manim animation."
#         else:
#             raise ValueError("Either text or image must be provided")
    
    def _prepare_messages(self, prompt: str) -> list:
        """Prepare messages for the API request"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert educator and Python programmer specializing in Manim animations."
            }
        ]
        
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
                            "x-api-key": self.claude_api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                            "HTTP-Referer": "http://localhost:5173",
                            "X-Title": "TMAS Chatbot"
                        },
                        json={
                            "model": self.claude_model,
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
                        "Authorization": f"Bearer {self.claude_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                                                    "X-Title": "TMAS Chatbot"
                    },
                    json={
                        "model": self.claude_model,
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

    # def _parse_structured_question(self, part: str) -> Optional[Dict[str, Any]]:
    #     """Parse a structured question part"""
    #     try:
    #         question_text = ""
    #         options = {"A": "", "B": "", "C": "", "D": ""}
    #         correct_answer = ""
    #         explanation = ""
    #         hint = ""
            
    #         lines = part.strip().split('\n')
    #         current_section = ""
            
    #         for line in lines:
    #             line = line.strip()
    #             if not line:
    #                 continue
                
    #             # Skip markdown separators and empty lines
    #             if line in ['---', '**', '']:
    #                 continue
                    
    #             if line.startswith("Options:"):
    #                 current_section = "options"
    #             elif line.startswith("Correct Answer:"):
    #                 current_section = "correct"
    #             elif line.startswith("Explanation:"):
    #                 current_section = "explanation"
    #             elif line.startswith("Hint:"):
    #                 current_section = "hint"
    #             elif line.startswith("A)"):
    #                 options["A"] = line.replace("A)", "").strip()
    #             elif line.startswith("B)"):
    #                 options["B"] = line.replace("B)", "").strip()
    #             elif line.startswith("C)"):
    #                 options["C"] = line.replace("C)", "").strip()
    #             elif line.startswith("D)"):
    #                 options["D"] = line.replace("D)", "").strip()
    #             elif current_section == "correct" and line:
    #                 correct_answer = line.strip()
    #             elif current_section == "explanation" and line:
    #                 explanation = line.strip()
    #             elif current_section == "hint" and line:
    #                 hint = line.strip()
    #             elif not current_section and line and ('?' in line or line.startswith('Who') or line.startswith('What') or line.startswith('How') or line.startswith('Why') or line.startswith('Which') or line.startswith('When') or line.startswith('Where')):
    #                 question_text = line.strip()
            
    #         print(f"Parsed question data - Question: '{question_text}', Options: {options}, Correct: '{correct_answer}'")
            
    #         if question_text and correct_answer and any(options.values()):
    #             return {
    #                 "question": question_text,
    #                 "options": options,
    #                 "correctAnswer": correct_answer,
    #                 "explanation": explanation or "This is the correct answer based on the concept explained above.",
    #                 "hint": hint or "Think about the concept explained above."
    #             }
    #     except Exception as e:
    #         print(f"Failed to parse structured question: {e}")
        
    #     return None

    # def _parse_numbered_questions(self, content: str) -> List[Dict[str, Any]]:
    #     """Parse numbered questions (Q1, Q2, Q3)"""
    #     questions = []
    #     try:
    #         # Look for Q1, Q2, Q3 patterns
    #         for i in range(1, 4):
    #             q_marker = f"Q{i}"
    #             if q_marker in content:
    #                 # Simple parsing for numbered questions
    #                 questions.append({
    #                     "question": f"Question {i} about the concept",
    #                     "options": {
    #                         "A": "The main concept explained above",
    #                         "B": "A different topic",
    #                         "C": "Something unrelated", 
    #                         "D": "None of the above"
    #                     },
    #                     "correctAnswer": "A",
    #                     "explanation": "This concept is explained in the text above.",
    #                     "hint": "Review the explanation carefully"
    #                 })
    #     except Exception as e:
    #         print(f"Failed to parse numbered questions: {e}")
        
    #     return questions

    # def _parse_flexible_format(self, content: str) -> List[Dict[str, Any]]:
    #     """Parse any format that might contain questions"""
    #     questions = []
    #     try:
    #         # Look for any text that might be a question
    #         lines = content.split('\n')
    #         question_lines = []
            
    #         for line in lines:
    #             line = line.strip()
    #             if line and ('?' in line or line.startswith('What') or line.startswith('How') or line.startswith('Why')):
    #                 question_lines.append(line)
            
    #         # Create questions from found lines
    #         for i, q_line in enumerate(question_lines[:3]):
    #             questions.append({
    #                 "question": q_line,
    #                 "options": {
    #                     "A": "The concept from the explanation above",
    #                     "B": "A different topic",
    #                     "C": "Something unrelated",
    #                     "D": "None of the above"
    #                 },
    #                 "correctAnswer": "A",
    #                 "explanation": "This concept is explained in the text above.",
    #                 "hint": "Review the explanation carefully"
    #             })
    #     except Exception as e:
    #         print(f"Failed to parse flexible format: {e}")
        
    #     return questions

    # def _create_fallback_questions(self, explanation: str = "") -> List[Dict[str, Any]]:
    #     """Create fallback questions when parsing fails"""
    #     # Try to extract topic-specific information from the explanation
    #     topic_keywords = self._extract_topic_keywords(explanation)
        
    #     return [
    #         {
    #             "question": f"What is the main concept being explained about {topic_keywords.get('main_topic', 'this topic')}?",
    #             "options": {
    #                 "A": f"The {topic_keywords.get('main_topic', 'concept')} explained above",
    #                 "B": "A completely different topic",
    #                 "C": "Something unrelated",
    #                 "D": "None of the above"
    #             },
    #             "correctAnswer": "A",
    #             "explanation": f"The explanation focuses on {topic_keywords.get('main_topic', 'this specific concept')}.",
    #             "hint": f"Review the explanation about {topic_keywords.get('main_topic', 'the concept')} carefully"
    #         },
    #         {
    #             "question": f"Can you provide an example of {topic_keywords.get('main_topic', 'this concept')}?",
    #             "options": {
    #                 "A": f"Examples of {topic_keywords.get('main_topic', 'the concept')} from the explanation",
    #                 "B": "Random examples",
    #                 "C": "Opposite examples",
    #                 "D": "No examples available"
    #             },
    #             "correctAnswer": "A",
    #             "explanation": f"The explanation includes relevant examples of {topic_keywords.get('main_topic', 'this concept')}.",
    #             "hint": f"Look for specific examples of {topic_keywords.get('main_topic', 'the concept')} in the text"
    #         },
    #         {
    #             "question": f"What are the key points to remember about {topic_keywords.get('main_topic', 'this concept')}?",
    #             "options": {
    #                 "A": f"The main points about {topic_keywords.get('main_topic', 'the concept')} from the explanation",
    #                 "B": "Minor details only",
    #                 "C": "Unrelated information",
    #                 "D": "Nothing important"
    #             },
    #             "correctAnswer": "A",
    #             "explanation": f"Focus on the main concepts about {topic_keywords.get('main_topic', 'this topic')} explained.",
    #             "hint": f"Focus on the most important information about {topic_keywords.get('main_topic', 'the concept')}"
    #         }
    #     ]

    # def _ensure_three_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    #     """Ensure exactly 3 questions"""
    #     if len(questions) > 3:
    #         return questions[:3]
    #     elif len(questions) < 3:
    #         # Add fallback questions if we don't have 3
    #         while len(questions) < 3:
    #             questions.append({
    #                 "question": f"What is concept {len(questions) + 1} from the explanation?",
    #                 "options": {
    #                     "A": "The main concept explained above",
    #                     "B": "A different topic",
    #                     "C": "Something unrelated",
    #                     "D": "None of the above"
    #                 },
    #                 "correctAnswer": "A",
    #                 "explanation": "This concept is explained in the text above.",
    #                 "hint": "Review the explanation carefully"
    #             })
        
    #     return questions

    def _extract_topic_keywords(self, text: str) -> Dict[str, str]:
        """Extract simple topic keywords from a block of text for on-topic fallbacks.
        Heuristic approach: pick likely concept words (capitalized tokens, known algorithm terms),
        otherwise fall back to the first sentence head words.
        """
        try:
            if not text:
                return {"main_topic": "the concept"}
            snippet = text.strip().split("\n", 1)[0]
            first_sentence = re.split(r"[.!?]\s", snippet)[0]
            # Prefer known CS/math keywords if present
            known_terms = [
                "Binary Search Tree", "BST", "Dijkstra", "Dijkstra's Algorithm", "A*", "A* Search",
                "Merge Sort", "Quick Sort", "Sorting", "Graph", "DFS", "BFS", "Dynamic Programming",
                "Neural Network", "Gradient Descent", "Backpropagation", "Matrix", "Vector",
                "Probability", "Bayes", "Regression", "Classification", "KNN", "SVM",
            ]
            lowered = text.lower()
            for term in known_terms:
                if term.lower() in lowered:
                    return {"main_topic": term}
            # Otherwise, collect capitalized multi-word phrases as candidates
            capitalized_words = re.findall(r"(?:[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})", first_sentence)
            if capitalized_words:
                return {"main_topic": capitalized_words[0]}
            # Fallback: first 3-4 meaningful words
            tokens = re.findall(r"[A-Za-z0-9]+", first_sentence)
            tokens = [t for t in tokens if len(t) > 2]
            if tokens:
                topic = " ".join(tokens[:4])
                return {"main_topic": topic}
            return {"main_topic": "the concept"}
        except Exception:
            return {"main_topic": "the concept"}