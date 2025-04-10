import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Get database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class ResearchProject(Base):
    """Model for research projects"""
    __tablename__ = "research_projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    product_concept = Column(Text, nullable=False)
    target_segment = Column(Text, nullable=False)
    
    # Relationships
    personas = relationship("Persona", back_populates="project", cascade="all, delete-orphan")
    questions = relationship("ResearchQuestion", back_populates="project", cascade="all, delete-orphan")
    transcripts = relationship("Transcript", back_populates="project", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")

class Persona(Base):
    """Model for personas"""
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    occupation = Column(String(100))
    background = Column(Text)
    interests = Column(Text)
    media_consumption = Column(Text)
    values = Column(Text)
    spending_habits = Column(Text)
    pain_points = Column(Text)
    communication_style = Column(Text)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="personas")

class ResearchQuestion(Base):
    """Model for research questions"""
    __tablename__ = "research_questions"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    question_text = Column(Text, nullable=False)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="questions")

class Transcript(Base):
    """Model for focus group transcripts"""
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text, nullable=False)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="transcripts")

class Analysis(Base):
    """Model for analysis results"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    emotional_tone = Column(JSON)
    emotional_summary = Column(Text)
    themes = Column(JSON)
    theme_details = Column(JSON)
    objections = Column(JSON)
    praise = Column(JSON)
    pricing = Column(JSON)
    participant_alignment = Column(JSON)
    summary = Column(Text)
    recommendations = Column(JSON)
    
    # Relationships
    project = relationship("ResearchProject", back_populates="analyses")

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def save_research_project(name, product_concept, target_segment, research_questions, personas, transcript, analysis):
    """
    Save a complete research project to the database.
    
    Args:
        name (str): Name of the research project
        product_concept (str): Description of the product or service
        target_segment (str): Description of the target segment
        research_questions (list): List of research question strings
        personas (list): List of persona dictionaries
        transcript (str): Focus group transcript
        analysis (dict): Analysis results
        
    Returns:
        int: ID of the created research project
    """
    session = Session()
    
    try:
        # Create research project
        project = ResearchProject(
            name=name,
            product_concept=product_concept,
            target_segment=target_segment
        )
        session.add(project)
        session.flush()  # Generate ID for the project
        
        # Add research questions
        for question in research_questions:
            q = ResearchQuestion(
                project_id=project.id,
                question_text=question
            )
            session.add(q)
        
        # Add personas
        for persona_data in personas:
            persona = Persona(
                project_id=project.id,
                name=persona_data.get('name', ''),
                age=persona_data.get('age', 0),
                occupation=persona_data.get('occupation', ''),
                background=persona_data.get('background', ''),
                interests=persona_data.get('interests and hobbies', ''),
                media_consumption=persona_data.get('media consumption habits', ''),
                values=persona_data.get('values and motivations', ''),
                spending_habits=persona_data.get('spending habits and income level', ''),
                pain_points=persona_data.get('pain points relevant to product research', ''),
                communication_style=persona_data.get('communication style', '')
            )
            session.add(persona)
        
        # Add transcript
        session.add(Transcript(
            project_id=project.id,
            content=transcript
        ))
        
        # Add analysis
        session.add(Analysis(
            project_id=project.id,
            emotional_tone=analysis.get('emotional_tone', {}),
            emotional_summary=analysis.get('emotional_summary', ''),
            themes=analysis.get('themes', {}),
            theme_details=analysis.get('theme_details', {}),
            objections=analysis.get('objections', []),
            praise=analysis.get('praise', []),
            pricing=analysis.get('pricing', {}),
            participant_alignment=analysis.get('participant_alignment', {}),
            summary=analysis.get('summary', ''),
            recommendations=analysis.get('recommendations', [])
        ))
        
        session.commit()
        return project.id
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()

def get_research_projects():
    """
    Get all research projects from the database.
    
    Returns:
        list: List of project dictionaries with basic info
    """
    session = Session()
    
    try:
        projects = session.query(ResearchProject).order_by(ResearchProject.created_at.desc()).all()
        return [
            {
                'id': project.id,
                'name': project.name,
                'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'product_concept': project.product_concept,
                'target_segment': project.target_segment
            }
            for project in projects
        ]
    
    finally:
        session.close()

def get_project_details(project_id):
    """
    Get complete details of a research project.
    
    Args:
        project_id (int): ID of the research project
        
    Returns:
        dict: Complete project data including personas, transcript, and analysis
    """
    session = Session()
    
    try:
        # Get basic project info
        project = session.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            return None
        
        # Get research questions
        questions = [q.question_text for q in project.questions]
        
        # Get personas
        personas = []
        for p in project.personas:
            persona = {
                'name': p.name,
                'age': p.age,
                'occupation': p.occupation,
                'background': p.background,
                'interests and hobbies': p.interests,
                'media consumption habits': p.media_consumption,
                'values and motivations': p.values,
                'spending habits and income level': p.spending_habits,
                'pain points relevant to product research': p.pain_points,
                'communication style': p.communication_style
            }
            personas.append(persona)
        
        # Get transcript
        transcript = project.transcripts[0].content if project.transcripts else ""
        
        # Get analysis
        analysis = {}
        if project.analyses:
            analysis_obj = project.analyses[0]
            analysis = {
                'emotional_tone': analysis_obj.emotional_tone,
                'emotional_summary': analysis_obj.emotional_summary,
                'themes': analysis_obj.themes,
                'theme_details': analysis_obj.theme_details,
                'objections': analysis_obj.objections,
                'praise': analysis_obj.praise,
                'pricing': analysis_obj.pricing,
                'participant_alignment': analysis_obj.participant_alignment,
                'summary': analysis_obj.summary,
                'recommendations': analysis_obj.recommendations
            }
        
        # Compile the complete project data
        project_data = {
            'id': project.id,
            'name': project.name,
            'created_at': project.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'product_concept': project.product_concept,
            'target_segment': project.target_segment,
            'research_questions': questions,
            'personas': personas,
            'transcript': transcript,
            'analysis': analysis
        }
        
        return project_data
    
    finally:
        session.close()

def delete_project(project_id):
    """
    Delete a research project.
    
    Args:
        project_id (int): ID of the project to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    session = Session()
    
    try:
        project = session.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            return False
        
        session.delete(project)
        session.commit()
        return True
    
    except Exception:
        session.rollback()
        return False
    
    finally:
        session.close()

# Initialize the database when this module is imported
init_db()