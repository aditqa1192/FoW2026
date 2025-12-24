"""
Lilaq Course Content Agent - Streamlit UI
Interactive web interface for generating course content
"""

import streamlit as st
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import re

from agent import CourseContentAgent, generate_markdown_course, generate_html_course, format_course_summary
from agent.course_agent_langchain import CourseContentAgentLangChain

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Lilaq Course Content Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'course_content' not in st.session_state:
    st.session_state.course_content = None
if 'generation_in_progress' not in st.session_state:
    st.session_state.generation_in_progress = False
if 'validation_errors' not in st.session_state:
    st.session_state.validation_errors = []

def extract_course_parameters(prompt):
    """
    Extract course parameters from user prompt.
    Returns a dictionary with extracted parameters and a list of missing required fields.
    """
    params = {
        'topic': None,
        'duration_weeks': None,
        'difficulty': None,
        'target_audience': None,
        'lessons_per_module': None
    }
    
    missing_fields = []
    
    # Extract topic (usually the first significant phrase or after keywords)
    topic_patterns = [
        r'course (?:on|about|for|in)\s+([^\n,.]+)',
        r'(?:create|generate|build)\s+(?:a\s+)?course\s+(?:on|about|for|in)\s+([^\n,.]+)',
        r'topic:\s*([^\n,.]+)',
        r'^([^.\n]+?)(?:\s+course|\s+for|\s+duration|\s+difficulty|$)'
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            params['topic'] = match.group(1).strip()
            break
    
    # Extract duration in weeks
    duration_patterns = [
        r'(\d+)\s*weeks?',
        r'duration:\s*(\d+)\s*weeks?',
        r'over\s+(\d+)\s*weeks?',
        r'for\s+(\d+)\s*weeks?'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            params['duration_weeks'] = int(match.group(1))
            break
    
    # Extract difficulty level
    difficulty_keywords = ['beginner', 'intermediate', 'advanced']
    for level in difficulty_keywords:
        if re.search(rf'\b{level}\b', prompt, re.IGNORECASE):
            params['difficulty'] = level
            break
    
    # Extract target audience
    audience_patterns = [
        r'for\s+([^,.\n]+?)\s+(?:students|learners|professionals|people)',
        r'target audience:\s*([^\n,.]+)',
        r'audience:\s*([^\n,.]+)',
        r'aimed at\s+([^\n,.]+)'
    ]
    
    for pattern in audience_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            params['target_audience'] = match.group(1).strip()
            break
    
    # Extract lessons per module
    lessons_patterns = [
        r'(\d+)\s*lessons?\s+per\s+module',
        r'lessons per module:\s*(\d+)',
        r'(\d+)\s*lessons?\s+in\s+each\s+module'
    ]
    
    for pattern in lessons_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            params['lessons_per_module'] = int(match.group(1))
            break
    
    # Set defaults for optional parameters
    if params['duration_weeks'] is None:
        params['duration_weeks'] = 4
        
    if params['difficulty'] is None:
        params['difficulty'] = 'beginner'
        
    if params['target_audience'] is None:
        params['target_audience'] = 'general learners'
        
    if params['lessons_per_module'] is None:
        params['lessons_per_module'] = 4
    
    # Check for required fields
    if not params['topic']:
        missing_fields.append('Course Topic')
    
    return params, missing_fields

# Header
st.markdown('<div class="main-header">📚 Lilaq Course Content Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Course Content Generation</div>', unsafe_allow_html=True)

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Read API key and model from environment variables
    api_key = os.getenv("GOOGLE_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Display current configuration (read-only)
    st.info(f"""**Current Configuration:**
    
🤖 **Model:** {model}
🔑 **API Key:** {"✅ Configured" if api_key else "❌ Not Set"}

*Configure via .env file*
    """)
    
    if not api_key:
        st.error("⚠️ API Key not configured. Please set GOOGLE_API_KEY in .env file.")
    
    st.divider()
    
    st.header("📖 About")
    st.markdown("""
    This agent generates comprehensive course content including:
    - Course outline and structure
    - Detailed modules and lessons
    - Learning objectives
    - Activities and assessments
    - Key takeaways
    
    Simply enter a course topic and customize the parameters to get started!
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Course Requirements")
    
    # Prompt-based input
    st.markdown("""
    **Describe your course requirements in natural language:**
    
    You can include:
    - Course topic (required)
    - Duration in weeks (optional, default: 4 weeks)
    - Difficulty level: beginner, intermediate, or advanced (optional, default: beginner)
    - Target audience (optional, default: general learners)
    - Lessons per module (optional, default: 4)
    """)
    
    course_prompt = st.text_area(
        "Course Description",
        placeholder="""Example:
Create a course on Python Programming for Beginners.
Duration: 6 weeks
Difficulty: beginner
Target audience: college students
4 lessons per module""",
        help="Describe your course requirements in natural language",
        height=200
    )
    
    # Validate button
    if st.button("🔍 Validate Requirements", type="secondary"):
        if course_prompt:
            params, missing = extract_course_parameters(course_prompt)
            st.session_state.validation_errors = missing
            
            if not missing:
                st.success("✅ All required parameters detected!")
                st.markdown(f"""
                **Extracted Parameters:**
                - **Topic:** {params['topic']}
                - **Duration:** {params['duration_weeks']} weeks
                - **Difficulty:** {params['difficulty']}
                - **Target Audience:** {params['target_audience']}
                - **Lessons per Module:** {params['lessons_per_module']}
                """)
            else:
                st.error(f"❌ Missing required information: {', '.join(missing)}")
                st.warning("Please update your description to include all required details.")
        else:
            st.warning("⚠️ Please enter course requirements first.")
    
    st.divider()
    
    # Display validation errors if any
    if st.session_state.validation_errors:
        st.error(f"⚠️ Missing required information: {', '.join(st.session_state.validation_errors)}")
    
    # Generate button
    generate_col, clear_col = st.columns([3, 1])
    
    with generate_col:
        generate_button = st.button(
            "🚀 Generate Course Content",
            type="primary",
            use_container_width=True,
            disabled=not course_prompt or not api_key
        )
    
    with clear_col:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.course_content = None
            st.rerun()

with col2:
    st.header("💡 Quick Tips")
    st.info("""
    **For best results:**
    - Clearly state the course topic
    - Mention duration if you have a preference
    - Specify difficulty level (beginner/intermediate/advanced)
    - Describe your target audience
    - Use natural language - be conversational!
    
    **Example:**
    "Create a 6-week intermediate course on Machine Learning for software developers with 5 lessons per module"
    """)
    
    if st.session_state.course_content:
        st.success("✅ Course content generated successfully!")

# Generate course content
if generate_button:
    if not api_key:
        st.error("❌ Please provide a Google API key in the sidebar.")
    elif not course_prompt:
        st.error("❌ Please enter course requirements.")
    else:
        # Extract parameters from prompt
        params, missing = extract_course_parameters(course_prompt)
        st.session_state.validation_errors = missing
        
        if missing:
            st.error(f"❌ Missing required information: {', '.join(missing)}")
            st.warning("Please update your course description to include all required details and try again.")
        else:
            try:
                with st.spinner("🤖 Generating course content... This may take a few minutes."):
                    # Initialize LangChain agent
                    agent = CourseContentAgentLangChain(api_key=api_key, model=model)
                    
                    # Generate course
                    course = agent.generate_complete_course(
                        topic=params['topic'],
                        duration_weeks=params['duration_weeks'],
                        difficulty=params['difficulty'],
                        target_audience=params['target_audience'],
                        lessons_per_module=params['lessons_per_module']
                    )
                    
                    # Store in session state
                    st.session_state.course_content = agent.export_to_dict(course)
                    st.session_state.validation_errors = []
                    
                    st.success("✨ Course content generated successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error generating course: {str(e)}")
                st.exception(e)

# Display generated content
if st.session_state.course_content:
    st.divider()
    st.header("📋 Generated Course Content")
    
    course = st.session_state.course_content
    
    # Summary
    with st.expander("📊 Course Summary", expanded=True):
        st.code(format_course_summary(course), language=None)
    
    # Course overview
    with st.expander("📚 Course Overview", expanded=True):
        st.subheader(course['title'])
        st.write(course['description'])
        
        col_overview_a, col_overview_b = st.columns(2)
        
        with col_overview_a:
            st.markdown("**Target Audience:**")
            st.write(course['target_audience'])
            
            st.markdown("**Difficulty:**")
            st.write(course['difficulty_level'].title())
            
            st.markdown("**Duration:**")
            st.write(f"{course['duration_weeks']} weeks")
        
        with col_overview_b:
            st.markdown("**Prerequisites:**")
            for prereq in course['prerequisites']:
                st.write(f"- {prereq}")
            
            st.markdown("**Learning Outcomes:**")
            for outcome in course['learning_outcomes'][:3]:
                st.write(f"- {outcome}")
            if len(course['learning_outcomes']) > 3:
                st.write(f"- ...and {len(course['learning_outcomes']) - 3} more")
    
    # Modules and lessons
    for module_idx, module in enumerate(course['modules'], 1):
        with st.expander(f"📦 Module {module_idx}: {module['title']}"):
            st.write(f"**Description:** {module['description']}")
            st.write(f"**Duration:** {module['duration_hours']} hours")
            
            for lesson_idx, lesson in enumerate(module['lessons'], 1):
                st.markdown(f"### Lesson {module_idx}.{lesson_idx}: {lesson['title']}")
                st.write(f"⏱️ Duration: {lesson['duration_minutes']} minutes")
                
                # Learning objectives
                st.markdown("**🎯 Learning Objectives:**")
                for obj in lesson['learning_objectives']:
                    st.write(f"- {obj}")
                
                # Content
                with st.container():
                    st.markdown("**📖 Content:**")
                    st.write(lesson['content'])
                
                # Key points in columns
                st.markdown("**🔑 Key Points:**")
                key_cols = st.columns(2)
                for i, point in enumerate(lesson['key_points']):
                    with key_cols[i % 2]:
                        st.write(f"• {point}")
                
                # Activities
                st.markdown("**✏️ Activities:**")
                for i, activity in enumerate(lesson['activities'], 1):
                    st.write(f"{i}. {activity}")
                
                # Assessment
                with st.container():
                    st.markdown("**📝 Assessment:**")
                    for i, q in enumerate(lesson['assessment_questions'], 1):
                        st.info(f"**Q{i}:** {q.get('question', 'N/A')}")
                        with st.expander("Show Answer"):
                            st.write(q.get('answer', 'N/A'))
                
                if lesson_idx < len(module['lessons']):
                    st.divider()
    
    # Export options
    st.divider()
    st.header("💾 Export Options")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # JSON export
        json_data = json.dumps(course, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download as JSON",
            data=json_data,
            file_name=f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with export_col2:
        # Markdown export
        markdown_data = generate_markdown_course(course)
        st.download_button(
            label="📝 Download as Markdown",
            data=markdown_data,
            file_name=f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with export_col3:
        # HTML export
        html_data = generate_html_course(course)
        st.download_button(
            label="🌐 Download as HTML",
            data=html_data,
            file_name=f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>Lilaq Course Content Agent | Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)
