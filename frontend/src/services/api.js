// API Service for Synthetic Market Research Engine
const apiService = {
  baseUrl: 'http://localhost:5001/api',
  
  async generateResearch(data) {
    try {
      const response = await fetch(`${this.baseUrl}/generate/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-KEY': data.api_key
        },
        body: JSON.stringify({
          target_segment: data.target_segment,
          product_concept: data.product_concept,
          research_questions: data.research_questions
        })
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error generating research:', error);
      throw new Error('Failed to connect to the API server');
    }
  },
  
  async getProjects() {
    try {
      const response = await fetch(`${this.baseUrl}/projects`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching projects:', error);
      throw new Error('Failed to connect to the API server');
    }
  },
  
  async getProject(projectId) {
    try {
      const response = await fetch(`${this.baseUrl}/projects/${projectId}`);
      return await response.json();
    } catch (error) {
      console.error(`Error fetching project ${projectId}:`, error);
      throw new Error('Failed to connect to the API server');
    }
  },
  
  async saveProject(data) {
    try {
      const response = await fetch(`${this.baseUrl}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      return await response.json();
    } catch (error) {
      console.error('Error saving project:', error);
      throw new Error('Failed to connect to the API server');
    }
  },
  
  async deleteProject(projectId) {
    try {
      const response = await fetch(`${this.baseUrl}/projects/${projectId}`, {
        method: 'DELETE'
      });
      
      return await response.json();
    } catch (error) {
      console.error(`Error deleting project ${projectId}:`, error);
      throw new Error('Failed to connect to the API server');
    }
  }
};

export default apiService;