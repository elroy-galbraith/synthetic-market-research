import json
from utils.openai_service import generate_openai_response, get_response_json

def generate_personas(target_segment, num_personas=5):
    """
    Generate demographically relevant personas based on the target segment.
    
    Args:
        target_segment (str): Description of the target demographic or psychographic segment
        num_personas (int): Number of personas to generate
        
    Returns:
        list: List of persona dictionaries
    """
    prompt = f"""
    You are a market research specialist. Based on the target segment described below, 
    create {num_personas} detailed, unique, and culturally appropriate personas that 
    represent this segment.
    
    Target Segment: {target_segment}
    
    For each persona, include:
    1. Name
    2. Age
    3. Occupation
    4. Background (personal history, living situation, etc.)
    5. Interests and hobbies
    6. Media consumption habits
    7. Values and motivations
    8. Spending habits and income level
    9. Pain points relevant to product research
    10. Communication style
    
    Make these personas:
    - Demographically diverse while still representing the target segment
    - Culturally appropriate and realistic
    - Detailed enough to have a clear mental image of each person
    - Have distinct personalities that would influence how they might respond to products
    
    Return your response as a JSON array, where each object is a persona with the fields specified above.
    """
    
    # Call the OpenAI API
    response = generate_openai_response(
        messages=[
            {"role": "system", "content": "You are a market research assistant that creates realistic personas based on demographic information."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,  # Higher temperature for more diverse personas
        as_json=True
    )
    
    # Parse the response
    personas = get_response_json(response)
    
    # Check if we have a list or something wrapped in a field
    if isinstance(personas, dict) and 'personas' in personas:
        personas = personas['personas']
    
    # Ensure we got the right number of personas
    if len(personas) != num_personas:
        raise ValueError(f"Expected {num_personas} personas, but got {len(personas)}")
    
    return personas
