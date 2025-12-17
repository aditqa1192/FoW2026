"""
Flask API Backend for OKIR Course Content Agent
Provides REST API endpoints for course generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import io

from agent import CourseContentAgent, generate_markdown_course, generate_html_course

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/generate-course', methods=['POST'])
def generate_course():
    """Generate complete course content"""
    try:
        data = request.json
        
        # Extract parameters
        api_key = data.get('apiKey') or os.getenv('GOOGLE_API_KEY')
        model = data.get('model', 'gemini-2.0-flash-exp')
        course_topic = data.get('courseTopic')
        duration_weeks = data.get('durationWeeks', 4)
        difficulty = data.get('difficulty', 'beginner')
        target_audience = data.get('targetAudience', 'general learners')
        lessons_per_module = data.get('lessonsPerModule', 4)
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        if not course_topic:
            return jsonify({'error': 'Course topic is required'}), 400
        
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
        
        # Export to dict
        course_dict = agent.export_to_dict(course)
        
        return jsonify(course_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/json', methods=['POST'])
def export_json():
    """Export course content as JSON"""
    try:
        course = request.json
        
        json_data = json.dumps(course, indent=2, ensure_ascii=False)
        
        buffer = io.BytesIO()
        buffer.write(json_data.encode('utf-8'))
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'course_{timestamp}.json'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/md', methods=['POST'])
def export_markdown():
    """Export course content as Markdown"""
    try:
        course = request.json
        
        markdown_data = generate_markdown_course(course)
        
        buffer = io.BytesIO()
        buffer.write(markdown_data.encode('utf-8'))
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return send_file(
            buffer,
            mimetype='text/markdown',
            as_attachment=True,
            download_name=f'course_{timestamp}.md'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/html', methods=['POST'])
def export_html():
    """Export course content as HTML"""
    try:
        course = request.json
        
        html_data = generate_html_course(course)
        
        buffer = io.BytesIO()
        buffer.write(html_data.encode('utf-8'))
        buffer.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return send_file(
            buffer,
            mimetype='text/html',
            as_attachment=True,
            download_name=f'course_{timestamp}.html'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
