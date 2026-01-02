"""
Course Roadmap Agent
Generates structured learning roadmaps and timelines for courses
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class WeeklySchedule(BaseModel):
    """Weekly schedule structure"""
    week_number: int
    week_title: str
    topics: List[str]
    modules_covered: List[str]
    estimated_hours: float
    milestones: List[str]
    deliverables: List[str]


class Milestone(BaseModel):
    """Course milestone structure"""
    week: int
    title: str
    description: str
    type: str  # quiz, project, assignment, checkpoint


class CourseRoadmap(BaseModel):
    """Complete course roadmap structure"""
    course_title: str
    total_duration_weeks: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_modules: int
    total_estimated_hours: float
    weekly_schedule: List[WeeklySchedule]
    milestones: List[Milestone]
    study_tips: List[str]
    pacing_recommendations: str


class CourseRoadmapAgent:
    """
    Agent that generates course roadmaps and learning timelines
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the roadmap agent
        
        Args:
            api_key: Google API key (defaults to environment variable)
            model: Model to use for generation
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )
        
        self.json_parser = JsonOutputParser()
    
    def generate_roadmap_from_modules(self, course_title: str, modules: List[Dict],
                                     duration_weeks: int, difficulty: str = "beginner",
                                     hours_per_week: float = 5.0,
                                     start_date: Optional[str] = None) -> CourseRoadmap:
        """
        Generate a course roadmap from module information
        
        Args:
            course_title: Title of the course
            modules: List of module dictionaries with title, description, and lessons
            duration_weeks: Course duration in weeks
            difficulty: Course difficulty level
            hours_per_week: Expected study hours per week
            start_date: Optional start date (YYYY-MM-DD format)
            
        Returns:
            CourseRoadmap object with complete timeline
        """
        # Prepare module summary
        module_summary = []
        total_lessons = 0
        for idx, module in enumerate(modules):
            lessons = module.get('lessons', [])
            total_lessons += len(lessons)
            module_summary.append({
                'number': idx + 1,
                'title': module.get('title', f'Module {idx + 1}'),
                'description': module.get('description', ''),
                'num_lessons': len(lessons),
                'estimated_hours': module.get('duration_hours', len(lessons) * 0.75)
            })
        
        # Calculate dates if start_date provided
        dates_info = ""
        calculated_end_date = None
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = start + timedelta(weeks=duration_weeks)
                calculated_end_date = end.strftime("%Y-%m-%d")
                dates_info = f"\nStart Date: {start_date}\nEnd Date: {calculated_end_date}"
            except:
                pass
        
        roadmap_prompt = PromptTemplate(
            template="""You are an expert learning designer. Create a comprehensive course roadmap and study timeline.

Course Information:
- Title: {course_title}
- Duration: {duration_weeks} weeks
- Difficulty: {difficulty}
- Expected Study Time: {hours_per_week} hours per week
- Total Modules: {total_modules}
- Total Lessons: {total_lessons}{dates_info}

Module Breakdown:
{module_summary}

Create a detailed week-by-week roadmap that:
1. Distributes modules and lessons evenly across {duration_weeks} weeks
2. Balances workload to approximately {hours_per_week} hours per week
3. Includes strategic milestones (quizzes, projects, checkpoints)
4. Provides realistic pacing for {difficulty} level learners
5. Builds knowledge progressively

Generate a JSON object with this structure:
{{
    "weekly_schedule": [
        {{
            "week_number": 1,
            "week_title": "Week 1: [Descriptive title]",
            "topics": ["Topic 1 from modules", "Topic 2", "Topic 3"],
            "modules_covered": ["Module title(s) covered this week"],
            "estimated_hours": {hours_per_week},
            "milestones": ["Milestone 1", "Milestone 2"],
            "deliverables": ["Assignment/Quiz/Project due this week"]
        }}
    ],
    "milestones": [
        {{
            "week": 2,
            "title": "Quiz 1: [Topic]",
            "description": "Brief description of milestone",
            "type": "quiz"
        }},
        {{
            "week": 4,
            "title": "Project 1: [Title]",
            "description": "Brief description of project",
            "type": "project"
        }}
    ],
    "study_tips": [
        "Study tip 1 for effective learning",
        "Study tip 2 for time management",
        "Study tip 3 for retention",
        "Study tip 4 for practice",
        "Study tip 5 for review"
    ],
    "pacing_recommendations": "2-3 sentences on how to pace learning through this course for best results"
}}

IMPORTANT: 
- Create exactly {duration_weeks} weekly schedule entries
- Distribute all modules across the weeks
- Include at least one milestone every 2 weeks
- Make milestones realistic (quizzes, assignments, projects, checkpoints)
- Ensure total estimated hours align with course expectations

Return ONLY valid JSON without markdown formatting.""",
            input_variables=["course_title", "duration_weeks", "difficulty", "hours_per_week",
                           "total_modules", "total_lessons", "dates_info", "module_summary"]
        )
        
        # Format module summary for prompt
        module_text = "\n".join([
            f"Module {m['number']}: {m['title']} ({m['num_lessons']} lessons, ~{m['estimated_hours']:.1f} hours)"
            for m in module_summary
        ])
        
        # Create chain
        chain = roadmap_prompt | self.llm | self.json_parser
        
        try:
            result = chain.invoke({
                "course_title": course_title,
                "duration_weeks": duration_weeks,
                "difficulty": difficulty,
                "hours_per_week": hours_per_week,
                "total_modules": len(modules),
                "total_lessons": total_lessons,
                "dates_info": dates_info,
                "module_summary": module_text
            })
        except Exception as e:
            print(f"Error parsing roadmap: {e}")
            # Fallback to text parsing
            response = (roadmap_prompt | self.llm).invoke({
                "course_title": course_title,
                "duration_weeks": duration_weeks,
                "difficulty": difficulty,
                "hours_per_week": hours_per_week,
                "total_modules": len(modules),
                "total_lessons": total_lessons,
                "dates_info": dates_info,
                "module_summary": module_text
            })
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            result = json.loads(content.strip())
        
        # Calculate total estimated hours
        total_hours = sum(week.get('estimated_hours', 0) for week in result.get('weekly_schedule', []))
        
        # Build the roadmap
        roadmap_data = {
            "course_title": course_title,
            "total_duration_weeks": duration_weeks,
            "start_date": start_date,
            "end_date": calculated_end_date,
            "total_modules": len(modules),
            "total_estimated_hours": round(total_hours, 1),
            "weekly_schedule": [
                WeeklySchedule(**week) for week in result.get('weekly_schedule', [])
            ],
            "milestones": [
                Milestone(**milestone) for milestone in result.get('milestones', [])
            ],
            "study_tips": result.get('study_tips', []),
            "pacing_recommendations": result.get('pacing_recommendations', '')
        }
        
        return CourseRoadmap(**roadmap_data)
    
    def generate_roadmap_from_outline(self, course_title: str, module_titles: List[str],
                                     duration_weeks: int, difficulty: str = "beginner",
                                     hours_per_week: float = 5.0,
                                     start_date: Optional[str] = None) -> CourseRoadmap:
        """
        Generate a course roadmap from just module titles (lightweight version)
        
        Args:
            course_title: Title of the course
            module_titles: List of module title strings
            duration_weeks: Course duration in weeks
            difficulty: Course difficulty level
            hours_per_week: Expected study hours per week
            start_date: Optional start date (YYYY-MM-DD format)
            
        Returns:
            CourseRoadmap object with complete timeline
        """
        # Convert module titles to basic module structure
        modules = [
            {
                'title': title,
                'description': '',
                'lessons': [{'title': f'Lesson {i+1}'} for i in range(4)],  # Assume 4 lessons per module
                'duration_hours': 3.0
            }
            for title in module_titles
        ]
        
        return self.generate_roadmap_from_modules(
            course_title, modules, duration_weeks, difficulty, hours_per_week, start_date
        )
    
    def export_to_dict(self, roadmap: CourseRoadmap) -> Dict:
        """Export roadmap to dictionary format"""
        return roadmap.model_dump()
    
    def export_to_json(self, roadmap: CourseRoadmap, filepath: str):
        """Export roadmap to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(roadmap.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"Roadmap exported to {filepath}")
    
    def format_roadmap_markdown(self, roadmap: CourseRoadmap) -> str:
        """
        Format roadmap as markdown for display
        
        Args:
            roadmap: CourseRoadmap object
            
        Returns:
            Formatted markdown string
        """
        md = [f"# {roadmap.course_title} - Learning Roadmap\n"]
        
        # Overview
        md.append("## Course Overview\n")
        md.append(f"- **Duration:** {roadmap.total_duration_weeks} weeks")
        if roadmap.start_date:
            md.append(f"- **Start Date:** {roadmap.start_date}")
        if roadmap.end_date:
            md.append(f"- **End Date:** {roadmap.end_date}")
        md.append(f"- **Total Modules:** {roadmap.total_modules}")
        md.append(f"- **Estimated Hours:** {roadmap.total_estimated_hours} hours")
        md.append(f"- **Weekly Commitment:** ~{roadmap.total_estimated_hours / roadmap.total_duration_weeks:.1f} hours/week\n")
        
        # Pacing recommendations
        if roadmap.pacing_recommendations:
            md.append("## Pacing Recommendations\n")
            md.append(f"{roadmap.pacing_recommendations}\n")
        
        # Weekly schedule
        md.append("## Weekly Schedule\n")
        for week in roadmap.weekly_schedule:
            md.append(f"### {week.week_title}\n")
            md.append(f"**Estimated Time:** {week.estimated_hours} hours\n")
            
            if week.modules_covered:
                md.append("**Modules:**")
                for module in week.modules_covered:
                    md.append(f"- {module}")
                md.append("")
            
            if week.topics:
                md.append("**Topics:**")
                for topic in week.topics:
                    md.append(f"- {topic}")
                md.append("")
            
            if week.deliverables:
                md.append("**Deliverables:**")
                for deliverable in week.deliverables:
                    md.append(f"- {deliverable}")
                md.append("")
            
            if week.milestones:
                md.append("**Milestones:**")
                for milestone in week.milestones:
                    md.append(f"- {milestone}")
                md.append("")
        
        # Milestones overview
        if roadmap.milestones:
            md.append("## Key Milestones\n")
            md.append("| Week | Type | Title | Description |")
            md.append("|------|------|-------|-------------|")
            for milestone in roadmap.milestones:
                md.append(f"| {milestone.week} | {milestone.type.capitalize()} | {milestone.title} | {milestone.description} |")
            md.append("")
        
        # Study tips
        if roadmap.study_tips:
            md.append("## Study Tips for Success\n")
            for idx, tip in enumerate(roadmap.study_tips, 1):
                md.append(f"{idx}. {tip}")
            md.append("")
        
        return "\n".join(md)
    
    def generate_summary_table(self, roadmap: CourseRoadmap) -> str:
        """
        Generate a summary table of weekly schedule
        
        Args:
            roadmap: CourseRoadmap object
            
        Returns:
            Markdown table string
        """
        table = []
        table.append("| Week | Week Title | Modules Covered | Estimated Hours |")
        table.append("|------|------------|-----------------|-----------------|")
        
        for week in roadmap.weekly_schedule:
            modules_str = ", ".join(week.modules_covered) if week.modules_covered else "N/A"
            # Truncate long module names
            if len(modules_str) > 60:
                modules_str = modules_str[:57] + "..."
            
            table.append(f"| {week.week_number} | {week.week_title} | {modules_str} | {week.estimated_hours} hrs |")
        
        # Add totals row
        table.append(f"| **Total** | **{roadmap.total_duration_weeks} weeks** | **{roadmap.total_modules} modules** | **{roadmap.total_estimated_hours} hrs** |")
        
        return "\n".join(table)
    
    def export_to_pdf(self, roadmap: CourseRoadmap, filepath: str):
        """
        Export roadmap to PDF file using xhtml2pdf (Windows-friendly)
        
        Args:
            roadmap: CourseRoadmap object
            filepath: Output PDF file path
        """
        try:
            from markdown2 import markdown
            from xhtml2pdf import pisa
            from io import BytesIO
            
            # Generate markdown content with summary table at the top
            summary_table = self.generate_summary_table(roadmap)
            md_content = self.format_roadmap_markdown(roadmap)
            
            # Insert summary table after the overview section
            md_parts = md_content.split('## Pacing Recommendations', 1)
            if len(md_parts) == 2:
                md_content = md_parts[0] + '\n## Weekly Schedule Summary\n\n' + summary_table + '\n\n## Pacing Recommendations' + md_parts[1]
            
            # Convert markdown to HTML
            html_content = markdown(md_content, extras=['tables', 'fenced-code-blocks'])
            
            # Add CSS styling
            css_style = """
            <style>
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: Arial, Helvetica, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    font-size: 11pt;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-top: 20px;
                    font-size: 24pt;
                }
                h2 {
                    color: #34495e;
                    border-bottom: 2px solid #95a5a6;
                    padding-bottom: 8px;
                    margin-top: 25px;
                    font-size: 18pt;
                }
                h3 {
                    color: #2c3e50;
                    margin-top: 20px;
                    font-size: 14pt;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                    font-size: 10pt;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: left;
                }
                th {
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                ul, ol {
                    margin: 10px 0;
                    padding-left: 30px;
                }
                li {
                    margin: 5px 0;
                }
                strong {
                    color: #2c3e50;
                }
                p {
                    margin: 8px 0;
                }
            </style>
            """
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                {css_style}
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Generate PDF
            with open(filepath, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(
                    full_html,
                    dest=pdf_file
                )
            
            if pisa_status.err:
                raise Exception(f"PDF generation failed with error code: {pisa_status.err}")
            
            print(f"PDF roadmap exported to {filepath}")
            
        except ImportError as e:
            print(f"Error: Required libraries not installed. Run: pip install markdown2 xhtml2pdf")
            print(f"Details: {e}")
            raise
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise


def format_roadmap_summary(roadmap: CourseRoadmap) -> str:
    """
    Format a brief summary of the roadmap
    
    Args:
        roadmap: CourseRoadmap object
        
    Returns:
        Formatted summary string
    """
    summary = [
        f"Course Roadmap: {roadmap.course_title}",
        f"Duration: {roadmap.total_duration_weeks} weeks",
        f"Total Hours: {roadmap.total_estimated_hours}",
        f"Modules: {roadmap.total_modules}",
        f"Milestones: {len(roadmap.milestones)}"
    ]
    
    if roadmap.start_date and roadmap.end_date:
        summary.append(f"Timeline: {roadmap.start_date} to {roadmap.end_date}")
    
    return " | ".join(summary)
