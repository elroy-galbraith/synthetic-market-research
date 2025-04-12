#!/usr/bin/env python
"""
Script to retrieve details of a specific research project from the database.
Called by the Express.js server to access the database.
"""

import os
import sys
import json

# Add parent directories to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.database import get_project_details

def main():
    try:
        # Get the project ID from command-line arguments
        if len(sys.argv) < 2:
            sys.stderr.write("Error: Project ID not provided\n")
            sys.exit(1)
            
        project_id = int(sys.argv[1])
        
        # Get project details
        project = get_project_details(project_id)
        
        if not project:
            # Return empty JSON if project not found
            print("{}")
            sys.exit(0)
            
        # Return the results as JSON
        print(json.dumps(project))
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()