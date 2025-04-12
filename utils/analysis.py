"""Analysis module for the Synthetic Market Research Engine."""

import logging
from .openai_service import generate_openai_response, get_response_json, DEFAULT_ANALYSIS_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_transcript(transcript, product_concept, research_questions):
    """
    Analyze the focus group transcript for sentiment, themes, objections/praise, and pricing.
    
    Args:
        transcript (str): The focus group transcript
        product_concept (str): Description of the product or service
        research_questions (list): List of research questions discussed
        
    Returns:
        dict: Analysis results
        int: Number of tokens used
    """
    logger.info("Analyzing focus group transcript")
    
    # Format the research questions as a string
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(research_questions)])
    
    # Construct the prompt for the OpenAI API
    system_message = """You are an expert market research analyst who specializes in analyzing focus group transcripts.
    Your task is to analyze a focus group transcript and extract key insights about the discussed product/service concept.
    
    Analyze the transcript and provide the following:
    
    1. EMOTIONAL TONE: Quantify the emotional reactions of participants (surprise, interest, confusion, enthusiasm, skepticism, etc.)
       with numerical values from 0.0-1.0, and provide a brief summary of the overall emotional response.
    
    2. KEY THEMES: Identify 3-5 key themes or patterns in the discussion, and provide a detailed explanation of each theme.
    
    3. OBJECTIONS: List the main objections or concerns raised about the product/service.
    
    4. PRAISE: List the main positive points or aspects praised about the product/service.
    
    5. PRICING SENSITIVITY: Analyze mentions of pricing or value, and provide a summary of price sensitivity and a suggested price range if discussed.
    
    6. PARTICIPANT ALIGNMENT: Analyze how well each participant aligns with or seems interested in the product/service concept.
    
    7. SUMMARY: Provide a concise summary of the overall market research findings.
    
    8. RECOMMENDATIONS: Provide 3-5 concrete recommendations for improving the product/service concept based on the focus group feedback.
    
    Structure your response as a JSON object with appropriate keys for each section of the analysis.
    """
    
    user_message = f"""Analyze this focus group transcript about the following product/service concept:
    
    PRODUCT/SERVICE CONCEPT:
    {product_concept}
    
    RESEARCH QUESTIONS DISCUSSED:
    {questions_text}
    
    TRANSCRIPT:
    {transcript}
    
    Please provide a comprehensive analysis following the structure in your instructions.
    Focus especially on extracting actionable insights and clear recommendations.
    """
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    
    # Call the OpenAI API to generate the analysis
    response, token_count = generate_openai_response(
        messages=messages,
        model=DEFAULT_ANALYSIS_MODEL,
        temperature=0.5,
        as_json=True
    )
    
    # Parse and return the analysis results
    analysis = get_response_json(response)
    
    logger.info(f"Completed transcript analysis using {token_count} tokens")
    return analysis, token_count