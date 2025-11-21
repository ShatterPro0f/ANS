"""
LLM client utilities for the ANS application.

This module provides functions for interacting with the Ollama LLM client,
including automatic retry logic with exponential backoff.
"""
import time
from typing import Optional, Any, Callable

from ans.utils.constants import DEFAULT_MAX_RETRIES


def generate_with_retry(
    client: Any,
    model: str,
    prompt: str,
    temperature: float = 0.7,
    max_retries: int = DEFAULT_MAX_RETRIES,
    log_callback: Optional[Callable[[str], None]] = None,
    error_callback: Optional[Callable[[str], None]] = None
) -> Optional[Any]:
    """Generate LLM response with automatic retry logic.
    
    Args:
        client: Ollama client instance
        model: Model name (e.g., 'gemma3:12b')
        prompt: Prompt text to send to LLM
        temperature: Temperature setting for response creativity
        max_retries: Maximum number of retry attempts
        log_callback: Optional callback for logging messages
        error_callback: Optional callback for error notifications
    
    Returns:
        Generator/Iterator with streamed response, or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            if client is None:
                if log_callback:
                    log_callback("Error: LLM client is None")
                return None
            
            stream = client.generate(
                model=model,
                prompt=prompt,
                stream=True,
                options={'temperature': temperature}
            )
            
            if not hasattr(stream, '__iter__'):
                if log_callback:
                    log_callback("Error: LLM response is not iterable")
                return None
            
            return stream
        
        except Exception as e:
            attempt_num = attempt + 1
            if log_callback:
                log_callback(f"LLM connection attempt {attempt_num}/{max_retries} failed: {str(e)}")
            
            if attempt_num < max_retries:
                # Wait before retry (exponential backoff: 1s, 2s, 4s)
                time.sleep(2 ** attempt)
            else:
                error_msg = f"Failed to connect to LLM after {max_retries} attempts: {str(e)}"
                if log_callback:
                    log_callback(error_msg)
                if error_callback:
                    error_callback(error_msg)
                return None


def test_llm_connection(
    client: Any,
    model: str = "gemma3:12b",
    log_callback: Optional[Callable[[str], None]] = None
) -> bool:
    """Test LLM connection with a simple prompt.
    
    Args:
        client: Ollama client instance
        model: Model name to test
        log_callback: Optional callback for logging messages
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        if client is None:
            if log_callback:
                log_callback("Error: LLM client is None")
            return False
        
        response = client.generate(model=model, prompt='Test.')
        
        if log_callback:
            log_callback(f"LLM connection successful ({model})")
        
        return True
    
    except Exception as e:
        if log_callback:
            log_callback(f"LLM connection failed: {str(e)}")
        return False
