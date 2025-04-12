const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

const app = express();
const PORT = 5001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Helper function to run Python scripts
function runPythonScript(scriptPath, args = [], env = {}) {
  return new Promise((resolve, reject) => {
    const fullEnv = { ...process.env, ...env };
    const pythonProcess = spawn('python', [scriptPath, ...args], { env: fullEnv });
    
    let result = '';
    let error = '';
    
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python script exited with code ${code}`);
        console.error(`Error: ${error}`);
        reject(new Error(`Python script exited with code ${code}: ${error}`));
      } else {
        try {
          // Try to parse the result as JSON
          const jsonResult = JSON.parse(result);
          resolve(jsonResult);
        } catch (e) {
          // If it's not valid JSON, just return the string
          resolve(result);
        }
      }
    });
  });
}

// API Routes

// Default route
app.get('/', (req, res) => {
  res.json({
    message: "Synthetic Market Research API is running",
    version: "1.0.0"
  });
});

// Generate research (personas, focus group, analysis)
app.post('/api/generate/research', async (req, res) => {
  try {
    const { target_segment, product_concept, research_questions } = req.body;
    const apiKey = req.headers['x-api-key'];
    
    if (!apiKey) {
      return res.status(401).json({
        success: false,
        error: "Missing API key"
      });
    }
    
    // Validate required fields
    if (!target_segment || !product_concept || !research_questions || research_questions.length === 0) {
      return res.status(400).json({
        success: false,
        error: "Missing required fields: target_segment, product_concept, research_questions"
      });
    }
    
    // Run Python script to generate personas
    console.log("Generating personas...");
    const scriptPath = path.join(__dirname, 'scripts', 'generate_research.py');
    const result = await runPythonScript(
      scriptPath,
      [],
      {
        OPENAI_API_KEY: apiKey,
        TARGET_SEGMENT: target_segment,
        PRODUCT_CONCEPT: product_concept,
        RESEARCH_QUESTIONS: JSON.stringify(research_questions)
      }
    );
    
    res.json({
      success: true,
      ...result
    });
  } catch (error) {
    console.error("Error generating research:", error);
    res.status(500).json({
      success: false,
      error: error.message || "An error occurred while generating research"
    });
  }
});

// Get all projects
app.get('/api/projects', async (req, res) => {
  try {
    const scriptPath = path.join(__dirname, 'scripts', 'get_projects.py');
    const result = await runPythonScript(scriptPath);
    
    res.json({
      success: true,
      projects: result
    });
  } catch (error) {
    console.error("Error fetching projects:", error);
    res.status(500).json({
      success: false,
      error: error.message || "An error occurred while fetching projects"
    });
  }
});

// Get a specific project
app.get('/api/projects/:id', async (req, res) => {
  try {
    const projectId = req.params.id;
    const scriptPath = path.join(__dirname, 'scripts', 'get_project.py');
    const result = await runPythonScript(scriptPath, [projectId]);
    
    if (result) {
      res.json({
        success: true,
        project: result
      });
    } else {
      res.status(404).json({
        success: false,
        error: "Project not found"
      });
    }
  } catch (error) {
    console.error(`Error fetching project ${req.params.id}:`, error);
    res.status(500).json({
      success: false,
      error: error.message || "An error occurred while fetching the project"
    });
  }
});

// Create a new project
app.post('/api/projects', async (req, res) => {
  try {
    const {
      name,
      product_concept,
      target_segment,
      research_questions,
      personas,
      transcript,
      analysis
    } = req.body;
    
    // Validate required fields
    if (!name || !product_concept || !target_segment) {
      return res.status(400).json({
        success: false,
        error: "Missing required fields: name, product_concept, target_segment"
      });
    }
    
    const scriptPath = path.join(__dirname, 'scripts', 'save_project.py');
    const result = await runPythonScript(
      scriptPath,
      [],
      {
        PROJECT_DATA: JSON.stringify({
          name,
          product_concept,
          target_segment,
          research_questions,
          personas,
          transcript,
          analysis
        })
      }
    );
    
    res.json({
      success: true,
      message: "Project created successfully",
      project_id: result.project_id
    });
  } catch (error) {
    console.error("Error creating project:", error);
    res.status(500).json({
      success: false,
      error: error.message || "An error occurred while creating the project"
    });
  }
});

// Delete a project
app.delete('/api/projects/:id', async (req, res) => {
  try {
    const projectId = req.params.id;
    const scriptPath = path.join(__dirname, 'scripts', 'delete_project.py');
    const result = await runPythonScript(scriptPath, [projectId]);
    
    if (result.success) {
      res.json({
        success: true,
        message: `Project ${projectId} deleted successfully`
      });
    } else {
      res.status(404).json({
        success: false,
        error: "Project not found or could not be deleted"
      });
    }
  } catch (error) {
    console.error(`Error deleting project ${req.params.id}:`, error);
    res.status(500).json({
      success: false,
      error: error.message || "An error occurred while deleting the project"
    });
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});