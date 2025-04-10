import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.openai_service import validate_api_key
from utils.persona_generator import generate_personas
from utils.focus_group import simulate_focus_group
from utils.analysis import analyze_transcript

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
                
                # Display personas
                st.subheader("Generated Personas")
                personas_df = pd.DataFrame(st.session_state.personas)
                st.dataframe(personas_df[["name", "age", "occupation", "background"]], use_container_width=True)
                
                # Step 2: Simulate focus group
                with st.spinner("Simulating focus group discussion..."):
                    st.session_state.transcript = simulate_focus_group(
                        st.session_state.personas,
                        product_concept,
                        questions
                    )
                    
                    # Display transcript
                    st.subheader("Focus Group Transcript")
                    st.markdown(st.session_state.transcript)
                    
                    # Step 3: Analyze transcript
                    with st.spinner("Analyzing focus group feedback..."):
                        st.session_state.analysis = analyze_transcript(
                            st.session_state.transcript,
                            product_concept,
                            questions
                        )
                        
                        # Display analysis
                        st.subheader("Analysis Results")
                        
                        # Create tabs for different analysis aspects
                        tab1, tab2, tab3, tab4 = st.tabs(["Emotional Tone", "Themes", "Feedback", "Pricing"])
                        
                        with tab1:
                            st.markdown("### Emotional Tone Analysis")
                            
                            # Create sentiment data for visualization
                            sentiments = st.session_state.analysis['emotional_tone']
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
                            st.markdown(f"**Summary**: {st.session_state.analysis['emotional_summary']}")
                        
                        with tab2:
                            st.markdown("### Key Themes")
                            
                            # Visualize themes
                            themes = st.session_state.analysis['themes']
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
                            for theme, description in st.session_state.analysis['theme_details'].items():
                                with st.expander(theme):
                                    st.write(description)
                        
                        with tab3:
                            st.markdown("### Objections & Praise")
                            
                            # Create columns for objections and praise
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### Objections")
                                for obj in st.session_state.analysis['objections']:
                                    st.warning(obj)
                            
                            with col2:
                                st.markdown("#### Praise")
                                for praise in st.session_state.analysis['praise']:
                                    st.success(praise)
                        
                        with tab4:
                            st.markdown("### Pricing Sensitivity")
                            
                            # Display pricing info
                            pricing_data = st.session_state.analysis['pricing']
                            
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
                        st.markdown(st.session_state.analysis['summary'])
                        
                        with st.expander("Recommendations"):
                            for rec in st.session_state.analysis['recommendations']:
                                st.markdown(f"- {rec}")
                        
                        # Download options
                        st.subheader("Download Results")
                        
                        # Create JSON of all results
                        import json
                        results = {
                            "product_concept": product_concept,
                            "target_segment": target_segment,
                            "research_questions": questions,
                            "personas": st.session_state.personas,
                            "transcript": st.session_state.transcript,
                            "analysis": st.session_state.analysis
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
                                data=st.session_state.transcript,
                                file_name="focus_group_transcript.txt",
                                mime="text/plain"
                            )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your inputs and try again, or validate your API key.")

# Footer
st.markdown("---")
st.markdown("Synthetic Market Research Engine - Powered by OpenAI GPT-4o")
