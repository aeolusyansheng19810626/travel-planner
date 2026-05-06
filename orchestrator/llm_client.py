"""
LLM client with fallback mechanism for Orchestrator
"""
from groq import Groq
import os
from typing import Optional, List, Dict, Any

# Model fallback list (from best to fastest)
MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b"
]

class GroqClientWithFallback:
    """Groq client with automatic model fallback"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.models = MODELS.copy()
        self.last_model: Optional[str] = None
    
    def chat_completion(
        self,
        messages: List,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Groq with automatic fallback to next model if current fails
        """
        if not self.client:
            raise ValueError("Groq client not initialized (missing API key?)")
        
        errors = []
        for model in self.models:
            try:
                request_kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if response_format:
                    request_kwargs["response_format"] = response_format

                response = self.client.chat.completions.create(**request_kwargs)
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("empty response content")
                self.last_model = model
                return content
            except Exception as e:
                print(f"Model {model} failed: {e}, trying next...")
                errors.append(f"{model}: {str(e)}")
                continue
        
        # All models failed
        raise RuntimeError(f"All models failed. Details: {'; '.join(errors)}")

# Made with Bob
