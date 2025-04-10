# Synthetic Market Research Engine

A Streamlit-based application that uses AI to generate synthetic market research by creating realistic personas, simulating focus groups, and analyzing feedback for product concepts.

## Features

- **AI Persona Generation**: Create demographically and psychographically accurate personas based on your target segment
- **Focus Group Simulation**: Simulate realistic moderated discussions between personas about your product concept
- **Comprehensive Analysis**: Get insights on emotional tone, themes, objections, praise, and pricing sensitivity
- **Data Visualization**: Interactive charts and graphics to help understand research findings
- **Project Management**: Save, load, and manage your research projects
- **Token Usage Tracking**: Monitor API usage to control costs

## Requirements

- Python 3.8+
- PostgreSQL database
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/elroy-galbraith/synthetic-market-research.git
   cd synthetic-market-research
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add the following environment variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     DATABASE_URL=your_postgresql_database_url
     ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Enter your OpenAI API key in the sidebar
2. Define your product concept, target segment, and research questions
3. Click "Generate Research" to start the process
4. Review the personas, focus group transcript, and analysis
5. Save your research project or download the results

## Project Structure

- `app.py`: Main Streamlit application
- `utils/`: Utility modules
  - `persona_generator.py`: AI-powered persona creation
  - `focus_group.py`: Focus group simulation
  - `analysis.py`: Transcript analysis
  - `openai_service.py`: OpenAI API integration
  - `database.py`: Database operations

## License

MIT

## Acknowledgements

- OpenAI for providing the GPT-4o API
- Streamlit for the web application framework
- NLTK for additional sentiment analysis