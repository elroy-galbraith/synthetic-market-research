import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.persona_generator import generate_personas
from utils.focus_group import simulate_focus_group
from utils.analysis import analyze_transcript
from utils.database import (
    init_db, 
    save_research_project, 
    get_research_projects, 
    get_project_details, 
    delete_project
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database
init_db()

# API Routes
@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all saved research projects"""
    try:
        projects = get_research_projects()
        return jsonify({"success": True, "projects": projects})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Get details of a specific project"""
    try:
        project_data = get_project_details(project_id)
        if project_data:
            return jsonify({"success": True, "project": project_data})
        else:
            return jsonify({"success": False, "error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def remove_project(project_id):
    """Delete a specific project"""
    try:
        success = delete_project(project_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Failed to delete project"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new research project"""
    try:
        data = request.json
        project_id = save_research_project(
            name=data.get('name'),
            product_concept=data.get('product_concept'),
            target_segment=data.get('target_segment'),
            research_questions=data.get('research_questions'),
            personas=data.get('personas'),
            transcript=data.get('transcript'),
            analysis=data.get('analysis')
        )
        return jsonify({"success": True, "project_id": project_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate/personas', methods=['POST'])
def create_personas():
    """Generate personas based on target segment"""
    try:
        data = request.json
        target_segment = data.get('target_segment')
        num_personas = data.get('num_personas', 5)
        
        personas = generate_personas(target_segment, num_personas)
        return jsonify({"success": True, "personas": personas})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate/focus-group', methods=['POST'])
def create_focus_group():
    """Simulate a focus group discussion"""
    try:
        data = request.json
        personas = data.get('personas')
        product_concept = data.get('product_concept')
        research_questions = data.get('research_questions')
        
        transcript = simulate_focus_group(personas, product_concept, research_questions)
        return jsonify({"success": True, "transcript": transcript})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate/analysis', methods=['POST'])
def create_analysis():
    """Analyze focus group transcript"""
    try:
        data = request.json
        transcript = data.get('transcript')
        product_concept = data.get('product_concept')
        research_questions = data.get('research_questions')
        
        analysis = analyze_transcript(transcript, product_concept, research_questions)
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate/research', methods=['POST'])
def generate_complete_research():
    """Generate complete research (personas, focus group, and analysis)"""
    try:
        data = request.json
        target_segment = data.get('target_segment')
        product_concept = data.get('product_concept')
        research_questions = data.get('research_questions')
        
        # Step 1: Generate personas
        personas = generate_personas(target_segment)
        
        # Step 2: Simulate focus group
        transcript = simulate_focus_group(personas, product_concept, research_questions)
        
        # Step 3: Analyze transcript
        analysis = analyze_transcript(transcript, product_concept, research_questions)
        
        return jsonify({
            "success": True,
            "personas": personas,
            "transcript": transcript,
            "analysis": analysis
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)