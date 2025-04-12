import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from utils.openai_service import generate_openai_response, get_response_json, get_response_text

# Download NLTK resources
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def analyze_transcript(transcript, product_concept, research_questions):
    """
    Analyze the focus group transcript for sentiment, themes, objections/praise, and pricing.
    
    Args:
        transcript (str): The focus group transcript
        product_concept (str): Description of the product or service
        research_questions (list): List of research questions discussed
        
    Returns:
        dict: Analysis results
    """
    # First, use NLTK for a quick sentiment analysis to provide additional context
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(transcript)
    
    # LLM-based analysis for comprehensive insights
    prompt = f"""
    You are a market research analyst reviewing a focus group transcript. Analyze this 
    transcript and extract key insights related to the product concept.
    
    # PRODUCT CONCEPT
    {product_concept}
    
    # RESEARCH QUESTIONS
    {", ".join(research_questions)}
    
    # TRANSCRIPT
    {transcript}
    
    Based on this transcript, provide a comprehensive analysis in JSON format with the following structure:
    
    {{
        "emotional_tone": {{
            "positive": 0.0 to 1.0,
            "neutral": 0.0 to 1.0,
            "negative": 0.0 to 1.0,
            "skeptical": 0.0 to 1.0,
            "excited": 0.0 to 1.0
        }},
        "emotional_summary": "Brief summary of overall emotional response",
        "themes": {{
            "theme1": frequency (1-10),
            "theme2": frequency (1-10),
            ...
        }},
        "theme_details": {{
            "theme1": "explanation of this theme and examples from transcript",
            "theme2": "explanation of this theme and examples from transcript",
            ...
        }},
        "objections": [
            "Major objection 1",
            "Major objection 2",
            ...
        ],
        "praise": [
            "Major praise point 1",
            "Major praise point 2",
            ...
        ],
        "pricing": {{
            "sensitivity": 0.0 to 1.0 (0 = not sensitive, 1 = extremely sensitive),
            "min_price": suggested minimum price (numeric),
            "max_price": suggested maximum price (numeric),
            "notes": "Detailed notes on pricing discussion"
        }},
        "participant_alignment": {{
            "persona1": "brief description of their overall stance",
            "persona2": "brief description of their overall stance",
            ...
        }},
        "summary": "Overall summary of focus group findings",
        "recommendations": [
            "Strategic recommendation 1",
            "Strategic recommendation 2",
            ...
        ]
    }}
    
    Ensure that all numeric values are actual numbers (not strings), the analysis is objective, 
    and insights are directly supported by the transcript content.
    """
    
    # Call the OpenAI API for the analysis
    response = generate_openai_response(
        messages=[
            {"role": "system", "content": "You are a market research analysis expert who provides detailed, objective insights from focus group data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # Lower temperature for more consistent analysis
        as_json=True
    )
    
    # Parse the response
    analysis = get_response_json(response)
    
    # Add NLTK sentiment data for comparison
    analysis['nltk_sentiment'] = sentiment_scores
    
    return analysis
