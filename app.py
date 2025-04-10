import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.openai_service import validate_api_key
from utils.persona_generator import generate_personas
from utils.focus_group import simulate_focus_group
from utils.analysis import analyze_transcript
from utils.database import save_research_project, get_research_projects, get_project_details, delete_project

# Set page configuration
st.set_page_config(
    page_title="Synthetic Market Research Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False
if 'personas' not in st.session_state:
    st.session_state.personas = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'active_page' not in st.session_state:
    st.session_state.active_page = "new_research"  # Options: "new_research", "saved_projects"
if 'loaded_project' not in st.session_state:
    st.session_state.loaded_project = None
if 'token_count' not in st.session_state:
    st.session_state.token_count = {
        "personas": 0,
        "focus_group": 0,
        "analysis": 0,
        "total": 0
    }

# Title and description
st.title("Synthetic Market Research Engine")
st.markdown("""
This tool helps you gather synthetic market research insights by:
1. Generating realistic personas based on your target segment
2. Simulating a focus group discussion about your concept
3. Analyzing feedback and providing actionable insights
""")

# API Key input section
with st.sidebar:
    st.subheader("OpenAI API Key")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password", help="Required for persona generation and focus group simulation")
    
    if api_key:
        # Set the API key as an environment variable
        os.environ["OPENAI_API_KEY"] = api_key
        
        if st.button("Validate API Key"):
            with st.spinner("Validating API key..."):
                is_valid, message = validate_api_key()
                if is_valid:
                    st.session_state.api_key_validated = True
                    st.success(message)
                else:
                    st.error(message)
    
    if st.session_state.api_key_validated:
        st.success("API Key validated! You can now use the application.")
        
        # Navigation
        st.sidebar.markdown("---")
        st.sidebar.subheader("Navigation")
        
        if st.sidebar.button("New Research", 
                           type="primary" if st.session_state.active_page == "new_research" else "secondary"):
            st.session_state.active_page = "new_research"
            st.session_state.loaded_project = None
            st.rerun()
            
        if st.sidebar.button("Saved Projects", 
                          type="primary" if st.session_state.active_page == "saved_projects" else "secondary"):
            st.session_state.active_page = "saved_projects"
            st.rerun()
            
        # Display token usage estimation
        st.sidebar.markdown("---")
        st.sidebar.subheader("Estimated Token Usage")
        st.sidebar.info(f"""
        **Current Session:**
        - Personas: {st.session_state.token_count['personas']}
        - Focus Group: {st.session_state.token_count['focus_group']}
        - Analysis: {st.session_state.token_count['analysis']}
        - **Total**: {st.session_state.token_count['total']}
        """)
        st.sidebar.caption("Token counts are approximate and used to estimate API costs")

# Main input form
with st.form("research_inputs"):
    st.subheader("Enter Research Parameters")
    
    # Input fields
    product_concept = st.text_area(
        "Product/Service Concept:", 
        placeholder="E.g., an app that teaches Japanese through memes",
        help="Describe your product or service idea in detail"
    )
    
    target_segment = st.text_area(
        "Target Segment:", 
        placeholder="E.g., Nigerian Gen Z college students, or urban side-hustlers",
        help="Describe your target demographic or psychographic segment"
    )
    
    st.subheader("Research Questions")
    st.markdown("Enter up to 5 questions you want to ask the focus group")
    
    # Create 5 question input fields
    questions = []
    for i in range(5):
        placeholder_text = ""
        if i == 0:
            placeholder_text = "E.g., Would you use this product/service?"
        elif i == 1:
            placeholder_text = "E.g., What price feels fair for this offering?"
        
        question = st.text_input(f"Question {i+1}:", placeholder=placeholder_text)
        if question:
            questions.append(question)
    
    # Submit button
    submit_disabled = not st.session_state.api_key_validated
    submit_button = st.form_submit_button(
        "Generate Research", 
        disabled=submit_disabled,
        help="First validate your API key in the sidebar" if submit_disabled else None
    )

# Function to estimate token count for a text
def estimate_tokens(text):
    # Roughly 4 chars per token for English text
    return len(text) // 4

# Function to display research results
def display_research_results(personas, transcript, analysis, product_concept, questions):
    # Display personas
    st.subheader("Generated Personas")
    personas_df = pd.DataFrame(personas)
    st.dataframe(personas_df[["name", "age", "occupation", "background"]], use_container_width=True)
    
    # Display transcript
    st.subheader("Focus Group Transcript")
    st.markdown(transcript)
    
    # Display analysis results
    st.subheader("Analysis Results")
    
    # Create tabs for different analysis aspects
    tab1, tab2, tab3, tab4 = st.tabs(["Emotional Tone", "Themes", "Feedback", "Pricing"])
    
    with tab1:
        st.markdown("### Emotional Tone Analysis")
        
        # Create sentiment data for visualization
        sentiments = analysis['emotional_tone']
        sentiment_df = pd.DataFrame({
            'Sentiment': list(sentiments.keys()),
            'Score': list(sentiments.values())
        })
        
        # Create sentiment visualization
        fig = px.bar(
            sentiment_df, 
            x='Sentiment', 
            y='Score', 
            color='Score',
            color_continuous_scale=['red', 'yellow', 'green'],
            title="Emotional Response Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary of emotional tone
        st.markdown(f"**Summary**: {analysis['emotional_summary']}")
    
    with tab2:
        st.markdown("### Key Themes")
        
        # Visualize themes
        themes = analysis['themes']
        theme_df = pd.DataFrame({
            'Theme': list(themes.keys()),
            'Frequency': list(themes.values())
        })
        theme_df = theme_df.sort_values('Frequency', ascending=False)
        
        fig = px.pie(
            theme_df, 
            names='Theme', 
            values='Frequency',
            title="Key Discussion Themes"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display theme descriptions
        st.markdown("#### Theme Details")
        for theme, description in analysis['theme_details'].items():
            with st.expander(theme):
                st.write(description)
    
    with tab3:
        st.markdown("### Objections & Praise")
        
        # Create columns for objections and praise
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Objections")
            for obj in analysis['objections']:
                st.warning(obj)
        
        with col2:
            st.markdown("#### Praise")
            for praise in analysis['praise']:
                st.success(praise)
    
    with tab4:
        st.markdown("### Pricing Sensitivity")
        
        # Display pricing info
        pricing_data = analysis['pricing']
        
        # Create gauge for price sensitivity
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = pricing_data['sensitivity'] * 10,
            title = {'text': "Price Sensitivity (0-10)"},
            gauge = {
                'axis': {'range': [0, 10]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 3.33], 'color': "green"},
                    {'range': [3.33, 6.66], 'color': "yellow"},
                    {'range': [6.66, 10], 'color': "red"}
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        # Display price range and notes
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Suggested Minimum Price", f"${pricing_data['min_price']}")
        with col2:
            st.metric("Suggested Maximum Price", f"${pricing_data['max_price']}")
        
        st.markdown("#### Pricing Notes")
        st.write(pricing_data['notes'])
        
    # Final summary and recommendations
    st.subheader("Summary & Recommendations")
    st.markdown(analysis['summary'])
    
    with st.expander("Recommendations"):
        for rec in analysis['recommendations']:
            st.markdown(f"- {rec}")
    
    # Download options
    st.subheader("Download Results")
    
    # Create JSON of all results
    import json
    results = {
        "product_concept": product_concept,
        "target_segment": st.session_state.loaded_project['target_segment'] if st.session_state.loaded_project else target_segment,
        "research_questions": questions,
        "personas": personas,
        "transcript": transcript,
        "analysis": analysis
    }
    
    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Complete Results (JSON)",
            data=json.dumps(results, indent=2),
            file_name="market_research_results.json",
            mime="application/json"
        )
    
    with col2:
        st.download_button(
            "Download Transcript (TXT)",
            data=transcript,
            file_name="focus_group_transcript.txt",
            mime="text/plain"
        )
    
    # Save project option
    st.subheader("Save Research Project")
    project_name = st.text_input("Project Name:", 
                                placeholder="E.g., Japanese Learning App Research",
                                help="Enter a name to identify this research project")
    
    if st.button("Save Project to Database", disabled=not project_name):
        with st.spinner("Saving project to database..."):
            try:
                project_id = save_research_project(
                    name=project_name,
                    product_concept=product_concept,
                    target_segment=st.session_state.loaded_project['target_segment'] if st.session_state.loaded_project else target_segment,
                    research_questions=questions,
                    personas=personas,
                    transcript=transcript,
                    analysis=analysis
                )
                st.success(f"Project saved successfully! Project ID: {project_id}")
            except Exception as e:
                st.error(f"Error saving project: {str(e)}")

# Show different pages based on active_page
if st.session_state.active_page == "saved_projects":
    st.header("Saved Research Projects")
    
    try:
        # Get all saved projects
        projects = get_research_projects()
        
        if not projects:
            st.info("No saved projects found. Create a new research project first.")
        else:
            # Display projects as a table
            projects_df = pd.DataFrame(projects)
            projects_df['created_at'] = pd.to_datetime(projects_df['created_at'])
            projects_df = projects_df.sort_values('created_at', ascending=False)
            
            # Convert to a more readable format for display
            display_df = projects_df.copy()
            display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            display_df['product_concept'] = display_df['product_concept'].str[:50] + '...'
            display_df['target_segment'] = display_df['target_segment'].str[:50] + '...'
            
            st.dataframe(
                display_df[['id', 'name', 'created_at', 'product_concept', 'target_segment']], 
                use_container_width=True
            )
            
            # Project selection
            selected_project_id = st.selectbox(
                "Select a project to view:", 
                options=projects_df['id'].tolist(),
                format_func=lambda x: f"{x}: {projects_df[projects_df['id'] == x]['name'].values[0]}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Load Selected Project", key="load_project"):
                    with st.spinner("Loading project..."):
                        # Get project details
                        project_data = get_project_details(selected_project_id)
                        if project_data:
                            st.session_state.loaded_project = project_data
                            st.session_state.personas = project_data['personas']
                            st.session_state.transcript = project_data['transcript']
                            st.session_state.analysis = project_data['analysis']
                            st.session_state.active_page = "new_research"
                            st.rerun()
                        else:
                            st.error("Could not load project. Please try again.")
            
            with col2:
                if st.button("Delete Selected Project", key="delete_project"):
                    if st.checkbox("Confirm deletion?", key="confirm_delete"):
                        with st.spinner("Deleting project..."):
                            success = delete_project(selected_project_id)
                            if success:
                                st.success("Project deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Could not delete project. Please try again.")
                
    except Exception as e:
        st.error(f"Error loading projects: {str(e)}")

# New Research Page
elif st.session_state.active_page == "new_research":
    # If a project is loaded, display its data
    if st.session_state.loaded_project:
        st.header(f"Loaded Project: {st.session_state.loaded_project['name']}")
        
        # Display the research data
        display_research_results(
            st.session_state.personas,
            st.session_state.transcript,
            st.session_state.analysis,
            st.session_state.loaded_project['product_concept'],
            st.session_state.loaded_project['research_questions']
        )
        
        # Button to clear loaded project and start new research
        if st.button("Start New Research", key="clear_loaded_project"):
            st.session_state.loaded_project = None
            st.session_state.personas = None
            st.session_state.transcript = None
            st.session_state.analysis = None
            st.rerun()
    
    # If no project is loaded, show the research form
    else:
        # Process form submission
        if submit_button:
            # Validate inputs
            if not product_concept:
                st.error("Please enter a product/service concept")
            elif not target_segment:
                st.error("Please enter a target segment")
            elif not questions:
                st.error("Please enter at least one research question")
            else:
                # Step 1: Generate personas
                with st.spinner("Generating personas based on your target segment..."):
                    try:
                        st.session_state.personas = generate_personas(target_segment)
                        
                        # Estimate token usage for personas
                        persona_tokens = estimate_tokens(str(st.session_state.personas))
                        st.session_state.token_count['personas'] = persona_tokens
                        st.session_state.token_count['total'] += persona_tokens
                        
                        # Step 2: Simulate focus group
                        with st.spinner("Simulating focus group discussion..."):
                            st.session_state.transcript = simulate_focus_group(
                                st.session_state.personas,
                                product_concept,
                                questions
                            )
                            
                            # Estimate token usage for focus group
                            focus_group_tokens = estimate_tokens(st.session_state.transcript)
                            st.session_state.token_count['focus_group'] = focus_group_tokens
                            st.session_state.token_count['total'] += focus_group_tokens
                            
                            # Step 3: Analyze transcript
                            with st.spinner("Analyzing focus group feedback..."):
                                st.session_state.analysis = analyze_transcript(
                                    st.session_state.transcript,
                                    product_concept,
                                    questions
                                )
                                
                                # Estimate token usage for analysis
                                analysis_tokens = estimate_tokens(str(st.session_state.analysis))
                                st.session_state.token_count['analysis'] = analysis_tokens
                                st.session_state.token_count['total'] += analysis_tokens
                                
                                # Display the research results
                                display_research_results(
                                    st.session_state.personas,
                                    st.session_state.transcript,
                                    st.session_state.analysis,
                                    product_concept,
                                    questions
                                )
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.error("Please check your inputs and try again, or validate your API key.")

# Footer
st.markdown("---")
st.markdown("Synthetic Market Research Engine - Powered by OpenAI GPT-4o")
