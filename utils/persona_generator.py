"""Persona generator for the Synthetic Market Research Engine."""

import logging
from .openai_service import generate_openai_response, get_response_json, DEFAULT_PERSONAS_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_personas(target_segment, num_personas=5):
    """
    Generate demographically relevant personas based on the target segment.
    
    Args:
        target_segment (str): Description of the target demographic or psychographic segment
        num_personas (int): Number of personas to generate
        
    Returns:
        list: List of persona dictionaries
        int: Number of tokens used
    """
    logger.info(f"Generating {num_personas} personas for segment: {target_segment}")
    
    # Construct the prompt for the OpenAI API
    system_message = """You are an expert market research consultant with deep understanding of consumer demographics,
    psychographics, and behavior. Your task is to create realistic, diverse, and detailed personas 
    based on a target market segment description.
    
    Create detailed, realistic personas that match the target segment. Each persona should feel like a real person
    with consistent traits, backgrounds, and believable characteristics.
    
    For each persona, include:
    1. Name and age
    2. Occupation
    3. Background (education, family situation)
    4. Interests/hobbies
    5. Media consumption habits
    6. Core values
    7. Spending habits and price sensitivity
    8. Pain points relevant to the product/service category
    9. Communication style and preferred channel

    Response should be formatted as a JSON array of persona objects.
    """
    
    user_message = f"""Generate {num_personas} detailed personas that represent the target segment described below:
    
    Target segment: {target_segment}
    
    Ensure the personas:
    - Are demographically and psychographically appropriate for the segment
    - Have diverse backgrounds, needs, and preferences while still fitting the segment
    - Include realistic details that would impact their purchasing decisions
    - Have consistent and coherent characteristics
    - Represent different perspectives within the segment
    
    Format as a JSON array of persona objects with the fields mentioned in your instructions.
    """
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    # Call the OpenAI API to generate personas
    response, token_count = generate_openai_response(
        messages=messages,
        model=DEFAULT_PERSONAS_MODEL,
        temperature=0.8,
        as_json=True
    )
    
    # Parse and return the generated personas
    personas = get_response_json(response)
    
    logger.info(f"Generated {len(personas)} personas using {token_count} tokens")
    return personas, token_count