#!/usr/bin/env python
"""
Script to save a research project to the database.
Called by the Express.js server to leverage our Python database implementation.
"""

import os
import sys
import json

# Add parent directories to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.database import save_research_project

def main():
    try:
        # Get project data from environment variable
        project_data_str = os.environ.get('PROJECT_DATA')
        if not project_data_str:
            sys.stderr.write("Error: PROJECT_DATA not provided\n")
            sys.exit(1)
            
        # Parse project data
        project_data = json.loads(project_data_str)
        
        # Extract fields
        name = project_data.get('name')
        product_concept = project_data.get('product_concept')
        target_segment = project_data.get('target_segment')
        research_questions = project_data.get('research_questions', [])
        personas = project_data.get('personas', [])
        transcript = project_data.get('transcript', '')
        analysis = project_data.get('analysis', {})
        
        # Validate required fields
        if not name or not product_concept or not target_segment:
            sys.stderr.write("Error: Missing required fields: name, product_concept, target_segment\n")
            sys.exit(1)
            
        # Save the project
        project_id = save_research_project(
            name=name,
            product_concept=product_concept,
            target_segment=target_segment,
            research_questions=research_questions,
            personas=personas,
            transcript=transcript,
            analysis=analysis
        )
        
        # Return the project ID as JSON
        print(json.dumps({"project_id": project_id}))
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()