#!/usr/bin/env python
"""
Script to delete a research project from the database.
Called by the Express.js server to leverage our Python database implementation.
"""

import os
import sys
import json

# Add parent directories to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.database import delete_project

def main():
    try:
        # Get the project ID from command-line arguments
        if len(sys.argv) < 2:
            sys.stderr.write("Error: Project ID not provided\n")
            sys.exit(1)
            
        project_id = int(sys.argv[1])
        
        # Delete the project
        success = delete_project(project_id)
        
        # Return the result as JSON
        print(json.dumps({"success": success}))
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()