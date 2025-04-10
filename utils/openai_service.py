import os
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
DEFAULT_MODEL = "gpt-4o"

def get_openai_client():
    """Initialize and return an OpenAI client."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is not set. Please set it in the sidebar.")
    
    return OpenAI(api_key=api_key)

def validate_api_key():
    """Check if the provided OpenAI API key is valid."""
    try:
        client = get_openai_client()
        # Make a minimal API call to validate the key
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        # If we get here, the API key is valid
        return True, "API key is valid!"
    except Exception as e:
        error_message = str(e)
        if "API key" in error_message.lower() or "auth" in error_message.lower():
            return False, "Invalid API key. Please check and try again."
        else:
            return False, f"Error validating API key: {error_message}"

def generate_openai_response(
    messages, 
    model=DEFAULT_MODEL, 
    temperature=0.7,
    as_json=False,
    max_tokens=None
) -> ChatCompletion:
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
    """
    try:
        client = get_openai_client()
        
        # Prepare API call parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # Add optional parameters
        if as_json:
            params["response_format"] = {"type": "json_object"}
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Make the API call
        response = client.chat.completions.create(**params)
        
        return response
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
        
def get_response_text(response: ChatCompletion) -> str:
    """Extract the text content from an OpenAI API response."""
    return response.choices[0].message.content

def get_response_json(response: ChatCompletion) -> dict:
    """Extract and parse the JSON content from an OpenAI API response."""
    content = get_response_text(response)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If the response isn't valid JSON, try to find JSON within the content
        try:
            # Look for content between triple backticks
            import re
            json_match = re.search(r'```json\n([\s\S]*?)\n```', content)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Look for content between curly braces
            json_match = re.search(r'({[\s\S]*})', content)
            if json_match:
                return json.loads(json_match.group(1))
                
            raise ValueError("Could not extract JSON from response")
        except Exception as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {content}")
