"""
Timeout and retry utilities for API requests.
"""
import asyncio
import time
from typing import Any, Callable, TypeVar, Optional
from functools import wraps
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class TimeoutConfig:
    """Configuration for timeout handling."""
    
    def __init__(
        self,
        request_timeout: float = 60.0,
        operation_timeout: float = 120.0,
        chunk_timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.request_timeout = request_timeout
        self.operation_timeout = operation_timeout
        self.chunk_timeout = chunk_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

def with_timeout(config: Optional[TimeoutConfig] = None):
    """
    Decorator to add timeout handling to async functions.
    
    Args:
        config: Timeout configuration (uses defaults if None)
    """
    if config is None:
        config = TimeoutConfig()
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=config.operation_timeout
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"Function {func.__name__} timed out after {config.operation_timeout}s",
                    extra={"extra_fields": {
                        "function": func.__name__,
                        "timeout": config.operation_timeout,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }}
                )
                raise asyncio.TimeoutError(f"Operation timed out after {config.operation_timeout} seconds")
        
        return wrapper
    return decorator

async def with_retry(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> T:
    """
    Execute a function with retry logic.
    
    Args:
        func: The async function to execute
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay after each retry
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of the function call
        
    Raises:
        The last exception encountered if all retries fail
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(
                f"Executing {func.__name__} (attempt {attempt + 1}/{max_retries + 1})",
                extra={"extra_fields": {
                    "function": func.__name__,
                    "attempt": attempt + 1,
                    "max_attempts": max_retries + 1
                }}
            )
            
            return await func(*args, **kwargs)
            
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {current_delay}s",
                    extra={"extra_fields": {
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "error": str(e),
                        "retry_delay": current_delay
                    }}
                )
                
                await asyncio.sleep(current_delay)
                current_delay *= backoff_factor
            else:
                logger.error(
                    f"All {max_retries + 1} attempts failed for {func.__name__}",
                    extra={"extra_fields": {
                        "function": func.__name__,
                        "total_attempts": max_retries + 1,
                        "final_error": str(e)
                    }}
                )
    
    # If we get here, all retries failed
    raise last_exception

class StreamTimeoutMonitor:
    """Monitor for streaming operations with timeout protection."""
    
    def __init__(self, chunk_timeout: float = 30.0):
        self.chunk_timeout = chunk_timeout
        self.last_activity = time.time()
        self.total_chunks = 0
        
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = time.time()
        self.total_chunks += 1
        
    def check_timeout(self) -> bool:
        """
        Check if the stream has timed out.
        
        Returns:
            True if timed out, False otherwise
        """
        current_time = time.time()
        elapsed = current_time - self.last_activity
        
        if elapsed > self.chunk_timeout:
            logger.warning(
                "Stream timeout detected",
                extra={"extra_fields": {
                    "elapsed_time": elapsed,
                    "timeout_threshold": self.chunk_timeout,
                    "total_chunks_received": self.total_chunks
                }}
            )
            return True
            
        return False
        
    def get_stats(self) -> dict:
        """Get monitoring statistics."""
        return {
            "total_chunks": self.total_chunks,
            "last_activity": self.last_activity,
            "elapsed_since_last": time.time() - self.last_activity,
            "timeout_threshold": self.chunk_timeout
        }