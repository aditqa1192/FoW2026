"""
OKIR Course Content Agent - Streamlit UI
Interactive web interface for generating course content
"""

import streamlit as st
import os
from dotenv import load_dotenv
import json
from datetime import datetime

from agent import CourseContentAgent, generate_markdown_course, generate_html_course, format_course_summary

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="OKIR Course Content Agent",
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

# Header
st.markdown('<div class="main-header">📚 OKIR Course Content Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Course Content Generation</div>', unsafe_allow_html=True)

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Google API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Enter your Google API key. You can get one at https://makersuite.google.com/app/apikey"
    )
    
    # Model selection
    model = st.selectbox(
        "AI Model",
        ["gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemma-3-12b"],
        index=0,
        help="Select the Gemini model to use for generation"
    )
    
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
    st.header("🎯 Course Parameters")
    
    # Course topic
    course_topic = st.text_input(
        "Course Topic",
        placeholder="e.g., Python Programming for Beginners, Digital Marketing Fundamentals",
        help="Enter the main topic or subject of the course"
    )
    
    # Additional parameters
    col_a, col_b = st.columns(2)
    
    with col_a:
        duration_weeks = st.slider(
            "Duration (weeks)",
            min_value=1,
            max_value=16,
            value=4,
            help="How many weeks should the course run?"
        )
        
        difficulty = st.selectbox(
            "Difficulty Level",
            ["beginner", "intermediate", "advanced"],
            index=0,
            help="Target difficulty level for the course"
        )
    
    with col_b:
        target_audience = st.text_input(
            "Target Audience",
            value="general learners",
            placeholder="e.g., college students, professionals, hobbyists",
            help="Who is this course designed for?"
        )
        
        lessons_per_module = st.slider(
            "Lessons per Module",
            min_value=2,
            max_value=8,
            value=4,
            help="Number of lessons in each module"
        )
    
    st.divider()
    
    # Generate button
    generate_col, clear_col = st.columns([3, 1])
    
    with generate_col:
        generate_button = st.button(
            "🚀 Generate Course Content",
            type="primary",
            use_container_width=True,
            disabled=not course_topic or not api_key
        )
    
    with clear_col:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.course_content = None
            st.rerun()

with col2:
    st.header("💡 Quick Tips")
    st.info("""
    **For best results:**
    - Be specific with course topics
    - Adjust duration based on content depth
    - Match difficulty to audience
    - Review and customize generated content
    """)
    
    if st.session_state.course_content:
        st.success("✅ Course content generated successfully!")

# Generate course content
if generate_button:
    if not api_key:
        st.error("❌ Please provide a Google API key in the sidebar.")
    elif not course_topic:
        st.error("❌ Please enter a course topic.")
    else:
        try:
            with st.spinner("🤖 Generating course content... This may take a few minutes."):
                # Initialize agent
                agent = CourseContentAgent(api_key=api_key, model=model)
                
                # Generate course
                course = agent.generate_complete_course(
                    topic=course_topic,
                    duration_weeks=duration_weeks,
                    difficulty=difficulty,
                    target_audience=target_audience,
                    lessons_per_module=lessons_per_module
                )
                
                # Store in session state
                st.session_state.course_content = agent.export_to_dict(course)
                
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
    <p>OKIR Course Content Agent | Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)
