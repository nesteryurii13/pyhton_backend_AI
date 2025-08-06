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
    GPT_4_O = "gpt-4o"  # Latest flagship model
    GPT_4_O_MINI = "gpt-4o-mini"
    O1_MINI = "o1-mini"  # Reasoning model (faster)
    O1 = "o1"  # Reasoning model (more capable)


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
        description="GPT model to use (if not specified, uses default from environment)",
        examples=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-mini"]
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
                    "summary": "Simple Question (Default Model)",
                    "description": "Basic question using default model from environment",
                    "value": {
                        "query": "What is artificial intelligence and how does it work?"
                    }
                },
                {
                    "summary": "GPT-4o - Complex Analysis",
                    "description": "Using latest GPT-4o for comprehensive analysis",
                    "value": {
                        "query": "Compare the environmental impact of electric vehicles vs gasoline cars, considering manufacturing, usage, and disposal phases.",
                        "model": "gpt-4o",
                        "temperature": 0.3,
                        "max_tokens": 600
                    }
                },
                {
                    "summary": "GPT-4o-mini - Code Generation",
                    "description": "Fast coding task with GPT-4o-mini",
                    "value": {
                        "query": "Write a Python function that implements binary search with error handling and comments.",
                        "model": "gpt-4o-mini",
                        "temperature": 0.1,
                        "max_tokens": 300
                    }
                },
                {
                    "summary": "o1-mini - Math & Reasoning",
                    "description": "Step-by-step reasoning with o1-mini",
                    "value": {
                        "query": "A train travels from City A to City B at 80 km/h and returns at 120 km/h. If the total journey takes 5 hours, what is the distance between the cities?",
                        "model": "o1-mini",
                        "temperature": 0.2,
                        "max_tokens": 400
                    }
                },
                {
                    "summary": "GPT-4-turbo - Creative Writing",
                    "description": "Creative task with higher temperature",
                    "value": {
                        "query": "Write a compelling short story about a data scientist who discovers that AI models are dreaming. Make it mysterious and thought-provoking.",
                        "model": "gpt-4-turbo",
                        "temperature": 0.8,
                        "max_tokens": 500
                    }
                },
                {
                    "summary": "o1 - Complex Problem Solving",
                    "description": "Advanced reasoning for complex problems",
                    "value": {
                        "query": "Design a sustainable city transportation system that reduces emissions by 70% while maintaining accessibility for all income levels. Consider costs, technology, and social impact.",
                        "model": "o1",
                        "temperature": 0.4,
                        "max_tokens": 800
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
                "timestamp": "2024-01-15T14:30:25.123456",
                "response": "Artificial Intelligence (AI) is a branch of computer science that focuses on creating systems capable of performing tasks that typically require human intelligence. These tasks include learning from data, recognizing patterns, making decisions, understanding natural language, and solving complex problems.\n\nAt its core, AI works by processing large amounts of data through sophisticated algorithms and mathematical models. Machine learning, a subset of AI, enables systems to improve their performance automatically through experience without being explicitly programmed for every scenario.\n\nModern AI applications include virtual assistants like Siri and Alexa, recommendation systems on Netflix and Amazon, autonomous vehicles, medical diagnosis tools, and language models like ChatGPT. The field continues to evolve rapidly, with recent breakthroughs in deep learning and neural networks opening new possibilities for human-AI collaboration.",
                "model_used": "gpt-4o",
                "tokens_used": 187,
                "processing_time": 1.82
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
                    "summary": "Real-time Chat with GPT-4o",
                    "description": "Interactive conversation via WebSocket",
                    "value": {
                        "query": "Explain machine learning in simple terms that a beginner can understand",
                        "model": "gpt-4o",
                        "temperature": 0.6,
                        "max_tokens": 400
                    }
                },
                {
                    "summary": "Code Review with GPT-4o-mini",
                    "description": "Fast code analysis via WebSocket",
                    "value": {
                        "query": "Review this Python function and suggest improvements: def calculate_average(numbers): return sum(numbers) / len(numbers)",
                        "model": "gpt-4o-mini",
                        "temperature": 0.2,
                        "max_tokens": 300
                    }
                },
                {
                    "summary": "Math Problem with o1-mini",
                    "description": "Step-by-step reasoning via WebSocket",
                    "value": {
                        "query": "Solve and explain: If I invest $1000 at 5% annual compound interest, how much will I have after 10 years?",
                        "model": "o1-mini",
                        "temperature": 0.1,
                        "max_tokens": 350
                    }
                }
            ]
        }
    }