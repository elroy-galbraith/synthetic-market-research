#!/usr/bin/env python
"""
Script to retrieve all saved research projects from the database.
Called by the Express.js server to access the database.
"""

import os
import sys
import json

# Add parent directories to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.database import get_research_projects

def main():
    try:
        # Get all projects
        projects = get_research_projects()
        
        # Return the results as JSON
        print(json.dumps(projects))
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()