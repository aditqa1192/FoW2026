"""
Content generation utilities
"""

from typing import List, Dict


def generate_markdown_course(course_dict: Dict) -> str:
    """
    Generate a markdown formatted version of the course
    
    Args:
        course_dict: Course content dictionary
        
    Returns:
        Markdown formatted string
    """
    md = f"""# {course_dict['title']}

## Course Overview

**Description:** {course_dict['description']}

**Target Audience:** {course_dict['target_audience']}

**Difficulty Level:** {course_dict['difficulty_level']}

**Duration:** {course_dict['duration_weeks']} weeks

### Prerequisites
{chr(10).join(f"- {prereq}" for prereq in course_dict['prerequisites'])}

### Learning Outcomes
{chr(10).join(f"- {outcome}" for outcome in course_dict['learning_outcomes'])}

---

## Course Content

"""
    
    for module_idx, module in enumerate(course_dict['modules'], 1):
        md += f"""### Module {module_idx}: {module['title']}

**Description:** {module['description']}

**Duration:** {module['duration_hours']} hours

"""
        
        for lesson_idx, lesson in enumerate(module['lessons'], 1):
            md += f"""#### Lesson {module_idx}.{lesson_idx}: {lesson['title']}

**Duration:** {lesson['duration_minutes']} minutes

##### Learning Objectives
{chr(10).join(f"- {obj}" for obj in lesson['learning_objectives'])}

##### Content
{lesson['content']}

##### Key Points
{chr(10).join(f"- {point}" for point in lesson['key_points'])}

##### Activities
{chr(10).join(f"{i}. {activity}" for i, activity in enumerate(lesson['activities'], 1))}

##### Assessment
{chr(10).join(f"{i}. **Q:** {q.get('question', 'N/A')}{chr(10)}   **A:** {q.get('answer', 'N/A')}" for i, q in enumerate(lesson['assessment_questions'], 1))}

---

"""
    
    return md


def generate_html_course(course_dict: Dict) -> str:
    """
    Generate an HTML formatted version of the course
    
    Args:
        course_dict: Course content dictionary
        
    Returns:
        HTML formatted string
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course_dict['title']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #3498db;
            margin-top: 25px;
        }}
        h4 {{
            color: #555;
            margin-top: 20px;
        }}
        .meta {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .meta-item {{
            margin: 5px 0;
        }}
        .content-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
        }}
        ul, ol {{
            margin: 10px 0;
        }}
        li {{
            margin: 5px 0;
        }}
        .assessment {{
            background-color: #fff8dc;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{course_dict['title']}</h1>
        
        <div class="meta">
            <div class="meta-item"><strong>Description:</strong> {course_dict['description']}</div>
            <div class="meta-item"><strong>Target Audience:</strong> {course_dict['target_audience']}</div>
            <div class="meta-item"><strong>Difficulty:</strong> {course_dict['difficulty_level'].title()}</div>
            <div class="meta-item"><strong>Duration:</strong> {course_dict['duration_weeks']} weeks</div>
        </div>
        
        <h2>Prerequisites</h2>
        <ul>
            {''.join(f"<li>{prereq}</li>" for prereq in course_dict['prerequisites'])}
        </ul>
        
        <h2>Learning Outcomes</h2>
        <ul>
            {''.join(f"<li>{outcome}</li>" for outcome in course_dict['learning_outcomes'])}
        </ul>
        
        <h2>Course Content</h2>
"""
    
    for module_idx, module in enumerate(course_dict['modules'], 1):
        html += f"""
        <div class="content-section">
            <h3>Module {module_idx}: {module['title']}</h3>
            <p><strong>Description:</strong> {module['description']}</p>
            <p><strong>Duration:</strong> {module['duration_hours']} hours</p>
"""
        
        for lesson_idx, lesson in enumerate(module['lessons'], 1):
            html += f"""
            <h4>Lesson {module_idx}.{lesson_idx}: {lesson['title']}</h4>
            <p><strong>Duration:</strong> {lesson['duration_minutes']} minutes</p>
            
            <p><strong>Learning Objectives:</strong></p>
            <ul>
                {''.join(f"<li>{obj}</li>" for obj in lesson['learning_objectives'])}
            </ul>
            
            <p><strong>Content:</strong></p>
            <p>{lesson['content']}</p>
            
            <p><strong>Key Points:</strong></p>
            <ul>
                {''.join(f"<li>{point}</li>" for point in lesson['key_points'])}
            </ul>
            
            <p><strong>Activities:</strong></p>
            <ol>
                {''.join(f"<li>{activity}</li>" for activity in lesson['activities'])}
            </ol>
            
            <p><strong>Assessment:</strong></p>
            <div class="assessment">
                {''.join(f"<p><strong>Q{i}:</strong> {q.get('question', 'N/A')}<br><strong>A:</strong> {q.get('answer', 'N/A')}</p>" for i, q in enumerate(lesson['assessment_questions'], 1))}
            </div>
"""
        
        html += "</div>"
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


def format_course_summary(course_dict: Dict) -> str:
    """
    Generate a summary of the course
    
    Args:
        course_dict: Course content dictionary
        
    Returns:
        Formatted summary string
    """
    total_lessons = sum(len(module['lessons']) for module in course_dict['modules'])
    total_hours = sum(module['duration_hours'] for module in course_dict['modules'])
    
    summary = f"""
📚 Course: {course_dict['title']}

📊 Statistics:
- Modules: {len(course_dict['modules'])}
- Lessons: {total_lessons}
- Total Duration: {total_hours:.1f} hours ({course_dict['duration_weeks']} weeks)
- Difficulty: {course_dict['difficulty_level'].title()}
- Target Audience: {course_dict['target_audience']}

🎯 Learning Outcomes: {len(course_dict['learning_outcomes'])}
📋 Prerequisites: {len(course_dict['prerequisites'])}
"""
    
    return summary
