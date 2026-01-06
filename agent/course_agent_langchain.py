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
            template="""You are an expert course designer. Create a comprehensive course outline STRICTLY about the specified topic.

CRITICAL INSTRUCTION: The entire course MUST be about "{topic}" - do NOT generate content about any other subject. Every module, lesson, and outcome must directly relate to "{topic}".

Course Specifications:
- Topic: {topic}
- Difficulty Level: {difficulty}
- Target Audience: {target_audience}
- Duration: {duration_weeks} weeks
- Number of Modules: {num_modules}

Generate a JSON object with the following structure:
{{
    "title": "[Course title MUST include and be about '{topic}']",
    "description": "[1-2 sentences describing this course on {topic}]",
    "prerequisites": ["prerequisite 1 for learning {topic}", "prerequisite 2 for {topic}", "prerequisite 3"],
    "learning_outcomes": ["learners will be able to [skill 1 in {topic}]", "learners will understand [concept 2 in {topic}]", "learners will apply [technique 3 in {topic}]", "outcome 4 for {topic}", "outcome 5 for {topic}"],
    "modules": [
        {{"title": "Module 1: [Specific aspect of {topic}]", "description": "This module covers [specific content about {topic}]"}},
        {{"title": "Module 2: [Another aspect of {topic}]", "description": "This module covers [more content about {topic}]"}}
    ]
}}

VERIFY: Every field must relate to "{topic}". Return ONLY valid JSON without any markdown formatting or code blocks.""",
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
    
    def generate_course_outline_with_details(self, topic: str, duration_weeks: int = 4, 
                               difficulty: str = "beginner", 
                               target_audience: str = "general learners",
                               custom_learning_outcomes: Optional[List[str]] = None,
                               detailed_topics: Optional[str] = None) -> Dict:
        """
        Generate a high-level course outline using LangChain with optional custom parameters
        
        Args:
            topic: Course topic
            duration_weeks: Course duration in weeks
            difficulty: Difficulty level (beginner, intermediate, advanced)
            target_audience: Target audience description
            custom_learning_outcomes: Optional list of specific learning outcomes to achieve
            detailed_topics: Optional detailed description of topics to cover
            
        Returns:
            Course outline dictionary
        """
        # Build detailed topic specification
        topic_details = topic
        if detailed_topics:
            topic_details = f"{topic}. Specifically cover: {detailed_topics}"
        
        # Build learning outcomes specification
        outcomes_spec = ""
        if custom_learning_outcomes:
            outcomes_spec = f"\n\nREQUIRED LEARNING OUTCOMES (must include these):\n" + "\n".join([f"- {outcome}" for outcome in custom_learning_outcomes])
        
        # Create prompt template
        outline_prompt = PromptTemplate(
            template="""You are an expert course designer. Create a comprehensive course outline STRICTLY about the specified topic.

CRITICAL INSTRUCTION: The entire course MUST be about "{topic_details}" - do NOT generate content about any other subject. Every module, lesson, and outcome must directly relate to "{topic}".

Course Specifications:
- Topic: {topic_details}
- Difficulty Level: {difficulty}
- Target Audience: {target_audience}
- Duration: {duration_weeks} weeks
- Number of Modules: {num_modules}{outcomes_spec}

Generate a JSON object with the following structure:
{{
    "title": "[Course title MUST include and be about '{topic}']",
    "description": "[1-2 sentences describing this course on {topic}]",
    "prerequisites": ["prerequisite 1 for learning {topic}", "prerequisite 2 for {topic}", "prerequisite 3"],
    "learning_outcomes": ["learners will be able to [skill 1 in {topic}]", "learners will understand [concept 2 in {topic}]", "learners will apply [technique 3 in {topic}]", "outcome 4 for {topic}", "outcome 5 for {topic}"],
    "modules": [
        {{"title": "Module 1: [Specific aspect of {topic}]", "description": "This module covers [specific content about {topic}]"}},
        {{"title": "Module 2: [Another aspect of {topic}]", "description": "This module covers [more content about {topic}]"}}
    ]
}}

VERIFY: Every field must relate to "{topic}". Return ONLY valid JSON without any markdown formatting or code blocks.""",
            input_variables=["topic", "topic_details", "difficulty", "target_audience", "duration_weeks", "num_modules", "outcomes_spec"]
        )
        
        # Create chain
        chain = outline_prompt | self.llm | self.json_parser
        
        # Execute chain
        try:
            result = chain.invoke({
                "topic": topic,
                "topic_details": topic_details,
                "difficulty": difficulty,
                "target_audience": target_audience,
                "duration_weeks": duration_weeks,
                "num_modules": max(4, duration_weeks),
                "outcomes_spec": outcomes_spec
            })
            return result
        except Exception as e:
            print(f"Error parsing course outline: {e}")
            # Fallback to text parsing
            response = (outline_prompt | self.llm).invoke({
                "topic": topic,
                "topic_details": topic_details,
                "difficulty": difficulty,
                "target_audience": target_audience,
                "duration_weeks": duration_weeks,
                "num_modules": max(4, duration_weeks),
                "outcomes_spec": outcomes_spec
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
            template="""You are creating educational lesson content for a specific module.

Module: {module_title}
Course Context: {course_context}

CRITICAL INSTRUCTION: All {num_lessons} lesson(s) MUST be directly relevant to "{module_title}" and the course context provided. Do NOT create content about unrelated topics.

Generate a JSON array with {num_lessons} lesson object(s). Each lesson must have:
- title: Specific lesson title related to "{module_title}"
- duration_minutes: 45
- learning_objectives: Array of 3 concrete learning objectives for this lesson on {module_title}
- content: Detailed 200-300 word educational explanation about the lesson topic
- key_points: Array of 4 key takeaways from this lesson
- activities: Array of 2 practical activities related to the lesson
- assessment_questions: Array with 1 question-answer pair testing lesson understanding

Example structure:
[
  {{
    "title": "[Specific lesson title directly related to {module_title}]",
    "duration_minutes": 45,
    "learning_objectives": ["Learn [specific skill from {module_title}]", "Understand [concept from {module_title}]", "Apply [technique from {module_title}]"],
    "content": "Detailed 200-300 word explanation providing educational content about this specific lesson topic. Ensure the content is informative, accurate, and directly relevant to {module_title}...",
    "key_points": ["Key takeaway 1 from lesson", "Key takeaway 2", "Key takeaway 3", "Key takeaway 4"],
    "activities": ["Hands-on activity 1 related to the lesson", "Practical exercise 2 related to the lesson"],
    "assessment_questions": [{{"question": "Question testing understanding of this lesson", "answer": "Correct answer with explanation"}}]
  }}
]

VERIFY: All content must relate to "{module_title}". Return ONLY valid JSON array without any markdown formatting or code blocks.""",
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
                                lessons_per_module: int = 4,
                                custom_learning_outcomes: Optional[List[str]] = None,
                                detailed_topics: Optional[str] = None) -> CourseContent:
        """
        Generate a complete course with all modules and lessons using LangChain
        
        Args:
            topic: Course topic
            duration_weeks: Course duration in weeks
            difficulty: Difficulty level
            target_audience: Target audience
            lessons_per_module: Number of lessons per module
            custom_learning_outcomes: Optional list of custom learning outcomes
            detailed_topics: Optional detailed description of specific topics to cover
            
        Returns:
            Complete CourseContent object
        """
        print(f"Generating course outline for: {topic}")
        if custom_learning_outcomes:
            print(f"Using {len(custom_learning_outcomes)} custom learning outcomes")
        if detailed_topics:
            print(f"Using detailed topics specification")
            
        outline = self.generate_course_outline_with_details(
            topic, duration_weeks, difficulty, target_audience, 
            custom_learning_outcomes, detailed_topics
        )
        
        # Verify the generated outline is actually about the requested topic
        generated_title = outline.get("title", "").lower()
        topic_keywords = topic.lower().split()
        topic_match = any(keyword in generated_title for keyword in topic_keywords if len(keyword) > 3)
        
        if not topic_match:
            print(f"WARNING: Generated course title '{outline.get('title')}' may not match requested topic '{topic}'")
            print(f"Forcing title to match topic...")
            # Force the title to include the topic if it doesn't
            outline["title"] = f"{topic} - {difficulty.capitalize()} Course"
            print(f"Updated title to: {outline['title']}")
        
        course_data = {
            "title": outline.get("title", topic),
            "description": outline.get("description", ""),
            "target_audience": target_audience,
            "difficulty_level": difficulty,
            "duration_weeks": duration_weeks,
            "prerequisites": outline.get("prerequisites", []),
            "learning_outcomes": custom_learning_outcomes if custom_learning_outcomes else outline.get("learning_outcomes", []),
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
            if custom_learning_outcomes:
                course_context += f". Learning outcomes: {', '.join(custom_learning_outcomes[:3])}"
            if detailed_topics:
                course_context += f". Cover topics: {detailed_topics[:200]}"
                
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
