# Synthetic Market Research Engine

A modern web application built with the MEVN stack (MongoDB, Express, Vue.js, Node.js) that uses AI to generate synthetic market research by creating realistic personas, simulating focus groups, and analyzing feedback for product concepts.

## Features

- **AI Persona Generation**: Create demographically and psychographically accurate personas based on your target segment
- **Focus Group Simulation**: Simulate realistic moderated discussions between personas about your product concept
- **Comprehensive Analysis**: Get insights on emotional tone, themes, objections, praise, and pricing sensitivity
- **Data Visualization**: Interactive charts and graphics to help understand research findings
- **Project Management**: Save, load, and manage your research projects
- **Token Usage Tracking**: Monitor API usage to control costs
- **Modern Web Interface**: Responsive UI built with Vue.js

## Requirements

- Node.js 20+
- Python 3.8+
- PostgreSQL database
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/elroy-galbraith/synthetic-market-research.git
   cd synthetic-market-research
   ```

2. Install Node.js dependencies:
   ```
   npm install
   ```

3. Install Python dependencies:
   ```
   pip install -r dependencies.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add the following environment variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     DATABASE_URL=your_postgresql_database_url
     ```

5. Start the backend server:
   ```
   cd backend
   node server.js
   ```

6. Start the frontend server:
   ```
   cd frontend
   node server.js
   ```

## Usage

1. Navigate to the application in your browser (default: http://localhost:5000)
2. Enter your OpenAI API key in the sidebar
3. Define your product concept, target segment, and research questions
4. Click "Generate Research" to start the process
5. Review the personas, focus group transcript, and analysis
6. Save your research project or download the results

## Project Structure

- `backend/`: Backend server and API
  - `server.js`: Express.js server
  - `scripts/`: Python scripts for AI functionality
  - `utils/`: Python utility modules
- `frontend/`: Vue.js frontend application
  - `index.html`: Main HTML file
  - `src/`: Vue components and services
  - `server.js`: Frontend static file server
- `utils/`: Shared utility modules
  - `persona_generator.py`: AI-powered persona creation
  - `focus_group.py`: Focus group simulation
  - `analysis.py`: Transcript analysis
  - `openai_service.py`: OpenAI API integration
  - `database.py`: Database operations

## License

All rights reserved.

## Acknowledgements

- OpenAI for providing the GPT-4o API
- Vue.js for the frontend framework
- Express.js for the backend server
- NLTK for additional sentiment analysis