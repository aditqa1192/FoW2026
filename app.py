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
from agent.roadmap_agent import CourseRoadmapAgent, format_roadmap_summary

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
if 'course_roadmap' not in st.session_state:
    st.session_state.course_roadmap = None
if 'generation_in_progress' not in st.session_state:
    st.session_state.generation_in_progress = False
if 'validation_errors' not in st.session_state:
    st.session_state.validation_errors = []

def extract_course_parameters(prompt):
    """
    Extract course parameters from user prompt using enhanced natural language processing.
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
    prompt_lower = prompt.lower()
    
    # Extract topic - refined patterns with better ordering
    topic_patterns = [
        # Pattern 1: "X course/program/training for Y" - capture X before course keyword
        r'(?:create|generate|build|make|design|develop)\s+(?:a\s+)?([^\s]+(?:\s+[^\s]+)*?)\s+(?:course|class|training|program|curriculum)\s+for',
        
        # Pattern 2: "course/program on X" - preposition after course keyword
        r'(?:course|class|training|program|curriculum)\s+(?:on|about|regarding|covering)\s+([^\n,.;]+?)(?:\s+(?:for|over|duration|difficulty|that|which|with|lasting|taking)|[,.\n]|$)',
        
        # Pattern 3: "teach/learn X" - subject after action verb
        r'(?:teach|learn|study|master|understand)\s+(?:about\s+)?([^\n,.;]+?)(?:\s+(?:for|to|over|duration|in|within)|[,.\n]|$)',
        
        # Pattern 4: "create course on X" - with explicit preposition
        r'(?:create|generate|build|make|design|develop)\s+(?:a\s+)?(?:course|class|training|program)\s+(?:on|about|regarding|in)\s+([^\n,.;]+?)(?:\s+(?:for|over|duration)|[,.\n]|$)',
        
        # Pattern 5: Topic label format
        r'topic\s*[:\-]\s*([^\n,.;]+?)(?:\s+(?:for|over|duration)|[,.\n]|$)',
        r'subject\s*[:\-]\s*([^\n,.;]+?)(?:\s+(?:for|over|duration)|[,.\n]|$)',
        
        # Pattern 6: "I want to learn X" - conversational
        r'(?:i\s+)?(?:want|need|would like)\s+(?:to\s+)?(?:learn|study|create|take)\s+(?:a\s+)?(?:course\s+(?:on|in)\s+)?([^\n,.;]+?)(?:\s+(?:for|course|training)|[,.\n]|$)',
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            topic = match.group(1).strip()
            # Clean up common prefixes/suffixes
            topic = re.sub(r'^(?:a|an|the)\s+', '', topic, flags=re.IGNORECASE)
            topic = re.sub(r'\s+(?:course|class|training|program)$', '', topic, flags=re.IGNORECASE)
            # Remove audience-related words that might have been captured
            topic = re.sub(r'\s+(?:for|to|with)\s+.*$', '', topic, flags=re.IGNORECASE)
            if len(topic) > 3:  # Must be meaningful
                params['topic'] = topic
                break
    
    # Extract duration - more flexible
    duration_patterns = [
        r'(\d+)\s*(?:-|to)?\s*weeks?(?:\s+long)?',
        r'(?:duration|lasting|takes?|span(?:ning)?|over|in)\s*[:\-]?\s*(\d+)\s*weeks?',
        r'(?:for|across|throughout)\s+(\d+)\s*weeks?',
        r'(\d+)\s*week\s+(?:course|program|class)',
        r'(?:weekly|week by week)\s+(?:for\s+)?(\d+)\s+weeks?',
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            weeks = int(match.group(1))
            if 1 <= weeks <= 52:  # Sanity check
                params['duration_weeks'] = weeks
                break
    
    # Extract difficulty level - synonyms and variations
    difficulty_mappings = {
        'beginner': ['beginner', 'beginners', 'basic', 'introductory', 'intro', 'fundamental', 'elementary', 'starter', 'novice', 'entry level', 'entry-level', 'starting'],
        'intermediate': ['intermediate', 'mid level', 'mid-level', 'moderate', 'standard', 'regular', 'average'],
        'advanced': ['advanced', 'expert', 'professional', 'senior', 'high level', 'high-level', 'complex', 'sophisticated', 'in-depth', 'in depth', 'deep dive']
    }
    
    for level, keywords in difficulty_mappings.items():
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                params['difficulty'] = level
                break
        if params['difficulty']:
            break
    
    # Extract target audience - much more comprehensive
    audience_patterns = [
        # Direct patterns
        r'(?:for|aimed at|targeting|designed for|intended for)\s+([^\n,.;]+?)(?:\s+(?:who|that|with|wanting|interested|looking)|[,.\n]|$)',
        r'(?:target|target audience|audience)\s*[:\-]\s*([^\n,.;]+?)(?:[,.\n]|$)',
        # Professional/student indicators
        r'\b((?:college|university|high school|graduate|undergraduate|phd|doctoral|medical|engineering|business|law|nursing)\s+students?)\b',
        r'\b((?:software|web|data|machine learning|ai|cloud|mobile|frontend|backend|full stack|fullstack)\s+(?:developers?|engineers?|programmers?))\b',
        r'\b((?:aspiring|junior|senior|lead|staff|principal)\s+(?:developers?|engineers?|programmers?|professionals?))\b',
        r'\b((?:beginners?|novices?|experts?|professionals?|practitioners?|enthusiasts?|hobbyists?))\b',
        r'\b((?:managers?|leaders?|executives?|analysts?|consultants?|researchers?|scientists?))\b',
    ]
    
    for pattern in audience_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            audience = match.group(1).strip()
            # Clean up
            audience = re.sub(r'^(?:the\s+)?', '', audience)
            if len(audience) > 3:
                params['target_audience'] = audience
                break
    
    # Extract lessons per module
    lessons_patterns = [
        r'(\d+)\s*lessons?\s+(?:per|in\s+each|for\s+each)\s+module',
        r'(?:lessons per module|module lessons)\s*[:\-]?\s*(\d+)',
        r'each\s+module\s+(?:has|contains|includes)\s+(\d+)\s*lessons?',
        r'(\d+)\s*lessons?\s+(?:in|per)\s+(?:each|every)\s+module',
    ]
    
    for pattern in lessons_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            lessons = int(match.group(1))
            if 1 <= lessons <= 20:  # Sanity check
                params['lessons_per_module'] = lessons
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
    
    Just write naturally - the system will automatically extract:
    - Course topic
    - Duration (mention weeks)
    - Difficulty level (beginner/intermediate/advanced or synonyms)
    - Target audience (who it's for)
    - Lessons per module (optional)
    """)
    
    course_prompt = st.text_area(
        "Course Description",
        placeholder="""Examples of natural language input:

"Create a Data engineering course for college students. Should be intermediate level and last 6 weeks."

"I want to learn Python programming for data science. Make it 8 weeks for complete beginners."

"Build a Web development course for aspiring developers. Intermediate level, 6 weeks."

"Teach Machine learning to software engineers. Advanced level, 10 weeks."

"Generate a JavaScript fundamentals course for beginners over 4 weeks with 5 lessons per module."

"A basic introduction to Digital marketing for small business owners, lasting 5 weeks."
""",
        help="Just describe what you want in plain English - no special format needed!",
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
    **Natural Language Examples:**
    
    ✅ "Teach me React for 6 weeks"
    
    ✅ "I need a basic SQL course for beginners lasting 4 weeks"
    
    ✅ "Advanced Python for data scientists, 10 weeks"
    
    ✅ "Web design training for college students"
    
    ✅ "Create a course on cloud computing for professionals"
    
    **The system understands:**
    - Synonyms (basic=beginner, intro=introductory)
    - Various phrasings ("for X weeks", "lasting X weeks", "X week course")
    - Different audience descriptions
    - Natural conversational language
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
    
    export_col1, export_col2, export_col3, export_col4 = st.columns(4)
    
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
    
    with export_col4:
        # Generate roadmap button
        if st.button("🗺️ Generate Roadmap", use_container_width=True, type="secondary"):
            try:
                with st.spinner("🗺️ Generating course roadmap..."):
                    roadmap_agent = CourseRoadmapAgent(api_key=api_key, model=model)
                    
                    # Generate roadmap from course modules
                    roadmap = roadmap_agent.generate_roadmap_from_modules(
                        course_title=course['title'],
                        modules=course['modules'],
                        duration_weeks=course['duration_weeks'],
                        difficulty=course['difficulty_level'],
                        hours_per_week=5.0,
                        start_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    
                    st.session_state.course_roadmap = roadmap_agent.export_to_dict(roadmap)
                    st.success("✨ Roadmap generated successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error generating roadmap: {str(e)}")
                st.exception(e)
    
    # Display roadmap if generated
    if st.session_state.course_roadmap:
        st.divider()
        st.header("🗺️ Course Learning Roadmap")
        
        roadmap = st.session_state.course_roadmap
        
        # Roadmap summary
        with st.expander("📊 Roadmap Overview", expanded=True):
            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            
            with col_r1:
                st.metric("Duration", f"{roadmap['total_duration_weeks']} weeks")
            with col_r2:
                st.metric("Total Hours", f"{roadmap['total_estimated_hours']} hrs")
            with col_r3:
                st.metric("Modules", roadmap['total_modules'])
            with col_r4:
                st.metric("Milestones", len(roadmap['milestones']))
            
            if roadmap.get('start_date') and roadmap.get('end_date'):
                st.info(f"📅 **Timeline:** {roadmap['start_date']} to {roadmap['end_date']}")
            
            if roadmap.get('pacing_recommendations'):
                st.markdown("**💡 Pacing Recommendations:**")
                st.write(roadmap['pacing_recommendations'])
        
        # Weekly schedule
        with st.expander("📅 Weekly Schedule", expanded=True):
            for week in roadmap['weekly_schedule']:
                st.markdown(f"### {week['week_title']}")
                
                col_w1, col_w2 = st.columns([2, 1])
                
                with col_w1:
                    if week['topics']:
                        st.markdown("**Topics:**")
                        for topic in week['topics']:
                            st.write(f"• {topic}")
                    
                    if week['modules_covered']:
                        st.markdown("**Modules:**")
                        for module in week['modules_covered']:
                            st.write(f"📦 {module}")
                
                with col_w2:
                    st.metric("Estimated Hours", f"{week['estimated_hours']} hrs")
                    
                    if week['deliverables']:
                        st.markdown("**📝 Due:**")
                        for deliverable in week['deliverables']:
                            st.write(f"• {deliverable}")
                
                if week['milestones']:
                    st.success(f"🎯 Milestone: {week['milestones'][0]}")
                
                st.divider()
        
        # Milestones overview
        if roadmap['milestones']:
            with st.expander("🎯 Key Milestones"):
                for milestone in roadmap['milestones']:
                    milestone_type = milestone['type'].capitalize()
                    icon = {"quiz": "📝", "project": "🚀", "assignment": "✍️", "checkpoint": "✅"}.get(milestone['type'], "🎯")
                    
                    st.markdown(f"**Week {milestone['week']}: {icon} {milestone['title']}**")
                    st.write(f"_{milestone['description']}_")
                    st.write("")
        
        # Study tips
        if roadmap.get('study_tips'):
            with st.expander("💡 Study Tips for Success"):
                for idx, tip in enumerate(roadmap['study_tips'], 1):
                    st.write(f"{idx}. {tip}")
        
        # Roadmap export
        st.markdown("### Export Roadmap")
        roadmap_col1, roadmap_col2 = st.columns(2)
        
        with roadmap_col1:
            roadmap_json = json.dumps(roadmap, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download Roadmap (JSON)",
                data=roadmap_json,
                file_name=f"roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with roadmap_col2:
            # Create markdown roadmap
            roadmap_agent = CourseRoadmapAgent(api_key=api_key, model=model)
            from agent.roadmap_agent import CourseRoadmap
            roadmap_obj = CourseRoadmap(**roadmap)
            roadmap_markdown = roadmap_agent.format_roadmap_markdown(roadmap_obj)
            
            st.download_button(
                label="📝 Download Roadmap (Markdown)",
                data=roadmap_markdown,
                file_name=f"roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 1rem;">
    <p>Lilaq Course Content Agent | Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)
