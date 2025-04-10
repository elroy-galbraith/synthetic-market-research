from utils.openai_service import generate_openai_response, get_response_text

def simulate_focus_group(personas, product_concept, research_questions):
    """
    Simulate a focus group discussion between the generated personas.
    
    Args:
        personas (list): List of persona dictionaries
        product_concept (str): Description of the product or service
        research_questions (list): List of research questions to discuss
        
    Returns:
        str: Structured transcript of the simulated focus group
    """
    # Format the personas into a concise description for the prompt
    persona_descriptions = []
    for i, p in enumerate(personas):
        desc = f"Persona {i+1}: {p['name']}, {p['age']}, {p['occupation']}, {p['background'][:100]}..."
        persona_descriptions.append(desc)
    
    persona_text = "\n".join(persona_descriptions)
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(research_questions)])
    
    prompt = f"""
    You are an experienced market research moderator conducting a focus group with 
    the following participants about a new product or service concept.
    
    # PARTICIPANTS
    {persona_text}
    
    # PRODUCT CONCEPT
    {product_concept}
    
    # RESEARCH QUESTIONS
    {questions_text}
    
    Your task is to simulate a realistic focus group discussion between these personas 
    as they discuss the product concept and answer the research questions. 
    
    The discussion should:
    1. Start with brief introductions from each persona
    2. Have you as the moderator introduce the product concept
    3. Address each research question with input from all participants
    4. Include natural disagreements, insights, and reactions based on each persona's background
    5. Conclude with final thoughts from each participant
    
    Make sure the dialogue:
    - Is realistic and conversational
    - Reflects how each persona would actually speak based on their demographics and background
    - Includes interruptions, agreements, disagreements, and cross-talk where appropriate
    - Has personas referring to their own life experiences that influence their opinions
    - Shows clear personality differences between participants
    
    Format the transcript with clear speaker labels (e.g., "Moderator:", "Maria:"), and 
    organize it into sections for introductions, each research question, and conclusions.
    """
    
    # Call the OpenAI API - using higher max tokens because transcripts can be long
    response = generate_openai_response(
        messages=[
            {"role": "system", "content": "You are a market research specialist who creates realistic focus group transcripts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    
    # Extract the transcript text
    transcript = get_response_text(response)
    
    return transcript
