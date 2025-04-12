// Use Vue from CDN loaded in index.html
const { createApp } = Vue;

// API Service
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

// Root app component
const App = {
  data() {
    return {
      // Navigation state
      activePage: 'new-research',
      
      // Form data
      apiKey: localStorage.getItem('openai_api_key') || '',
      productConcept: '',
      targetSegment: '',
      researchQuestions: [''],
      projectName: '',
      
      // Generated research data
      personas: null,
      transcript: null,
      analysis: null,
      
      // Projects data
      projects: [],
      selectedProjectId: null,
      loadedProject: null,
      
      // UI state
      isLoading: false,
      loadingMessage: '',
      errorMessage: '',
      successMessage: '',
      confirmDelete: false,
      
      // Token usage tracking
      tokenCount: {
        personas: 0,
        focus_group: 0,
        analysis: 0,
        total: 0
      }
    };
  },
  
  mounted() {
    // Save API key when changed
    this.$watch('apiKey', (newKey) => {
      localStorage.setItem('openai_api_key', newKey);
    });
    
    // Load projects when viewing saved projects page
    this.$watch('activePage', (newPage) => {
      if (newPage === 'saved-projects') {
        this.loadProjects();
      }
    });
  },
  
  methods: {
    // Navigation methods
    navigateTo(page) {
      this.activePage = page;
      // Reset errors and success messages
      this.errorMessage = '';
      this.successMessage = '';
    },
    
    // Form methods
    addQuestion() {
      this.researchQuestions.push('');
    },
    
    removeQuestion(index) {
      this.researchQuestions = this.researchQuestions.filter((_, i) => i !== index);
    },
    
    // API methods
    async generateResearch() {
      if (!this.apiKey) {
        this.errorMessage = 'Please enter your OpenAI API key';
        return;
      }
      
      if (!this.productConcept) {
        this.errorMessage = 'Please enter a product/service concept';
        return;
      }
      
      if (!this.targetSegment) {
        this.errorMessage = 'Please enter a target segment';
        return;
      }
      
      const validQuestions = this.researchQuestions.filter(q => q.trim() !== '');
      if (validQuestions.length === 0) {
        this.errorMessage = 'Please enter at least one research question';
        return;
      }
      
      this.isLoading = true;
      this.loadingMessage = 'Generating research... This may take a minute';
      this.errorMessage = '';
      
      try {
        const response = await apiService.generateResearch({
          api_key: this.apiKey,
          product_concept: this.productConcept,
          target_segment: this.targetSegment,
          research_questions: validQuestions
        });
        
        if (response.success) {
          this.personas = response.personas;
          this.transcript = response.transcript;
          this.analysis = response.analysis;
          this.tokenCount = response.token_count || {
            personas: 0,
            focus_group: 0,
            analysis: 0,
            total: 0
          };
          this.successMessage = 'Research generated successfully!';
        } else {
          this.errorMessage = response.error || 'An error occurred while generating research';
        }
      } catch (error) {
        this.errorMessage = error.message || 'An error occurred while generating research';
      } finally {
        this.isLoading = false;
      }
    },
    
    async saveProject() {
      if (!this.projectName) {
        this.errorMessage = 'Please enter a project name';
        return;
      }
      
      this.isLoading = true;
      this.loadingMessage = 'Saving project...';
      this.errorMessage = '';
      
      try {
        const response = await apiService.saveProject({
          name: this.projectName,
          product_concept: this.productConcept,
          target_segment: this.targetSegment,
          research_questions: this.researchQuestions.filter(q => q.trim() !== ''),
          personas: this.personas,
          transcript: this.transcript,
          analysis: this.analysis
        });
        
        if (response.success) {
          this.successMessage = `Project saved successfully! Project ID: ${response.project_id}`;
        } else {
          this.errorMessage = response.error || 'An error occurred while saving the project';
        }
      } catch (error) {
        this.errorMessage = error.message || 'An error occurred while saving the project';
      } finally {
        this.isLoading = false;
      }
    },
    
    async loadProjects() {
      this.isLoading = true;
      this.loadingMessage = 'Loading projects...';
      this.errorMessage = '';
      
      try {
        const response = await apiService.getProjects();
        
        if (response.success) {
          this.projects = response.projects;
          if (this.projects.length > 0) {
            this.selectedProjectId = this.projects[0].id;
          }
        } else {
          this.errorMessage = response.error || 'An error occurred while loading projects';
        }
      } catch (error) {
        this.errorMessage = error.message || 'An error occurred while loading projects';
      } finally {
        this.isLoading = false;
      }
    },
    
    async loadProject() {
      if (!this.selectedProjectId) {
        this.errorMessage = 'Please select a project to load';
        return;
      }
      
      this.isLoading = true;
      this.loadingMessage = 'Loading project...';
      this.errorMessage = '';
      
      try {
        const response = await apiService.getProject(this.selectedProjectId);
        
        if (response.success) {
          this.loadedProject = response.project;
          this.personas = response.project.personas;
          this.transcript = response.project.transcript;
          this.analysis = response.project.analysis;
          this.productConcept = response.project.product_concept;
          this.targetSegment = response.project.target_segment;
          this.researchQuestions = response.project.research_questions;
          this.navigateTo('new-research');
          this.successMessage = 'Project loaded successfully!';
        } else {
          this.errorMessage = response.error || 'An error occurred while loading the project';
        }
      } catch (error) {
        this.errorMessage = error.message || 'An error occurred while loading the project';
      } finally {
        this.isLoading = false;
      }
    },
    
    async deleteProject() {
      if (!this.selectedProjectId) {
        this.errorMessage = 'Please select a project to delete';
        return;
      }
      
      if (!this.confirmDelete) {
        this.confirmDelete = true;
        return;
      }
      
      this.isLoading = true;
      this.loadingMessage = 'Deleting project...';
      this.errorMessage = '';
      
      try {
        const response = await apiService.deleteProject(this.selectedProjectId);
        
        if (response.success) {
          this.successMessage = 'Project deleted successfully!';
          this.loadProjects();
          this.confirmDelete = false;
        } else {
          this.errorMessage = response.error || 'An error occurred while deleting the project';
        }
      } catch (error) {
        this.errorMessage = error.message || 'An error occurred while deleting the project';
      } finally {
        this.isLoading = false;
      }
    },
    
    clearLoadedProject() {
      this.loadedProject = null;
      this.personas = null;
      this.transcript = null;
      this.analysis = null;
      this.productConcept = '';
      this.targetSegment = '';
      this.researchQuestions = [''];
    },
    
    // Download methods
    downloadJson() {
      const results = {
        product_concept: this.productConcept,
        target_segment: this.targetSegment,
        research_questions: this.researchQuestions.filter(q => q.trim() !== ''),
        personas: this.personas,
        transcript: this.transcript,
        analysis: this.analysis
      };
      
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(results, null, 2));
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", "market_research_results.json");
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    },
    
    downloadTranscript() {
      const dataStr = "data:text/plain;charset=utf-8," + encodeURIComponent(this.transcript);
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", "focus_group_transcript.txt");
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    }
  },
  
  template: `
    <div class="container-fluid">
      <!-- Loading overlay -->
      <div class="loading-overlay" v-if="isLoading">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <div class="mt-3">{{ loadingMessage }}</div>
      </div>
      
      <div class="row">
        <!-- Sidebar -->
        <div class="col-md-3 col-lg-2 sidebar">
          <h4 class="mb-4 text-center">Synthetic Market Research</h4>
          
          <div class="list-group mb-4">
            <button @click="navigateTo('new-research')" class="list-group-item list-group-item-action" :class="{ active: activePage === 'new-research' }">
              <i class="bi bi-lightbulb"></i> New Research
            </button>
            <button @click="navigateTo('saved-projects')" class="list-group-item list-group-item-action" :class="{ active: activePage === 'saved-projects' }">
              <i class="bi bi-archive"></i> Saved Projects
            </button>
          </div>
          
          <div class="card mb-4">
            <div class="card-header">OpenAI API Key</div>
            <div class="card-body">
              <input type="password" v-model="apiKey" class="form-control mb-2" placeholder="Enter your API key">
              <div class="form-text">Your API key is stored locally in your browser.</div>
            </div>
          </div>
          
          <div v-if="tokenCount.total > 0" class="card">
            <div class="card-header">Token Usage</div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                <li class="list-group-item d-flex justify-content-between">
                  <span>Personas:</span>
                  <span>{{ tokenCount.personas }}</span>
                </li>
                <li class="list-group-item d-flex justify-content-between">
                  <span>Focus Group:</span>
                  <span>{{ tokenCount.focus_group }}</span>
                </li>
                <li class="list-group-item d-flex justify-content-between">
                  <span>Analysis:</span>
                  <span>{{ tokenCount.analysis }}</span>
                </li>
                <li class="list-group-item d-flex justify-content-between fw-bold">
                  <span>Total:</span>
                  <span>{{ tokenCount.total }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Main content -->
        <div class="col-md-9 col-lg-10 content">
          <!-- Alert messages -->
          <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show">
            {{ errorMessage }}
            <button type="button" class="btn-close" @click="errorMessage = ''"></button>
          </div>
          
          <div v-if="successMessage" class="alert alert-success alert-dismissible fade show">
            {{ successMessage }}
            <button type="button" class="btn-close" @click="successMessage = ''"></button>
          </div>
          
          <!-- New Research Page -->
          <div v-if="activePage === 'new-research'">
            <!-- If a project is loaded -->
            <div v-if="loadedProject">
              <h2>Loaded Project: {{ loadedProject.name }}</h2>
              
              <!-- Results display (same as below) -->
              <div v-if="personas && transcript && analysis">
                <!-- Personas Section -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Generated Personas</h3>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div v-for="(persona, index) in personas" :key="index" class="col-md-6 mb-3">
                        <div class="card h-100">
                          <div class="card-header">
                            <h4>{{ persona.name }}, {{ persona.age }}</h4>
                          </div>
                          <div class="card-body">
                            <p><strong>Occupation:</strong> {{ persona.occupation }}</p>
                            <p><strong>Background:</strong> {{ persona.background }}</p>
                            <p><strong>Interests:</strong> {{ persona.interests }}</p>
                            <p><strong>Values:</strong> {{ persona.values }}</p>
                            <p><strong>Pain Points:</strong> {{ persona.pain_points }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Focus Group Transcript Section -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Focus Group Transcript</h3>
                  </div>
                  <div class="card-body">
                    <div class="bg-light p-3 rounded" style="white-space: pre-wrap;">{{ transcript }}</div>
                  </div>
                </div>
                
                <!-- Analysis Section -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Analysis Results</h3>
                  </div>
                  <div class="card-body">
                    <!-- Emotional Tone -->
                    <h4>Emotional Tone</h4>
                    <div class="mb-4">
                      <p>{{ analysis.emotional_summary }}</p>
                      <div class="row">
                        <div v-for="(value, emotion) in analysis.emotional_tone" :key="emotion" class="col-md-4 mb-3">
                          <div class="card">
                            <div class="card-body">
                              <h5 class="card-title">{{ emotion }}</h5>
                              <div class="progress">
                                <div class="progress-bar" role="progressbar" :style="{ width: (value * 100) + '%' }" :aria-valuenow="value * 100" aria-valuemin="0" aria-valuemax="100">
                                  {{ Math.round(value * 100) }}%
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Key Themes -->
                    <h4>Key Themes</h4>
                    <div class="mb-4">
                      <div class="row">
                        <div v-for="(details, theme) in analysis.theme_details" :key="theme" class="col-md-6 mb-3">
                          <div class="card h-100">
                            <div class="card-header">
                              <h5>{{ theme }}</h5>
                            </div>
                            <div class="card-body">
                              <p>{{ details }}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Objections & Praise -->
                    <div class="row mb-4">
                      <div class="col-md-6">
                        <h4>Objections</h4>
                        <ul class="list-group">
                          <li v-for="(objection, index) in analysis.objections" :key="'obj-'+index" class="list-group-item">
                            {{ objection }}
                          </li>
                        </ul>
                      </div>
                      <div class="col-md-6">
                        <h4>Praise</h4>
                        <ul class="list-group">
                          <li v-for="(praise, index) in analysis.praise" :key="'praise-'+index" class="list-group-item">
                            {{ praise }}
                          </li>
                        </ul>
                      </div>
                    </div>
                    
                    <!-- Pricing Sensitivity -->
                    <h4>Pricing Sensitivity</h4>
                    <div class="mb-4">
                      <p><strong>Summary:</strong> {{ analysis.pricing.summary }}</p>
                      <p><strong>Suggested Price Range:</strong> {{ analysis.pricing.price_range }}</p>
                    </div>
                    
                    <!-- Recommendations -->
                    <h4>Recommendations</h4>
                    <div class="mb-4">
                      <ul class="list-group">
                        <li v-for="(rec, index) in analysis.recommendations" :key="'rec-'+index" class="list-group-item">
                          {{ rec }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <!-- Download Options -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Download Results</h3>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-6">
                        <button @click="downloadJson" class="btn btn-primary w-100">Download Complete Results (JSON)</button>
                      </div>
                      <div class="col-md-6">
                        <button @click="downloadTranscript" class="btn btn-primary w-100">Download Transcript (TXT)</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <button @click="clearLoadedProject" class="btn btn-outline-primary mb-4">Start New Research</button>
            </div>
            
            <!-- If no project is loaded -->
            <div v-else>
              <h2>New Market Research</h2>
              
              <div class="card mb-4">
                <div class="card-header">Research Configuration</div>
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label">Product/Service Concept</label>
                    <textarea v-model="productConcept" class="form-control" rows="3" placeholder="Describe your product or service concept in detail"></textarea>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Target Segment</label>
                    <textarea v-model="targetSegment" class="form-control" rows="3" placeholder="Describe your target demographic or psychographic segment"></textarea>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Research Questions</label>
                    <div v-for="(question, index) in researchQuestions" :key="index" class="input-group mb-2">
                      <input type="text" v-model="researchQuestions[index]" class="form-control" placeholder="Enter a research question">
                      <button @click="removeQuestion(index)" class="btn btn-outline-danger" :disabled="researchQuestions.length === 1">
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                    <button @click="addQuestion" class="btn btn-outline-primary">
                      <i class="bi bi-plus"></i> Add Question
                    </button>
                  </div>
                  
                  <button @click="generateResearch" class="btn btn-primary">Generate Research</button>
                </div>
              </div>
              
              <!-- Results display (when available) -->
              <div v-if="personas && transcript && analysis">
                <!-- Same content as in the "project is loaded" case -->
                <!-- Personas Section -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Generated Personas</h3>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div v-for="(persona, index) in personas" :key="index" class="col-md-6 mb-3">
                        <div class="card h-100">
                          <div class="card-header">
                            <h4>{{ persona.name }}, {{ persona.age }}</h4>
                          </div>
                          <div class="card-body">
                            <p><strong>Occupation:</strong> {{ persona.occupation }}</p>
                            <p><strong>Background:</strong> {{ persona.background }}</p>
                            <p><strong>Interests:</strong> {{ persona.interests }}</p>
                            <p><strong>Values:</strong> {{ persona.values }}</p>
                            <p><strong>Pain Points:</strong> {{ persona.pain_points }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Focus Group Transcript Section -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Focus Group Transcript</h3>
                  </div>
                  <div class="card-body">
                    <div class="bg-light p-3 rounded" style="white-space: pre-wrap;">{{ transcript }}</div>
                  </div>
                </div>
                
                <!-- Analysis Section -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Analysis Results</h3>
                  </div>
                  <div class="card-body">
                    <!-- Emotional Tone -->
                    <h4>Emotional Tone</h4>
                    <div class="mb-4">
                      <p>{{ analysis.emotional_summary }}</p>
                      <div class="row">
                        <div v-for="(value, emotion) in analysis.emotional_tone" :key="emotion" class="col-md-4 mb-3">
                          <div class="card">
                            <div class="card-body">
                              <h5 class="card-title">{{ emotion }}</h5>
                              <div class="progress">
                                <div class="progress-bar" role="progressbar" :style="{ width: (value * 100) + '%' }" :aria-valuenow="value * 100" aria-valuemin="0" aria-valuemax="100">
                                  {{ Math.round(value * 100) }}%
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Key Themes -->
                    <h4>Key Themes</h4>
                    <div class="mb-4">
                      <div class="row">
                        <div v-for="(details, theme) in analysis.theme_details" :key="theme" class="col-md-6 mb-3">
                          <div class="card h-100">
                            <div class="card-header">
                              <h5>{{ theme }}</h5>
                            </div>
                            <div class="card-body">
                              <p>{{ details }}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Objections & Praise -->
                    <div class="row mb-4">
                      <div class="col-md-6">
                        <h4>Objections</h4>
                        <ul class="list-group">
                          <li v-for="(objection, index) in analysis.objections" :key="'obj-'+index" class="list-group-item">
                            {{ objection }}
                          </li>
                        </ul>
                      </div>
                      <div class="col-md-6">
                        <h4>Praise</h4>
                        <ul class="list-group">
                          <li v-for="(praise, index) in analysis.praise" :key="'praise-'+index" class="list-group-item">
                            {{ praise }}
                          </li>
                        </ul>
                      </div>
                    </div>
                    
                    <!-- Pricing Sensitivity -->
                    <h4>Pricing Sensitivity</h4>
                    <div class="mb-4">
                      <p><strong>Summary:</strong> {{ analysis.pricing.summary }}</p>
                      <p><strong>Suggested Price Range:</strong> {{ analysis.pricing.price_range }}</p>
                    </div>
                    
                    <!-- Recommendations -->
                    <h4>Recommendations</h4>
                    <div class="mb-4">
                      <ul class="list-group">
                        <li v-for="(rec, index) in analysis.recommendations" :key="'rec-'+index" class="list-group-item">
                          {{ rec }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <!-- Download Options -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Download Results</h3>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-6">
                        <button @click="downloadJson" class="btn btn-primary w-100">Download Complete Results (JSON)</button>
                      </div>
                      <div class="col-md-6">
                        <button @click="downloadTranscript" class="btn btn-primary w-100">Download Transcript (TXT)</button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Save Project Option -->
                <div class="card mb-4">
                  <div class="card-header">
                    <h3>Save Research Project</h3>
                  </div>
                  <div class="card-body">
                    <div class="input-group">
                      <input type="text" v-model="projectName" class="form-control" placeholder="E.g., Japanese Learning App Research">
                      <button @click="saveProject" class="btn btn-primary" :disabled="!projectName">Save Project to Database</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Saved Projects Page -->
          <div v-if="activePage === 'saved-projects'">
            <h2>Saved Research Projects</h2>
            
            <div v-if="projects.length === 0" class="alert alert-info">
              No saved projects found. Create a new research project first.
            </div>
            
            <div v-else>
              <div class="card mb-4">
                <div class="card-header">Project List</div>
                <div class="card-body">
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>ID</th>
                          <th>Name</th>
                          <th>Created</th>
                          <th>Product Concept</th>
                          <th>Target Segment</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="project in projects" :key="project.id" @click="selectedProjectId = project.id" :class="{ 'table-primary': selectedProjectId === project.id }">
                          <td>{{ project.id }}</td>
                          <td>{{ project.name }}</td>
                          <td>{{ new Date(project.created_at).toLocaleString() }}</td>
                          <td>{{ project.product_concept.substring(0, 50) }}{{ project.product_concept.length > 50 ? '...' : '' }}</td>
                          <td>{{ project.target_segment.substring(0, 50) }}{{ project.target_segment.length > 50 ? '...' : '' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              <div class="card mb-4">
                <div class="card-header">Project Actions</div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <button @click="loadProject" class="btn btn-primary w-100" :disabled="!selectedProjectId">Load Selected Project</button>
                    </div>
                    <div class="col-md-6">
                      <button v-if="!confirmDelete" @click="confirmDelete = true" class="btn btn-danger w-100" :disabled="!selectedProjectId">Delete Selected Project</button>
                      <button v-else @click="deleteProject" class="btn btn-danger w-100">Confirm Deletion</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Footer -->
          <footer class="mt-5 mb-3 text-center">
            <hr>
            <p>Synthetic Market Research Engine - Powered by OpenAI GPT-4o</p>
          </footer>
        </div>
      </div>
    </div>
  `
};

// Create and mount the Vue app
createApp(App).mount('#app');