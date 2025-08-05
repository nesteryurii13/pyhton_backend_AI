"""
GPT query endpoints.
"""
import json
import time
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from app.models.schemas import GPTQueryRequest, GPTQueryResponse
from app.services.gpt_service import GPTService, GPTServiceError
from app.api.deps import get_current_gpt_service
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/query",
    response_model=GPTQueryResponse,
    summary="Query GPT Model",
    description="Send a query to the GPT model and receive a response",
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Bad request - invalid input"},
        500: {"description": "Internal server error - GPT service issue"},
        503: {"description": "Service unavailable - GPT service down"}
    }
)
async def query_gpt(
    request: GPTQueryRequest,
    gpt_service: GPTService = Depends(get_current_gpt_service)
) -> GPTQueryResponse:
    """
    Process a query using the GPT model.
    
    Args:
        request: The query request containing the text and optional parameters
        gpt_service: The GPT service dependency
        
    Returns:
        The GPT model's response with metadata
        
    Raises:
        HTTPException: If there's an error processing the query
    """
    logger.info(
        "GPT query request received",
        extra={"extra_fields": {
            "query_length": len(request.query),
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }}
    )
    
    try:
        # Get response from GPT service
        gpt_response, metadata = await gpt_service.get_response(
            query=request.query,
            model=request.model.value if request.model else None,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        logger.info(
            "GPT query processed successfully",
            extra={"extra_fields": {
                "response_length": len(gpt_response),
                "processing_time": metadata.get("processing_time"),
                "tokens_used": metadata.get("tokens_used")
            }}
        )
        
        return GPTQueryResponse(
            response=gpt_response,
            model_used=metadata["model_used"],
            tokens_used=metadata.get("tokens_used"),
            processing_time=metadata.get("processing_time")
        )
        
    except GPTServiceError as e:
        logger.error(
            "GPT service error",
            extra={"extra_fields": {"error": str(e)}}
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"GPT service error: {str(e)}"
        )
    except ValueError as e:
        logger.error(
            "Validation error",
            extra={"extra_fields": {"error": str(e)}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Unexpected error processing GPT query",
            extra={"extra_fields": {"error": str(e)}}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        )


@router.post(
    "/query/stream",
    summary="Query GPT Model (Streaming)",
    description="Send a query to the GPT model and receive a real-time streaming response",
    responses={
        200: {"description": "Streaming response", "content": {"text/event-stream": {}}},
        400: {"description": "Bad request - invalid input"},
        500: {"description": "Internal server error - GPT service issue"},
        503: {"description": "Service unavailable - GPT service down"}
    },
    tags=["GPT"]
)
async def query_gpt_stream(
    request: GPTQueryRequest,
    gpt_service: GPTService = Depends(get_current_gpt_service)
) -> StreamingResponse:
    """
    Process a query using the GPT model with real-time streaming.
    
    Args:
        request: The query request containing the text and optional parameters
        gpt_service: The GPT service dependency
        
    Returns:
        Server-Sent Events stream with real-time GPT response
        
    Raises:
        HTTPException: If there's an error processing the query
    """
    logger.info(
        "GPT streaming query request received",
        extra={"extra_fields": {
            "query_length": len(request.query),
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }}
    )
    
    async def generate_stream():
        """Generate SSE stream for GPT response."""
        try:
            async for chunk in gpt_service.get_streaming_response(
                query=request.query,
                model=request.model.value if request.model else None,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                # Format as Server-Sent Events
                yield f"data: {json.dumps(chunk)}\n\n"
                
        except GPTServiceError as e:
            logger.error(
                "GPT service error in streaming",
                extra={"extra_fields": {"error": str(e)}}
            )
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if "timed out" in error_msg.lower():
                user_error = "⏱️ Request timed out. The AI is taking too long to respond. Try a shorter query or try again later."
            elif "rate limit" in error_msg.lower():
                user_error = "🚦 Rate limit reached. Please wait a moment before trying again."
            elif "quota" in error_msg.lower():
                user_error = "💳 API quota exceeded. Please check your OpenAI account."
            else:
                user_error = f"🤖 AI service error: {error_msg}"
            
            error_chunk = {
                "type": "error",
                "error": user_error,
                "timestamp": time.time(),
                "retry_suggested": "timed out" in error_msg.lower() or "rate limit" in error_msg.lower()
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            
        except Exception as e:
            logger.error(
                "Unexpected error in streaming",
                extra={"extra_fields": {"error": str(e)}}
            )
            error_chunk = {
                "type": "error", 
                "error": "⚠️ An unexpected error occurred. Please try again or contact support if the issue persists.",
                "timestamp": time.time(),
                "retry_suggested": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
        
        # Send end signal
        yield f"data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@router.websocket("/query/ws")
async def websocket_gpt_query(
    websocket: WebSocket,
    gpt_service: GPTService = Depends(get_current_gpt_service)
):
    """
    WebSocket endpoint for real-time GPT queries.
    
    Supports bidirectional communication for interactive GPT conversations.
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive query from client
            data = await websocket.receive_text()
            
            try:
                request_data = json.loads(data)
                query = request_data.get("query")
                model = request_data.get("model")
                temperature = request_data.get("temperature")
                max_tokens = request_data.get("max_tokens")
                
                if not query:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "error": "Query is required"
                    }))
                    continue
                
                logger.info(
                    "WebSocket GPT query received",
                    extra={"extra_fields": {
                        "query_length": len(query),
                        "model": model
                    }}
                )
                
                # Stream response back to client
                async for chunk in gpt_service.get_streaming_response(
                    query=query,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    await websocket.send_text(json.dumps(chunk))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Invalid JSON format"
                }))
                
            except GPTServiceError as e:
                logger.error(f"GPT service error in WebSocket: {e}")
                error_msg = str(e)
                
                # Provide user-friendly error messages
                if "timed out" in error_msg.lower():
                    user_error = "⏱️ Request timed out. Try a shorter query or try again later."
                elif "rate limit" in error_msg.lower():
                    user_error = "🚦 Rate limit reached. Please wait before trying again."
                elif "quota" in error_msg.lower():
                    user_error = "💳 API quota exceeded. Please check your OpenAI account."
                else:
                    user_error = f"🤖 AI service error: {error_msg}"
                
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": user_error,
                    "timestamp": time.time(),
                    "retry_suggested": "timed out" in error_msg.lower()
                }))
                
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "⚠️ An unexpected error occurred. Please try again.",
                    "timestamp": time.time(),
                    "retry_suggested": True
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)