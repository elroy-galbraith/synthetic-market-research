from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
import logging

# Add the parent directory to the path so we can import our utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our existing utility modules
from utils.database import init_db, save_research_project, get_research_projects, get_project_details, delete_project
from utils.persona_generator import generate_personas
from utils.focus_group import simulate_focus_group
from utils.analysis import analyze_transcript
from utils.openai_service import validate_api_key

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Default route
@app.route('/')
def index():
    return jsonify({
        "message": "Synthetic Market Research API is running",
        "version": "1.0.0"
    })

# API Routes
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all saved research projects"""
    try:
        projects = get_research_projects()
        return jsonify({
            "success": True,
            "projects": projects
        })
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get details of a specific project"""
    try:
        project = get_project_details(project_id)
        if project:
            return jsonify({
                "success": True,
                "project": project
            })
        else:
            return jsonify({
                "success": False,
                "error": "Project not found"
            }), 404
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def remove_project(project_id):
    """Delete a specific project"""
    try:
        success = delete_project(project_id)
        if success:
            return jsonify({
                "success": True,
                "message": f"Project {project_id} deleted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Project not found or could not be deleted"
            }), 404
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new research project"""
    try:
        data = request.json
        
        # Extract data from request
        name = data.get('name')
        product_concept = data.get('product_concept')
        target_segment = data.get('target_segment')
        research_questions = data.get('research_questions', [])
        personas = data.get('personas', [])
        transcript = data.get('transcript', '')
        analysis = data.get('analysis', {})
        
        # Validate required fields
        if not all([name, product_concept, target_segment]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: name, product_concept, target_segment"
            }), 400
        
        # Save to database
        project_id = save_research_project(
            name=name,
            product_concept=product_concept,
            target_segment=target_segment,
            research_questions=research_questions,
            personas=personas,
            transcript=transcript,
            analysis=analysis
        )
        
        return jsonify({
            "success": True,
            "message": "Project created successfully",
            "project_id": project_id
        })
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate/personas', methods=['POST'])
def create_personas():
    """Generate personas based on target segment"""
    try:
        data = request.json
        api_key = request.headers.get('X-API-KEY')
        
        # Validate API key
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Missing API key"
            }), 401
        
        os.environ['OPENAI_API_KEY'] = api_key
        valid_api_key = validate_api_key()
        if not valid_api_key:
            return jsonify({
                "success": False,
                "error": "Invalid OpenAI API key"
            }), 401
            
        # Extract data
        target_segment = data.get('target_segment')
        num_personas = int(data.get('num_personas', 5))
        
        # Validate data
        if not target_segment:
            return jsonify({
                "success": False,
                "error": "Missing target segment"
            }), 400
            
        # Generate personas
        personas, token_count = generate_personas(target_segment, num_personas)
        
        return jsonify({
            "success": True,
            "personas": personas,
            "token_count": token_count
        })
    except Exception as e:
        logger.error(f"Error generating personas: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate/focus-group', methods=['POST'])
def create_focus_group():
    """Simulate a focus group discussion"""
    try:
        data = request.json
        api_key = request.headers.get('X-API-KEY')
        
        # Validate API key
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Missing API key"
            }), 401
        
        os.environ['OPENAI_API_KEY'] = api_key
        valid_api_key = validate_api_key()
        if not valid_api_key:
            return jsonify({
                "success": False,
                "error": "Invalid OpenAI API key"
            }), 401
            
        # Extract data
        personas = data.get('personas')
        product_concept = data.get('product_concept')
        research_questions = data.get('research_questions')
        
        # Validate data
        if not all([personas, product_concept, research_questions]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: personas, product_concept, research_questions"
            }), 400
            
        # Generate focus group transcript
        transcript, token_count = simulate_focus_group(personas, product_concept, research_questions)
        
        return jsonify({
            "success": True,
            "transcript": transcript,
            "token_count": token_count
        })
    except Exception as e:
        logger.error(f"Error generating focus group: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate/analysis', methods=['POST'])
def create_analysis():
    """Analyze focus group transcript"""
    try:
        data = request.json
        api_key = request.headers.get('X-API-KEY')
        
        # Validate API key
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Missing API key"
            }), 401
        
        os.environ['OPENAI_API_KEY'] = api_key
        valid_api_key = validate_api_key()
        if not valid_api_key:
            return jsonify({
                "success": False,
                "error": "Invalid OpenAI API key"
            }), 401
            
        # Extract data
        transcript = data.get('transcript')
        product_concept = data.get('product_concept')
        research_questions = data.get('research_questions')
        
        # Validate data
        if not all([transcript, product_concept, research_questions]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: transcript, product_concept, research_questions"
            }), 400
            
        # Generate analysis
        analysis, token_count = analyze_transcript(transcript, product_concept, research_questions)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "token_count": token_count
        })
    except Exception as e:
        logger.error(f"Error generating analysis: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/generate/research', methods=['POST'])
def generate_complete_research():
    """Generate complete research (personas, focus group, and analysis)"""
    try:
        data = request.json
        api_key = request.headers.get('X-API-KEY')
        
        # Validate API key
        if not api_key:
            return jsonify({
                "success": False,
                "error": "Missing API key"
            }), 401
        
        os.environ['OPENAI_API_KEY'] = api_key
        valid_api_key = validate_api_key()
        if not valid_api_key:
            return jsonify({
                "success": False,
                "error": "Invalid OpenAI API key"
            }), 401
            
        # Extract data
        target_segment = data.get('target_segment')
        product_concept = data.get('product_concept')
        research_questions = data.get('research_questions')
        
        # Validate data
        if not all([target_segment, product_concept, research_questions]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: target_segment, product_concept, research_questions"
            }), 400
        
        # Generate personas
        logger.info("Generating personas...")
        personas, personas_tokens = generate_personas(target_segment)
        
        # Generate focus group transcript
        logger.info("Simulating focus group...")
        transcript, focus_group_tokens = simulate_focus_group(personas, product_concept, research_questions)
        
        # Generate analysis
        logger.info("Analyzing transcript...")
        analysis, analysis_tokens = analyze_transcript(transcript, product_concept, research_questions)
        
        # Combine token counts
        token_count = {
            "personas": personas_tokens,
            "focus_group": focus_group_tokens,
            "analysis": analysis_tokens,
            "total": personas_tokens + focus_group_tokens + analysis_tokens
        }
        
        return jsonify({
            "success": True,
            "personas": personas,
            "transcript": transcript,
            "analysis": analysis,
            "token_count": token_count
        })
    except Exception as e:
        logger.error(f"Error generating complete research: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)