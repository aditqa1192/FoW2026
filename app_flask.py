"""
Lilaq Course Content Agent - Flask Web Application
HTML-based web interface for generating course content
"""

import os
import logging
import json
from datetime import datetime
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv

from agent import CourseContentAgent, generate_markdown_course, generate_html_course, format_course_summary
from agent.course_agent_langchain import CourseContentAgentLangChain
from agent.roadmap_agent import CourseRoadmapAgent, CourseRoadmap, format_roadmap_summary
from utils.logger_config import setup_logging
from utils.extract_params import extract_course_parameters

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(log_dir="logs", log_level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting Lilaq Course Content Agent Flask application")

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates/web',
            static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'lilaq-course-agent-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Store course data in-memory (for demo purposes)
# In production, use a proper database or session management
course_storage = {
    'course_content': None,
    'course_roadmap': None
}


@app.route('/')
def index():
    """Render the main page"""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    config = {
        'model': model,
        'api_key_configured': bool(api_key)
    }
    
    return render_template('index.html', config=config)


@app.route('/api/validate', methods=['POST'])
def validate_requirements():
    """Validate course requirements from user input"""
    try:
        data = request.get_json()
        course_prompt = data.get('prompt', '')
        
        if not course_prompt:
            return jsonify({
                'success': False,
                'error': 'Please enter course requirements'
            }), 400
        
        # Extract parameters
        params, missing = extract_course_parameters(course_prompt)
        
        return jsonify({
            'success': True,
            'params': params,
            'missing': missing,
            'is_valid': len(missing) == 0
        })
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-course', methods=['POST'])
def generate_course():
    """Generate course content"""
    try:
        data = request.get_json()
        course_prompt = data.get('prompt', '')
        
        api_key = os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured. Please set GOOGLE_API_KEY in .env file.'
            }), 500
        
        if not course_prompt:
            return jsonify({
                'success': False,
                'error': 'Please enter course requirements'
            }), 400
        
        # Extract parameters
        params, missing = extract_course_parameters(course_prompt)
        
        if missing:
            return jsonify({
                'success': False,
                'error': f"Missing required information: {', '.join(missing)}"
            }), 400
        
        logger.info(f"Starting course generation for topic: {params['topic']}")
        logger.debug(f"Generation parameters: {params}")
        
        # Initialize agent and generate course
        agent = CourseContentAgentLangChain(api_key=api_key, model=model)
        
        course = agent.generate_complete_course(
            topic=params['topic'],
            duration_weeks=params['duration_weeks'],
            difficulty=params['difficulty'],
            target_audience=params['target_audience'],
            lessons_per_module=params['lessons_per_module']
        )
        
        # Store course content
        course_dict = agent.export_to_dict(course)
        course_storage['course_content'] = course_dict
        
        logger.info("Course content generated successfully")
        
        return jsonify({
            'success': True,
            'course': course_dict
        })
        
    except Exception as e:
        logger.error(f"Error generating course: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-roadmap', methods=['POST'])
def generate_roadmap():
    """Generate course roadmap"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            }), 500
        
        course = course_storage.get('course_content')
        if not course:
            return jsonify({
                'success': False,
                'error': 'Please generate course content first'
            }), 400
        
        logger.info(f"Starting roadmap generation for course: {course['title']}")
        
        # Generate roadmap
        roadmap_agent = CourseRoadmapAgent(api_key=api_key, model=model)
        
        roadmap = roadmap_agent.generate_roadmap_from_modules(
            course_title=course['title'],
            modules=course['modules'],
            duration_weeks=course['duration_weeks'],
            difficulty=course['difficulty_level'],
            hours_per_week=5.0,
            start_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Store roadmap
        roadmap_dict = roadmap_agent.export_to_dict(roadmap)
        course_storage['course_roadmap'] = roadmap_dict
        
        # Generate summary table
        summary_table = roadmap_agent.generate_summary_table(roadmap)
        
        logger.info("Roadmap generated successfully")
        
        return jsonify({
            'success': True,
            'roadmap': roadmap_dict,
            'summary_table': summary_table
        })
        
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/<format>', methods=['GET'])
def export_course(format):
    """Export course in various formats"""
    try:
        course = course_storage.get('course_content')
        if not course:
            return jsonify({
                'success': False,
                'error': 'No course content to export'
            }), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"course_{timestamp}.json"
            data = json.dumps(course, indent=2, ensure_ascii=False)
            mimetype = 'application/json'
            
        elif format == 'markdown':
            filename = f"course_{timestamp}.md"
            data = generate_markdown_course(course)
            mimetype = 'text/markdown'
            
        elif format == 'html':
            filename = f"course_{timestamp}.html"
            data = generate_html_course(course)
            mimetype = 'text/html'
            
        elif format == 'pdf':
            from agent.content_generator import export_course_to_pdf
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                pdf_path = tmp_file.name
            
            export_course_to_pdf(course, pdf_path)
            filename = f"course_{timestamp}.pdf"
            
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported format: {format}'
            }), 400
        
        # Create response
        return app.response_class(
            response=data,
            status=200,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting course: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export-roadmap/<format>', methods=['GET'])
def export_roadmap(format):
    """Export roadmap in various formats"""
    try:
        roadmap_dict = course_storage.get('course_roadmap')
        if not roadmap_dict:
            return jsonify({
                'success': False,
                'error': 'No roadmap to export'
            }), 400
        
        api_key = os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        roadmap_agent = CourseRoadmapAgent(api_key=api_key, model=model)
        roadmap = CourseRoadmap(**roadmap_dict)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filename = f"roadmap_{timestamp}.json"
            data = json.dumps(roadmap_dict, indent=2, ensure_ascii=False)
            mimetype = 'application/json'
            
        elif format == 'markdown':
            filename = f"roadmap_{timestamp}.md"
            data = roadmap_agent.format_roadmap_markdown(roadmap)
            mimetype = 'text/markdown'
            
        elif format == 'pdf':
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                pdf_path = tmp_file.name
            
            roadmap_agent.export_to_pdf(roadmap, pdf_path)
            filename = f"roadmap_{timestamp}.pdf"
            
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported format: {format}'
            }), 400
        
        # Create response
        return app.response_class(
            response=data,
            status=200,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting roadmap: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear stored course data"""
    course_storage['course_content'] = None
    course_storage['course_roadmap'] = None
    
    return jsonify({
        'success': True,
        'message': 'Data cleared successfully'
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
