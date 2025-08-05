"""
Pydantic models for request and response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """Request model for the query endpoint."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The query text to send to the GPT model",
        example="What is the capital of France?"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What is the capital of France?"
            }
        }
    }


class QueryResponse(BaseModel):
    """Response model for the query endpoint."""
    
    response: str = Field(
        ...,
        description="The response from the GPT model",
        example="The capital of France is Paris."
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "The capital of France is Paris."
            }
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(
        ...,
        description="Error message",
        example="An error occurred while processing your request"
    )
    
    detail: Optional[str] = Field(
        None,
        description="Additional error details",
        example="OpenAI API key not configured"
    )