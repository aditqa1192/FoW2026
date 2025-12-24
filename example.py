"""
Example usage of the Course Content Agent
Run this script to test the agent functionality
"""

import os
from dotenv import load_dotenv
from agent import CourseContentAgent, generate_markdown_course, generate_html_course
from utils import export_all_formats

# Load environment variables
load_dotenv()


def main():
    """Main example function"""
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your Google API key")
        print("Example: GOOGLE_API_KEY=your_key_here")
        return
    
    print("🚀 Lilaq Course Content Agent - Example Usage\n")
    
    # Initialize the agent
    print("Initializing agent...")
    agent = CourseContentAgent(api_key=api_key)
    
    # Define course parameters
    topic = "Introduction to Machine Learning"
    duration_weeks = 4
    difficulty = "beginner"
    target_audience = "software developers new to AI"
    
    print(f"\n📚 Generating course: {topic}")
    print(f"   Duration: {duration_weeks} weeks")
    print(f"   Difficulty: {difficulty}")
    print(f"   Audience: {target_audience}\n")
    
    # Generate course content
    try:
        course = agent.generate_complete_course(
            topic=topic,
            duration_weeks=duration_weeks,
            difficulty=difficulty,
            target_audience=target_audience,
            lessons_per_module=3  # Fewer lessons for faster generation
        )
        
        print("\n✅ Course generation complete!\n")
        
        # Export to dictionary
        course_dict = agent.export_to_dict(course)
        
        # Display summary
        print("=" * 60)
        print(f"Course: {course_dict['title']}")
        print(f"Modules: {len(course_dict['modules'])}")
        total_lessons = sum(len(m['lessons']) for m in course_dict['modules'])
        print(f"Total Lessons: {total_lessons}")
        print("=" * 60)
        
        # Generate different formats
        print("\n📝 Generating export formats...")
        markdown = generate_markdown_course(course_dict)
        html = generate_html_course(course_dict)
        
        # Export all formats
        print("💾 Exporting to files...")
        exports = export_all_formats(course_dict, markdown, html, "example_ml_course")
        
        print("\n✨ Export complete!")
        for format_name, filepath in exports.items():
            print(f"   {format_name.upper()}: {filepath}")
        
        print("\n🎉 Done! Check the exports directory for the generated files.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
