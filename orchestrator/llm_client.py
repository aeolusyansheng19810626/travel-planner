"""
LLM client with fallback mechanism for Orchestrator
"""
from groq import Groq
import os
from typing import Optional, List

# Model fallback list (from best to fastest)
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b", 
    "qwen/qwen3-32b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant"
]

class GroqClientWithFallback:
    """Groq client with automatic model fallback"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.models = MODELS.copy()
    
    def chat_completion(self, messages: List, temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
        """
        Call Groq with automatic fallback to next model if current fails
        """
        if not self.client:
            return None
        
        for model in self.models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Model {model} failed: {e}, trying next...")
                continue
        
        # All models failed
        return None

# Made with Bob