"""OpenAI service utilities for the Synthetic Market Research Engine."""

import os
from openai import OpenAI
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
DEFAULT_PERSONAS_MODEL = "gpt-4o"
DEFAULT_FOCUS_GROUP_MODEL = "gpt-4o"
DEFAULT_ANALYSIS_MODEL = "gpt-4o"

def get_openai_client():
    """Initialize and return an OpenAI client."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key found in environment")
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    return OpenAI(api_key=api_key)

def validate_api_key():
    """Check if the provided OpenAI API key is valid."""
    try:
        client = get_openai_client()
        # Make a minimal API call to verify the key
        response = client.models.list()
        return True
    except Exception as e:
        logger.error(f"API key validation failed: {str(e)}")
        return False

def generate_openai_response(
    messages, 
    model=DEFAULT_MODEL, 
    temperature=0.7,
    as_json=False,
    max_tokens=None
):
    """
    Generate a response from OpenAI's API.
    
    Args:
        messages: List of message objects to send to the API
        model: The OpenAI model to use
        temperature: Controls randomness (0-1)
        as_json: Whether to request response as JSON
        max_tokens: Maximum tokens to generate
        
    Returns:
        ChatCompletion: The API response
        int: Approximate token count used
    """
    client = get_openai_client()
    
    # Configure request parameters
    params = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
    # Add optional parameters if provided
    if max_tokens:
        params["max_tokens"] = max_tokens
        
    if as_json:
        params["response_format"] = {"type": "json_object"}
    
    # Log the request for debugging
    logger.debug(f"OpenAI request: {json.dumps(params, default=str)}")
    
    # Make the API call
    response = client.chat.completions.create(**params)
    
    # Calculate approximate token usage
    token_count = response.usage.total_tokens
    
    return response, token_count

def get_response_text(response):
    """Extract the text content from an OpenAI API response."""
    return response.choices[0].message.content

def get_response_json(response):
    """Extract and parse the JSON content from an OpenAI API response."""
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse response as JSON: {content}")
        raise ValueError("OpenAI response is not valid JSON")