"""Focus group simulator for the Synthetic Market Research Engine."""

import logging
from .openai_service import generate_openai_response, get_response_text, DEFAULT_FOCUS_GROUP_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_focus_group(personas, product_concept, research_questions):
    """
    Simulate a focus group discussion between the generated personas.
    
    Args:
        personas (list): List of persona dictionaries
        product_concept (str): Description of the product or service
        research_questions (list): List of research questions to discuss
        
    Returns:
        str: Structured transcript of the simulated focus group
        int: Number of tokens used
    """
    logger.info(f"Simulating focus group discussion for {len(personas)} personas")
    
    # Format the research questions as a string
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(research_questions)])
    
    # Format personas for the prompt
    personas_text = ""
    for i, persona in enumerate(personas):
        personas_text += f"Persona {i+1}: {persona['name']}, {persona['age']}, {persona['occupation']}\n"
        personas_text += f"Background: {persona.get('background', 'N/A')}\n"
        personas_text += f"Interests: {persona.get('interests', 'N/A')}\n"
        personas_text += f"Values: {persona.get('values', 'N/A')}\n"
        personas_text += f"Pain Points: {persona.get('pain_points', 'N/A')}\n"
        personas_text += f"Communication Style: {persona.get('communication_style', 'N/A')}\n\n"
    
    # Construct the prompt for the OpenAI API
    system_message = """You are an expert market research moderator who can simulate realistic focus group discussions.
    Your task is to create a transcript of a focus group discussion between multiple personas discussing
    a product/service concept. The discussion should follow a natural flow and address specific research questions.
    
    For each research question:
    1. Introduce the question as the moderator
    2. Show how each persona responds, with their name as a prefix
    3. Include follow-up questions and natural back-and-forth discussion between personas
    4. Make sure personas stay true to their backgrounds, values, and communication styles
    5. Include realistic group dynamics like agreement, disagreement, building on others' points
    
    The transcript should be formatted clearly with timestamps, speaker names, and organized by discussion topics.
    Include an introduction and conclusion from the moderator. Make the discussion feel authentic and insightful.
    """
    
    user_message = f"""Simulate a focus group discussion between the following personas discussing this product/service concept:
    
    PRODUCT/SERVICE CONCEPT:
    {product_concept}
    
    RESEARCH QUESTIONS TO ADDRESS:
    {questions_text}
    
    PERSONAS:
    {personas_text}
    
    Create a realistic, detailed focus group transcript where these personas discuss the product/service concept
    and address all the research questions. Ensure each persona speaks in a way consistent with their background,
    values, and communication style. Include natural group dynamics and a mix of positive and negative feedback.
    """
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    # Call the OpenAI API to generate the focus group transcript
    response, token_count = generate_openai_response(
        messages=messages,
        model=DEFAULT_FOCUS_GROUP_MODEL,
        temperature=0.8
    )
    
    # Get the transcript text
    transcript = get_response_text(response)
    
    logger.info(f"Generated focus group transcript using {token_count} tokens")
    return transcript, token_count