"""
Course Content Agent
Generates comprehensive course content based on user specifications
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import google.generativeai as genai
import json


class Lesson(BaseModel):
    """Individual lesson structure"""
    title: str
    duration_minutes: int
    learning_objectives: List[str]
    content: str
    key_points: List[str]
    activities: List[str]
    assessment_questions: List[Dict[str, str]]


class Module(BaseModel):
    """Course module structure"""
    title: str
    description: str
    duration_hours: float
    lessons: List[Lesson]


class CourseContent(BaseModel):
    """Complete course structure"""
    title: str
    description: str
    target_audience: str
    difficulty_level: str
    duration_weeks: int
    prerequisites: List[str]
    learning_outcomes: List[str]
    modules: List[Module]


class CourseContentAgent:
    """
    Agent that generates comprehensive course content using AI
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the course content agent
        
        Args:
            api_key: Google API key (defaults to environment variable)
            model: Model to use for generation
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        
        # Configure generation settings for better token management
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        self.client = genai.GenerativeModel(
            self.model,
            generation_config=generation_config
        )
    
    def generate_course_outline(self, topic: str, duration_weeks: int = 4, 
                               difficulty: str = "beginner", 
                               target_audience: str = "general learners") -> Dict:
        """
        Generate a high-level course outline
        
        Args:
            topic: Course topic
            duration_weeks: Course duration in weeks
            difficulty: Difficulty level (beginner, intermediate, advanced)
            target_audience: Target audience description
            
        Returns:
            Course outline dictionary
        """
        prompt = f"""You are a course design expert. Create a comprehensive course outline STRICTLY about "{topic}".

IMPORTANT: The course MUST be about "{topic}" - do NOT generate content about any other subject.

Course Specifications:
- Topic: {topic}
- Difficulty: {difficulty}
- Target Audience: {target_audience}
- Duration: {duration_weeks} weeks
- Number of Modules: {max(4, duration_weeks)}

Generate a JSON object with this exact structure:
{{
    "title": "[Course title must include '{topic}']",
    "description": "[1-2 sentence description specifically about {topic}]",
    "prerequisites": ["prerequisite 1 for {topic}", "prerequisite 2", "prerequisite 3"],
    "learning_outcomes": ["outcome 1 related to {topic}", "outcome 2", "outcome 3", "outcome 4", "outcome 5"],
    "modules": [
        {{"title": "Module 1 title about {topic}", "description": "Module description"}},
        {{"title": "Module 2 title about {topic}", "description": "Module description"}}
    ]
}}

Return ONLY valid JSON without markdown formatting. The entire course must focus on {topic}."""

        response = self.client.generate_content(prompt)
        content = response.text.strip()
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        if not content:
            raise ValueError("Generated content is empty. Please try again.")
        
        return json.loads(content)
    
    def _generate_lessons_batch(self, module_title: str, course_context: str, 
                                 num_lessons: int, batch_num: int = 1) -> List[Dict]:
        """Generate a batch of lessons (max 2 per call)"""
        prompt = f"""You are creating lesson content for a module titled "{module_title}".

{course_context}

IMPORTANT: All lessons MUST be relevant to the module "{module_title}" and the overall course context. Do NOT create content about unrelated topics.

Create {num_lessons} detailed lesson(s) as a JSON array. Each lesson must:
- Be directly related to "{module_title}"
- Have a clear title, 45-minute duration
- Include 3 specific learning objectives
- Provide 200-300 words of educational content
- List 4 key takeaway points
- Suggest 2 practical activities
- Include 1 assessment question with answer

Example structure:
[
  {{
    "title": "Specific lesson title related to {module_title}",
    "duration_minutes": 45,
    "learning_objectives": ["Learn objective 1 about {module_title}", "Learn objective 2", "Learn objective 3"],
    "content": "Detailed 200-300 word educational explanation about the topic...",
    "key_points": ["Key point 1", "Key point 2", "Key point 3", "Key point 4"],
    "activities": ["Practical activity 1", "Practical activity 2"],
    "assessment_questions": [{{"question": "Assessment question about the lesson", "answer": "Correct answer"}}]
  }}
]

Return ONLY valid JSON array without markdown formatting."""

        try:
            response = self.client.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
        except Exception as e:
            print(f"   Batch {batch_num} failed: {e}")
            return []
    
    def generate_module_content(self, module_title: str, module_description: str,
                               course_context: str, num_lessons: int = 4) -> List[Dict]:
        """
        Generate detailed content for a course module
        
        Args:
            module_title: Title of the module
            module_description: Description of the module
            course_context: Context about the overall course
            num_lessons: Number of lessons in the module
            
        Returns:
            List of lesson dictionaries
        """
        # Generate lessons in batches of 2 to avoid token limits
        all_lessons = []
        remaining = num_lessons
        batch_num = 1
        
        while remaining > 0:
            batch_size = min(2, remaining)
            lessons = self._generate_lessons_batch(module_title, course_context, batch_size, batch_num)
            
            if lessons:
                all_lessons.extend(lessons)
            else:
                # Fallback for failed batch
                for i in range(batch_size):
                    all_lessons.append({
                        "title": f"Lesson {len(all_lessons)+1}",
                        "duration_minutes": 45,
                        "learning_objectives": ["To be developed"],
                        "content": "Content to be developed.",
                        "key_points": ["To be developed"],
                        "activities": ["Activity to be developed"],
                        "assessment_questions": [{"question": "To be developed", "answer": "To be developed"}]
                    })
            
            remaining -= batch_size
            batch_num += 1
        
        return all_lessons
    
    def _call_api_and_parse(self, prompt: str) -> List[Dict]:
        """Helper to call API and parse JSON response"""
        response = self.client.generate_content(prompt)
        content = response.text.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        if not content:
            raise ValueError("Generated content is empty. Please try again.")
        
        return json.loads(content)
    
    def generate_complete_course(self, topic: str, duration_weeks: int = 4,
                                difficulty: str = "beginner",
                                target_audience: str = "general learners",
                                lessons_per_module: int = 4) -> CourseContent:
        """
        Generate a complete course with all modules and lessons
        
        Args:
            topic: Course topic
            duration_weeks: Course duration in weeks
            difficulty: Difficulty level
            target_audience: Target audience
            lessons_per_module: Number of lessons per module
            
        Returns:
            Complete CourseContent object
        """
        print(f"Generating course outline for: {topic}")
        outline = self.generate_course_outline(topic, duration_weeks, difficulty, target_audience)
        
        # Verify the generated outline is actually about the requested topic
        generated_title = outline.get("title", "").lower()
        topic_keywords = topic.lower().split()
        topic_match = any(keyword in generated_title for keyword in topic_keywords if len(keyword) > 3)
        
        if not topic_match:
            print(f"WARNING: Generated course title '{outline.get('title')}' may not match requested topic '{topic}'")
            print(f"Regenerating with stricter constraints...")
            # Retry with more explicit prompt
            prompt = f"""CRITICAL: Create a course outline ONLY about "{topic}". The title MUST include "{topic}".

Topic: {topic}
Difficulty: {difficulty}
Target Audience: {target_audience}
Duration: {duration_weeks} weeks

Generate JSON with title containing "{topic}", description, prerequisites, learning_outcomes, and {max(4, duration_weeks)} modules.
JSON only, no markdown."""
            response = self.client.generate_content(prompt)
            content = response.text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            outline = json.loads(content.strip())
        
        course_data = {
            "title": outline.get("title", topic),
            "description": outline.get("description", ""),
            "target_audience": target_audience,
            "difficulty_level": difficulty,
            "duration_weeks": duration_weeks,
            "prerequisites": outline.get("prerequisites", []),
            "learning_outcomes": outline.get("learning_outcomes", []),
            "modules": []
        }
        
        # Generate content for each module
        modules = outline.get("modules", [])
        if not modules:
            raise ValueError("No modules were generated in the course outline. Please try again.")
        
        print(f"\nGenerating {len(modules)} modules...")
        for idx, module_info in enumerate(modules):
            module_title = module_info.get("title", f"Module {idx + 1}")
            module_desc = module_info.get("description", "")
            print(f"  Module {idx + 1}/{len(modules)}: {module_title}")
            
            # Generate detailed lesson content
            course_context = f"Course: {course_data['title']}. Difficulty: {difficulty}. Audience: {target_audience}"
            lessons_data = self.generate_module_content(module_title, module_desc, course_context, lessons_per_module)
            
            # Convert lessons to Lesson objects
            lessons = []
            for lesson_data in lessons_data:
                lesson = Lesson(
                    title=lesson_data.get("title", "Untitled Lesson"),
                    duration_minutes=lesson_data.get("duration_minutes", 45),
                    learning_objectives=lesson_data.get("learning_objectives", []),
                    content=lesson_data.get("content", ""),
                    key_points=lesson_data.get("key_points", []),
                    activities=lesson_data.get("activities", []),
                    assessment_questions=lesson_data.get("assessment_questions", [])
                )
                lessons.append(lesson)
            
            # Calculate module duration
            total_minutes = sum(lesson.duration_minutes for lesson in lessons)
            duration_hours = total_minutes / 60
            
            module = Module(
                title=module_info.get("title", f"Module {idx + 1}"),
                description=module_info.get("description", ""),
                duration_hours=round(duration_hours, 1),
                lessons=lessons
            )
            
            course_data["modules"].append(module)
        
        return CourseContent(**course_data)
    
    def export_to_dict(self, course: CourseContent) -> Dict:
        """Export course content to dictionary format"""
        return course.model_dump()
    
    def export_to_json(self, course: CourseContent, filepath: str):
        """Export course content to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(course.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"Course content exported to {filepath}")
