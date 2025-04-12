#!/usr/bin/env python
"""
Script to generate complete market research using existing Python business logic.
Called by the Express.js server to leverage our Python AI capabilities.
"""

import os
import sys
import json

# Add parent directories to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.persona_generator import generate_personas
from utils.focus_group import simulate_focus_group
from utils.analysis import analyze_transcript

def main():
    # Get parameters from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    target_segment = os.environ.get('TARGET_SEGMENT')
    product_concept = os.environ.get('PRODUCT_CONCEPT')
    research_questions = json.loads(os.environ.get('RESEARCH_QUESTIONS', '[]'))
    
    # Set API key
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Validate parameters
    if not api_key:
        sys.stderr.write("Error: OPENAI_API_KEY not provided\n")
        sys.exit(1)
    if not target_segment:
        sys.stderr.write("Error: TARGET_SEGMENT not provided\n")
        sys.exit(1)
    if not product_concept:
        sys.stderr.write("Error: PRODUCT_CONCEPT not provided\n")
        sys.exit(1)
    if not research_questions:
        sys.stderr.write("Error: RESEARCH_QUESTIONS not provided or empty\n")
        sys.exit(1)
    
    try:
        # Generate personas
        personas, personas_tokens = generate_personas(target_segment)
        
        # Generate focus group transcript
        transcript, focus_group_tokens = simulate_focus_group(personas, product_concept, research_questions)
        
        # Generate analysis
        analysis, analysis_tokens = analyze_transcript(transcript, product_concept, research_questions)
        
        # Combine token counts
        token_count = {
            "personas": personas_tokens,
            "focus_group": focus_group_tokens,
            "analysis": analysis_tokens,
            "total": personas_tokens + focus_group_tokens + analysis_tokens
        }
        
        # Return the results as JSON
        result = {
            "personas": personas,
            "transcript": transcript,
            "analysis": analysis,
            "token_count": token_count
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()