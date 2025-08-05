"""
GPT service for handling OpenAI API interactions.
"""
import os
import time
import json
import asyncio
from typing import Dict, Optional, Tuple, AsyncGenerator
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.core.logging import get_logger
from app.models.schemas import GPTModelEnum

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class GPTServiceError(Exception):
    """Custom exception for GPT service errors."""
    pass


class GPTService:
    """Service for interacting with OpenAI's GPT models."""
    
    def __init__(self):
        """Initialize the GPT service."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise GPTServiceError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize OpenAI client with proper timeout and retry configuration
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=60.0,  # 60 seconds timeout for requests
            max_retries=3   # Retry failed requests up to 3 times
        )
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.default_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.default_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        logger.info(
            "GPT Service initialized",
            extra={"extra_fields": {
                "default_model": self.default_model,
                "max_tokens": self.default_max_tokens,
                "temperature": self.default_temperature
            }}
        )
    
    async def get_response(
        self,
        query: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, Dict]:
        """
        Get a response from the GPT model for the given query.
        
        Args:
            query: The user's query text
            model: The GPT model to use (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)
            
        Returns:
            Tuple of (response_text, metadata_dict)
            
        Raises:
            GPTServiceError: If there's an error communicating with the OpenAI API
        """
        start_time = time.time()
        
        # Use provided parameters or defaults
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        logger.info(
            "Sending query to GPT",
            extra={"extra_fields": {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "query_length": len(query)
            }}
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if not response.choices or not response.choices[0].message:
                raise GPTServiceError("No response received from GPT model")
            
            gpt_response = response.choices[0].message.content
            if not gpt_response:
                raise GPTServiceError("Empty response received from GPT model")
            
            processing_time = time.time() - start_time
            
            # Extract metadata
            metadata = {
                "model_used": model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "processing_time": processing_time,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(
                "Successfully received response from GPT",
                extra={"extra_fields": {
                    "processing_time": processing_time,
                    "tokens_used": metadata["tokens_used"],
                    "response_length": len(gpt_response)
                }}
            )
            
            return gpt_response.strip(), metadata
            
        except Exception as e:
            logger.error(
                "Error communicating with OpenAI API",
                extra={"extra_fields": {
                    "error": str(e),
                    "model": model,
                    "processing_time": time.time() - start_time
                }}
            )
            raise GPTServiceError(f"Failed to get response from GPT: {str(e)}")
    
    async def health_check(self) -> Dict:
        """
        Perform a health check on the GPT service.
        
        Returns:
            Dictionary with health status information
        """
        try:
            # Simple test query
            _, metadata = await self.get_response(
                "Hello", 
                max_tokens=10
            )
            return {
                "status": "healthy",
                "model": self.default_model,
                "last_response_time": metadata.get("processing_time")
            }
        except Exception as e:
            logger.error(f"GPT service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_streaming_response(
        self,
        query: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[Dict, None]:
        """
        Get a streaming response from the GPT model for the given query.
        
        Args:
            query: The user's query text
            model: The GPT model to use (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)
            
        Yields:
            Dictionary chunks with streaming data
            
        Raises:
            GPTServiceError: If there's an error communicating with the OpenAI API
        """
        start_time = time.time()
        
        # Use provided parameters or defaults
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        logger.info(
            "Starting streaming query to GPT",
            extra={"extra_fields": {
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "query_length": len(query)
            }}
        )
        
        try:
            # Create streaming request with proper timeout
            stream = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True,  # Enable streaming
                    timeout=90.0  # Individual request timeout
                ),
                timeout=120.0  # Overall operation timeout (2 minutes)
            )
            
            # Send initial metadata
            yield {
                "type": "start",
                "model": model,
                "timestamp": time.time()
            }
            
            full_response = ""
            total_tokens = 0
            chunk_count = 0
            last_chunk_time = time.time()
            
            # Process stream with timeout protection
            try:
                async for chunk in stream:
                    chunk_count += 1
                    current_time = time.time()
                    
                    # Check for chunk timeout (no data for 30 seconds)
                    if current_time - last_chunk_time > 30.0:
                        logger.warning("Stream chunk timeout detected, breaking")
                        break
                        
                    last_chunk_time = current_time
                    
                    # Handle content chunks
                    if chunk.choices and len(chunk.choices) > 0:
                        choice = chunk.choices[0]
                        if hasattr(choice, 'delta') and choice.delta and hasattr(choice.delta, 'content') and choice.delta.content:
                            content = choice.delta.content
                            full_response += content
                            
                            # Send content chunk
                            yield {
                                "type": "content",
                                "chunk": content,
                                "accumulated_length": len(full_response)
                            }
                    
                    # Handle token usage if available (usually only in final chunks)
                    if hasattr(chunk, 'usage') and chunk.usage and hasattr(chunk.usage, 'total_tokens'):
                        total_tokens = chunk.usage.total_tokens
                        
            except Exception as stream_error:
                logger.error(f"Error processing stream chunk: {stream_error}")
                # Continue to end processing gracefully
            
            processing_time = time.time() - start_time
            
            # Send completion metadata
            yield {
                "type": "end",
                "full_response": full_response,
                "model_used": model,
                "tokens_used": total_tokens if total_tokens > 0 else len(full_response.split()) * 1.3,  # Rough estimate if no usage data
                "processing_time": processing_time,
                "finish_reason": "stop",
                "chunks_received": chunk_count
            }
            
            logger.info(
                "Successfully completed streaming response from GPT",
                extra={"extra_fields": {
                    "processing_time": processing_time,
                    "tokens_used": total_tokens,
                    "response_length": len(full_response)
                }}
            )
            
        except asyncio.TimeoutError as e:
            processing_time = time.time() - start_time
            logger.error(
                "Timeout in streaming communication with OpenAI API",
                extra={"extra_fields": {
                    "error": "Request timeout after waiting too long",
                    "model": model,
                    "processing_time": processing_time,
                    "timeout_duration": "120 seconds"
                }}
            )
            
            # Send timeout error to stream
            yield {
                "type": "error",
                "error": "Request timed out. The AI model is taking too long to respond. Please try again with a shorter query.",
                "timestamp": time.time(),
                "error_type": "timeout"
            }
            
            raise GPTServiceError("Request timed out - AI model response took too long")
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            # Handle specific OpenAI errors
            if "rate_limit" in error_msg.lower():
                error_type = "rate_limit"
                user_message = "Rate limit exceeded. Please wait a moment and try again."
            elif "insufficient_quota" in error_msg.lower():
                error_type = "quota"
                user_message = "API quota exceeded. Please check your OpenAI account."
            elif "timeout" in error_msg.lower():
                error_type = "timeout"
                user_message = "Request timed out. Please try again with a shorter query."
            else:
                error_type = "general"
                user_message = "An error occurred while processing your request. Please try again."
            
            logger.error(
                "Error in streaming communication with OpenAI API",
                extra={"extra_fields": {
                    "error": error_msg,
                    "error_type": error_type,
                    "model": model,
                    "processing_time": processing_time
                }}
            )
            
            # Send user-friendly error to stream
            yield {
                "type": "error",
                "error": user_message,
                "timestamp": time.time(),
                "error_type": error_type
            }
            
            raise GPTServiceError(f"Failed to get streaming response from GPT: {user_message}")


# Global service instance
_gpt_service: Optional[GPTService] = None


async def get_gpt_service() -> GPTService:
    """
    Dependency injection function to get the GPT service instance.
    
    Returns:
        The GPT service instance
    """
    global _gpt_service
    if _gpt_service is None:
        _gpt_service = GPTService()
    return _gpt_service