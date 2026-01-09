"""AI Engine module for generating philosophical quotes using Google Gemini API."""

import os
import json
import re
from typing import Optional, Dict
from google import genai


class AIEngine:
    """Handles quote generation using Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3-flash-preview"):
        """
        Initialize the AI Engine.
        
        Args:
            api_key: Google Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model: Model name to use. Defaults to gemini-3-flash-preview.
        """
        # The client automatically gets the API key from GEMINI_API_KEY environment variable
        # But we can also pass it explicitly if provided
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set as environment variable")
        
        # Pass API key explicitly (or use genai.Client() if env var is set)
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def generate_quote(self, topic: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a philosophical quote.
        
        Args:
            topic: Optional topic or philosopher name. If None, generates random quote.
            
        Returns:
            Dictionary with 'quote', 'author', and 'context' keys.
        """
        if topic and topic.lower() != "random":
            prompt = f"""Generate a profound quote from {topic}, a famous Western philosopher. 
Return ONLY raw JSON (no markdown, no code blocks) with the following structure:
{{
  "quote": "the actual quote text",
  "author": "philosopher name",
  "context": "brief context about the quote or philosopher (1-2 sentences)"
}}"""
        else:
            prompt = """Generate a profound quote from a famous Western philosopher (e.g., Marcus Aurelius, Nietzsche, Seneca, Kant, Plato, Aristotle, Epictetus, Schopenhauer, Camus, Sartre).
Return ONLY raw JSON (no markdown, no code blocks) with the following structure:
{
  "quote": "the actual quote text",
  "author": "philosopher name",
  "context": "brief context about the quote or philosopher (1-2 sentences)"
}"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            # Get text from response (handles thought signatures automatically)
            text = response.text.strip() if hasattr(response, 'text') else str(response).strip()
            
            # Clean up the response - remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            text = text.strip()
            
            # Parse JSON
            quote_data = json.loads(text)
            
            # Validate required fields
            if not all(key in quote_data for key in ['quote', 'author', 'context']):
                raise ValueError("Missing required fields in AI response")
            
            return {
                'quote': quote_data['quote'],
                'author': quote_data['author'],
                'context': quote_data.get('context', '')
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating quote: {e}")
