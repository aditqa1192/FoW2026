"""
Course templates and structures
"""

from typing import Dict, List


class CourseTemplates:
    """Predefined course templates for different subjects and formats"""
    
    @staticmethod
    def get_programming_template() -> Dict:
        """Template for programming courses"""
        return {
            "structure": {
                "modules": [
                    "Introduction and Setup",
                    "Fundamentals",
                    "Intermediate Concepts",
                    "Advanced Topics",
                    "Real-World Projects"
                ],
                "lesson_components": [
                    "Theory",
                    "Code Examples",
                    "Hands-on Practice",
                    "Debugging Exercises",
                    "Mini-Project"
                ]
            },
            "assessment_types": [
                "Multiple Choice Questions",
                "Coding Challenges",
                "Code Review Questions",
                "Project-based Assessment"
            ]
        }
    
    @staticmethod
    def get_business_template() -> Dict:
        """Template for business and management courses"""
        return {
            "structure": {
                "modules": [
                    "Introduction and Overview",
                    "Core Concepts",
                    "Strategic Framework",
                    "Practical Applications",
                    "Case Studies and Analysis"
                ],
                "lesson_components": [
                    "Theoretical Foundation",
                    "Industry Examples",
                    "Group Discussion Topics",
                    "Case Study Analysis",
                    "Practical Exercises"
                ]
            },
            "assessment_types": [
                "Case Study Analysis",
                "Business Plan Development",
                "Presentation Assessment",
                "Written Reports"
            ]
        }
    
    @staticmethod
    def get_creative_template() -> Dict:
        """Template for creative and design courses"""
        return {
            "structure": {
                "modules": [
                    "Fundamentals and Inspiration",
                    "Tools and Techniques",
                    "Creative Process",
                    "Portfolio Development",
                    "Professional Practice"
                ],
                "lesson_components": [
                    "Visual Examples",
                    "Technique Demonstration",
                    "Guided Practice",
                    "Peer Review",
                    "Creative Projects"
                ]
            },
            "assessment_types": [
                "Portfolio Review",
                "Project Critique",
                "Process Documentation",
                "Final Creative Project"
            ]
        }
    
    @staticmethod
    def get_science_template() -> Dict:
        """Template for science courses"""
        return {
            "structure": {
                "modules": [
                    "Scientific Foundations",
                    "Core Principles",
                    "Experimental Methods",
                    "Applications",
                    "Current Research"
                ],
                "lesson_components": [
                    "Concept Explanation",
                    "Visual Demonstrations",
                    "Lab Exercises",
                    "Data Analysis",
                    "Research Review"
                ]
            },
            "assessment_types": [
                "Lab Reports",
                "Problem Sets",
                "Research Paper Review",
                "Experimental Design"
            ]
        }
    
    @staticmethod
    def get_template_by_category(category: str) -> Dict:
        """Get template based on course category"""
        templates = {
            "programming": CourseTemplates.get_programming_template(),
            "technology": CourseTemplates.get_programming_template(),
            "business": CourseTemplates.get_business_template(),
            "management": CourseTemplates.get_business_template(),
            "creative": CourseTemplates.get_creative_template(),
            "design": CourseTemplates.get_creative_template(),
            "science": CourseTemplates.get_science_template(),
            "engineering": CourseTemplates.get_science_template()
        }
        
        return templates.get(category.lower(), {
            "structure": {
                "modules": [
                    "Introduction",
                    "Fundamentals",
                    "Advanced Topics",
                    "Practical Application",
                    "Final Project"
                ],
                "lesson_components": [
                    "Theory",
                    "Examples",
                    "Practice",
                    "Assessment"
                ]
            },
            "assessment_types": [
                "Quizzes",
                "Assignments",
                "Projects",
                "Final Assessment"
            ]
        })


class LearningPathways:
    """Define learning pathways and prerequisites"""
    
    @staticmethod
    def get_beginner_pathway() -> List[str]:
        """Learning pathway for beginners"""
        return [
            "Start with foundational concepts",
            "Build basic skills through guided practice",
            "Apply skills in simple projects",
            "Gradually increase complexity",
            "Develop confidence through repetition"
        ]
    
    @staticmethod
    def get_intermediate_pathway() -> List[str]:
        """Learning pathway for intermediate learners"""
        return [
            "Review and solidify fundamentals",
            "Explore advanced concepts",
            "Work on real-world scenarios",
            "Develop problem-solving strategies",
            "Build portfolio projects"
        ]
    
    @staticmethod
    def get_advanced_pathway() -> List[str]:
        """Learning pathway for advanced learners"""
        return [
            "Deep dive into specialized topics",
            "Analyze complex case studies",
            "Contribute to advanced projects",
            "Research cutting-edge developments",
            "Mentor and teach others"
        ]


class AssessmentBuilder:
    """Build various types of assessments"""
    
    @staticmethod
    def get_quiz_template() -> Dict:
        """Template for quiz questions"""
        return {
            "type": "multiple_choice",
            "components": {
                "question": "Clear, specific question",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "Why this is correct"
            }
        }
    
    @staticmethod
    def get_project_template() -> Dict:
        """Template for project assignments"""
        return {
            "type": "project",
            "components": {
                "title": "Project Title",
                "description": "What students will build",
                "objectives": ["Objective 1", "Objective 2"],
                "requirements": ["Requirement 1", "Requirement 2"],
                "deliverables": ["Deliverable 1", "Deliverable 2"],
                "evaluation_criteria": {
                    "functionality": "40%",
                    "code_quality": "30%",
                    "documentation": "20%",
                    "creativity": "10%"
                }
            }
        }
    
    @staticmethod
    def get_essay_template() -> Dict:
        """Template for essay questions"""
        return {
            "type": "essay",
            "components": {
                "prompt": "Essay question or prompt",
                "word_count": "500-750 words",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "evaluation_criteria": [
                    "Clarity of argument",
                    "Supporting evidence",
                    "Organization",
                    "Writing quality"
                ]
            }
        }


class ContentGuidelines:
    """Guidelines for creating effective course content"""
    
    @staticmethod
    def get_lesson_structure() -> Dict:
        """Recommended lesson structure"""
        return {
            "introduction": {
                "duration": "5-10 minutes",
                "components": [
                    "Hook/Attention grabber",
                    "Learning objectives",
                    "Connection to previous lessons"
                ]
            },
            "main_content": {
                "duration": "30-40 minutes",
                "components": [
                    "Concept explanation",
                    "Examples and demonstrations",
                    "Guided practice",
                    "Independent practice"
                ]
            },
            "conclusion": {
                "duration": "5-10 minutes",
                "components": [
                    "Summary of key points",
                    "Preview of next lesson",
                    "Assignment or homework"
                ]
            }
        }
    
    @staticmethod
    def get_engagement_strategies() -> List[str]:
        """Strategies to engage learners"""
        return [
            "Use real-world examples and scenarios",
            "Include interactive elements and activities",
            "Vary content delivery methods (text, video, audio)",
            "Provide opportunities for collaboration",
            "Offer choices and personalization options",
            "Include frequent checkpoints and feedback",
            "Make content relevant to learner goals",
            "Use storytelling and narratives"
        ]
    
    @staticmethod
    def get_accessibility_guidelines() -> List[str]:
        """Guidelines for accessible content"""
        return [
            "Use clear, simple language",
            "Provide alternative text for images",
            "Include captions for videos",
            "Ensure sufficient color contrast",
            "Use descriptive link text",
            "Organize content with clear headings",
            "Provide transcripts for audio content",
            "Support keyboard navigation"
        ]
