"""
Pydantic models and schemas for API requests and responses.
"""
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class GPTModelEnum(str, Enum):
    """Available GPT models."""
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_O_MINI = "gpt-4o-mini"


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check Schemas
class HealthResponse(BaseResponse):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")


# GPT Query Schemas
class GPTQueryRequest(BaseModel):
    """Request model for GPT queries."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="The query text to send to the GPT model",
        examples=[
            "What is artificial intelligence?",
            "Explain machine learning in simple terms",
            "Write a Python function to calculate fibonacci numbers"
        ]
    )
    model: Optional[GPTModelEnum] = Field(
        default=None,
        description="GPT model to use (if not specified, uses default: gpt-4o-mini)",
        examples=["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"]
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 to 2.0). Lower values = more focused, higher values = more creative",
        examples=[0.3, 0.7, 1.0]
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=4000,
        description="Maximum number of tokens to generate (if not specified, uses default: 1000)",
        examples=[100, 500, 1000]
    )
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Simple Question",
                    "description": "A basic question to GPT",
                    "value": {
                        "query": "What is artificial intelligence?"
                    }
                },
                {
                    "summary": "Advanced Query with Parameters",
                    "description": "Query with model and parameter customization",
                    "value": {
                        "query": "Explain quantum computing in simple terms",
                        "model": "gpt-4o-mini",
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                },
                {
                    "summary": "Creative Writing",
                    "description": "Creative task with higher temperature",
                    "value": {
                        "query": "Write a short poem about artificial intelligence",
                        "model": "gpt-4o-mini",
                        "temperature": 0.9,
                        "max_tokens": 200
                    }
                }
            ]
        }
    }


class GPTQueryResponse(BaseResponse):
    """Response model for GPT queries."""
    response: str = Field(
        ...,
        description="The response from the GPT model"
    )
    model_used: str = Field(
        ...,
        description="The GPT model that was used"
    )
    tokens_used: Optional[int] = Field(
        None,
        description="Number of tokens used in the response"
    )
    processing_time: Optional[float] = Field(
        None,
        description="Processing time in seconds"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "timestamp": "2024-01-01T12:00:00",
                "response": "Quantum computing is a type of computation that harnesses quantum mechanics...",
                "model_used": "gpt-3.5-turbo",
                "tokens_used": 150,
                "processing_time": 2.34
            }
        }
    }


# Error Schemas
class ErrorDetail(BaseModel):
    """Error detail model."""
    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "timestamp": "2024-01-01T12:00:00",
                "error": "Validation error",
                "details": [
                    {
                        "type": "value_error",
                        "message": "Query cannot be empty",
                        "field": "query"
                    }
                ]
            }
        }
    }


# System Info Schemas
class SystemInfo(BaseResponse):
    """System information response."""
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment")
    docs_url: str = Field(..., description="Documentation URL")
    health_url: str = Field(..., description="Health check URL")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "timestamp": "2024-01-01T12:00:00",
                "service": "GPT Query API",
                "version": "1.0.0",
                "environment": "development",
                "docs_url": "/docs",
                "health_url": "/api/v1/health"
            }
        }
    }


# Streaming-specific schemas
class StreamChunkType(str, Enum):
    """Types of streaming chunks."""
    START = "start"
    CONTENT = "content"
    END = "end"
    ERROR = "error"


class StreamStartData(BaseModel):
    """Initial streaming metadata."""
    type: Literal["start"]
    model: str
    timestamp: float


class StreamContentData(BaseModel):
    """Content chunk from streaming response."""
    type: Literal["content"]
    chunk: str
    accumulated_length: int


class StreamEndData(BaseModel):
    """Final streaming metadata."""
    type: Literal["end"]
    full_response: str
    model_used: str
    tokens_used: int
    processing_time: float
    finish_reason: str


class StreamErrorData(BaseModel):
    """Error information in streaming."""
    type: Literal["error"]
    error: str
    timestamp: str


# WebSocket request schema
class WebSocketQueryRequest(BaseModel):
    """WebSocket query request schema."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="The query text to send to the GPT model via WebSocket"
    )
    model: Optional[str] = Field(
        default=None,
        description="GPT model to use (optional)"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (optional)"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=4000,
        description="Maximum tokens to generate (optional)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Simple WebSocket Query",
                    "description": "Basic query via WebSocket",
                    "value": {
                        "query": "What is artificial intelligence?",
                        "model": "gpt-4o-mini",
                        "temperature": 0.7
                    }
                }
            ]
        }
    }