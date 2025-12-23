"""
Course Content Agent with LangChain
Generates comprehensive course content using LangChain framework
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough


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


class CourseOutline(BaseModel):
    """Course outline structure for parsing"""
    title: str
    description: str
    prerequisites: List[str]
    learning_outcomes: List[str]
    modules: List[Dict[str, str]]


class CourseContentAgentLangChain:
    """
    Agent that generates comprehensive course content using LangChain
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the course content agent with LangChain
        
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
        
        # Initialize output parsers
        self.json_parser = JsonOutputParser()
        
    def generate_course_outline(self, topic: str, duration_weeks: int = 4, 
                               difficulty: str = "beginner", 
                               target_audience: str = "general learners") -> Dict:
        """
        Generate a high-level course outline using LangChain
        
        Args:
            topic: Course topic
            duration_weeks: Course duration in weeks
            difficulty: Difficulty level (beginner, intermediate, advanced)
            target_audience: Target audience description
            
        Returns:
            Course outline dictionary
        """
        # Create prompt template
        outline_prompt = PromptTemplate(
            template="""Create a comprehensive course outline for the following specifications:

Topic: {topic}
Difficulty Level: {difficulty}
Target Audience: {target_audience}
Duration: {duration_weeks} weeks
Number of Modules: {num_modules}

Generate a JSON object with the following structure:
{{
    "title": "Course title",
    "description": "1-2 sentence course description",
    "prerequisites": ["prerequisite 1", "prerequisite 2", "prerequisite 3"],
    "learning_outcomes": ["outcome 1", "outcome 2", "outcome 3", "outcome 4", "outcome 5"],
    "modules": [
        {{"title": "Module title", "description": "Module description"}}
    ]
}}

Return ONLY valid JSON without any markdown formatting or code blocks.""",
            input_variables=["topic", "difficulty", "target_audience", "duration_weeks", "num_modules"]
        )
        
        # Create chain
        chain = outline_prompt | self.llm | self.json_parser
        
        # Execute chain
        try:
            result = chain.invoke({
                "topic": topic,
                "difficulty": difficulty,
                "target_audience": target_audience,
                "duration_weeks": duration_weeks,
                "num_modules": max(4, duration_weeks)
            })
            return result
        except Exception as e:
            print(f"Error parsing course outline: {e}")
            # Fallback to text parsing
            response = (outline_prompt | self.llm).invoke({
                "topic": topic,
                "difficulty": difficulty,
                "target_audience": target_audience,
                "duration_weeks": duration_weeks,
                "num_modules": max(4, duration_weeks)
            })
            content = response.content.strip()
            # Clean up markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
    
    def _generate_lessons_batch(self, module_title: str, course_context: str, 
                                 num_lessons: int, batch_num: int = 1) -> List[Dict]:
        """Generate a batch of lessons using LangChain"""
        
        lesson_prompt = PromptTemplate(
            template="""Create {num_lessons} detailed lesson(s) for the following module:

Module: {module_title}
Course Context: {course_context}

Generate a JSON array with {num_lessons} lesson objects. Each lesson must have:
- title: Lesson title
- duration_minutes: 45
- learning_objectives: Array of 3 learning objectives
- content: Detailed 200-300 word explanation
- key_points: Array of 4 key takeaways
- activities: Array of 2 practical activities
- assessment_questions: Array with 1 question-answer pair

Example structure:
[
  {{
    "title": "Lesson title here",
    "duration_minutes": 45,
    "learning_objectives": ["objective 1", "objective 2", "objective 3"],
    "content": "Detailed explanation of the lesson content...",
    "key_points": ["point 1", "point 2", "point 3", "point 4"],
    "activities": ["activity 1", "activity 2"],
    "assessment_questions": [{{"question": "question text", "answer": "answer text"}}]
  }}
]

Return ONLY valid JSON array without any markdown formatting or code blocks.""",
            input_variables=["module_title", "course_context", "num_lessons"]
        )
        
        # Create chain
        chain = lesson_prompt | self.llm | self.json_parser
        
        try:
            result = chain.invoke({
                "module_title": module_title,
                "course_context": course_context,
                "num_lessons": num_lessons
            })
            return result if isinstance(result, list) else [result]
        except Exception as e:
            print(f"   Batch {batch_num} failed: {e}")
            return []
    
    def generate_module_content(self, module_title: str, module_description: str,
                               course_context: str, num_lessons: int = 4) -> List[Dict]:
        """
        Generate detailed content for a course module using LangChain
        
        Args:
            module_title: Title of the module
            module_description: Description of the module
            course_context: Context about the overall course
            num_lessons: Number of lessons in the module
            
        Returns:
            List of lesson dictionaries
        """
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
    
    def generate_complete_course(self, topic: str, duration_weeks: int = 4,
                                difficulty: str = "beginner",
                                target_audience: str = "general learners",
                                lessons_per_module: int = 4) -> CourseContent:
        """
        Generate a complete course with all modules and lessons using LangChain
        
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
        
        modules = outline.get("modules", [])
        if not modules:
            raise ValueError("No modules were generated in the course outline. Please try again.")
        
        print(f"\nGenerating {len(modules)} modules...")
        for idx, module_info in enumerate(modules):
            module_title = module_info.get("title", f"Module {idx + 1}")
            module_desc = module_info.get("description", "")
            print(f"  Module {idx + 1}/{len(modules)}: {module_title}")
            
            course_context = f"Course: {course_data['title']}. Difficulty: {difficulty}. Audience: {target_audience}"
            lessons_data = self.generate_module_content(module_title, module_desc, course_context, lessons_per_module)
            
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
