"""
Example usage of the Course Roadmap Agent
Demonstrates how to generate learning roadmaps for courses
"""

import os
from dotenv import load_dotenv
from agent import CourseRoadmapAgent, CourseContentAgent

# Load environment variables
load_dotenv()

def example_roadmap_from_course():
    """Generate a roadmap from a complete course"""
    print("=== Example 1: Generate Roadmap from Complete Course ===\n")
    
    # First, generate a course
    course_agent = CourseContentAgent()
    print("Generating a sample course...")
    course = course_agent.generate_complete_course(
        topic="Python Programming",
        duration_weeks=4,
        difficulty="beginner",
        target_audience="aspiring developers",
        lessons_per_module=3
    )
    
    print(f"\nCourse generated: {course.title}")
    print(f"Modules: {len(course.modules)}")
    
    # Now generate a roadmap
    roadmap_agent = CourseRoadmapAgent()
    print("\nGenerating course roadmap...")
    
    # Convert course modules to dict format
    modules_data = [module.model_dump() for module in course.modules]
    
    roadmap = roadmap_agent.generate_roadmap_from_modules(
        course_title=course.title,
        modules=modules_data,
        duration_weeks=course.duration_weeks,
        difficulty=course.difficulty_level,
        hours_per_week=5.0,
        start_date="2026-01-13"  # Next Monday
    )
    
    print(f"\n✅ Roadmap Generated!")
    print(f"Duration: {roadmap.total_duration_weeks} weeks")
    print(f"Total Hours: {roadmap.total_estimated_hours}")
    print(f"Weekly Schedule Entries: {len(roadmap.weekly_schedule)}")
    print(f"Milestones: {len(roadmap.milestones)}")
    
    # Display the roadmap
    print("\n" + "="*80)
    print(roadmap_agent.format_roadmap_markdown(roadmap))
    
    # Export to file
    roadmap_agent.export_to_json(roadmap, "outputs/python_roadmap.json")
    
    return roadmap


def example_roadmap_from_outline():
    """Generate a roadmap from just module titles"""
    print("\n\n=== Example 2: Generate Roadmap from Module Titles ===\n")
    
    roadmap_agent = CourseRoadmapAgent()
    
    # Define course with just module titles
    course_title = "Web Development Fundamentals"
    module_titles = [
        "Introduction to HTML & CSS",
        "JavaScript Basics",
        "Responsive Design",
        "Introduction to React",
        "Building Real Projects",
        "Deployment & Best Practices"
    ]
    
    print(f"Course: {course_title}")
    print(f"Modules: {len(module_titles)}")
    
    # Generate roadmap
    roadmap = roadmap_agent.generate_roadmap_from_outline(
        course_title=course_title,
        module_titles=module_titles,
        duration_weeks=8,
        difficulty="intermediate",
        hours_per_week=6.0,
        start_date="2026-02-01"
    )
    
    print(f"\n✅ Roadmap Generated!")
    print(f"Duration: {roadmap.total_duration_weeks} weeks")
    print(f"Total Hours: {roadmap.total_estimated_hours}")
    print(f"Start: {roadmap.start_date}")
    print(f"End: {roadmap.end_date}")
    
    # Display weekly schedule
    print("\nWeekly Schedule:")
    for week in roadmap.weekly_schedule:
        print(f"\n{week.week_title}")
        print(f"  Topics: {', '.join(week.topics[:3])}")
        print(f"  Hours: {week.estimated_hours}")
        if week.deliverables:
            print(f"  Due: {week.deliverables[0]}")
    
    # Export to file
    roadmap_agent.export_to_json(roadmap, "outputs/webdev_roadmap.json")
    
    return roadmap


def example_custom_roadmap():
    """Generate a custom roadmap with specific requirements"""
    print("\n\n=== Example 3: Custom Roadmap for Data Science ===\n")
    
    roadmap_agent = CourseRoadmapAgent()
    
    # Define a data science course structure
    course_title = "Data Science with Python - Complete Bootcamp"
    module_titles = [
        "Python Fundamentals for Data Science",
        "NumPy and Pandas Essentials",
        "Data Visualization with Matplotlib & Seaborn",
        "Statistical Analysis and Probability",
        "Machine Learning Basics",
        "Advanced ML Algorithms",
        "Deep Learning Introduction",
        "Capstone Project"
    ]
    
    # Generate intensive 12-week bootcamp roadmap
    roadmap = roadmap_agent.generate_roadmap_from_outline(
        course_title=course_title,
        module_titles=module_titles,
        duration_weeks=12,
        difficulty="intermediate",
        hours_per_week=10.0,  # Intensive bootcamp
        start_date="2026-03-01"
    )
    
    print(f"✅ {roadmap.course_title}")
    print(f"📅 {roadmap.start_date} to {roadmap.end_date}")
    print(f"⏱️  {roadmap.total_estimated_hours} total hours")
    print(f"📚 {roadmap.total_modules} modules")
    print(f"🎯 {len(roadmap.milestones)} milestones")
    
    # Show milestones
    print("\nKey Milestones:")
    for milestone in roadmap.milestones:
        print(f"  Week {milestone.week}: {milestone.title} ({milestone.type})")
    
    # Show study tips
    print("\nStudy Tips:")
    for idx, tip in enumerate(roadmap.study_tips[:3], 1):
        print(f"  {idx}. {tip}")
    
    # Export
    roadmap_agent.export_to_json(roadmap, "outputs/datascience_roadmap.json")
    
    # Save markdown version
    markdown = roadmap_agent.format_roadmap_markdown(roadmap)
    with open("outputs/datascience_roadmap.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    print("\n📄 Markdown roadmap saved to outputs/datascience_roadmap.md")
    
    return roadmap


if __name__ == "__main__":
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    print("🎓 Course Roadmap Agent - Examples\n")
    print("="*80)
    
    try:
        # Run examples
        roadmap1 = example_roadmap_from_course()
        roadmap2 = example_roadmap_from_outline()
        roadmap3 = example_custom_roadmap()
        
        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("\nGenerated files:")
        print("  - outputs/python_roadmap.json")
        print("  - outputs/webdev_roadmap.json")
        print("  - outputs/datascience_roadmap.json")
        print("  - outputs/datascience_roadmap.md")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
