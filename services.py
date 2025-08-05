"""
Service layer for OpenAI API integration.
"""
import os
import logging
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPTService:
    """Service for interacting with OpenAI's GPT models."""
    
    def __init__(self):
        """Initialize the GPT service."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1")
        logger.info(f"GPT Service initialized with model: {self.model}")
    
    async def get_response(self, query: str) -> str:
        """
        Get a response from the GPT model for the given query.
        
        Args:
            query: The user's query text
            
        Returns:
            The GPT model's response
            
        Raises:
            Exception: If there's an error communicating with the OpenAI API
        """
        try:
            logger.info(f"Sending query to GPT model: {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            if not response.choices or not response.choices[0].message:
                raise Exception("No response received from GPT model")
            
            gpt_response = response.choices[0].message.content
            if not gpt_response:
                raise Exception("Empty response received from GPT model")
            
            logger.info("Successfully received response from GPT model")
            return gpt_response.strip()
            
        except Exception as e:
            logger.error(f"Error communicating with OpenAI API: {str(e)}")
            raise Exception(f"Failed to get response from GPT: {str(e)}")


# Global service instance
gpt_service: Optional[GPTService] = None


def get_gpt_service() -> GPTService:
    """
    Dependency injection function to get the GPT service instance.
    
    Returns:
        The GPT service instance
    """
    global gpt_service
    if gpt_service is None:
        gpt_service = GPTService()
    return gpt_service