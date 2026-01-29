"""
Comprehensive Test Script for Course Content Agent
Tests PDF generation, roadmap generation, and all export formats
"""

import os
import sys
from dotenv import load_dotenv
from agent import CourseContentAgent, generate_markdown_course, generate_html_course
from agent.course_agent_langchain import CourseContentAgentLangChain
from agent.roadmap_agent import CourseRoadmapAgent, format_roadmap_summary
from agent.content_generator import export_course_to_pdf
from utils import export_all_formats

# Load environment variables
load_dotenv()


def check_environment():
    """Check if environment is properly configured"""
    print("=" * 80)
    print("🔍 ENVIRONMENT CHECK")
    print("=" * 80)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your Google API key")
        return False
    
    print("✅ GOOGLE_API_KEY found")
    
    # Check for required packages
    try:
        import streamlit
        print("✅ Streamlit installed")
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    
    try:
        import xhtml2pdf
        print("✅ xhtml2pdf installed (PDF generation)")
    except ImportError:
        print("⚠️  xhtml2pdf not installed - PDF generation will fail")
        print("   Run: pip install xhtml2pdf")
    
    try:
        import markdown2
        print("✅ markdown2 installed")
    except ImportError:
        print("⚠️  markdown2 not installed")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ LangChain Google GenAI installed")
    except ImportError:
        print("❌ LangChain Google GenAI not installed")
        return False
    
    print("\n✅ Environment check passed!\n")
    return True


def test_course_generation():
    """Test basic course generation"""
    print("=" * 80)
    print("📚 TEST 1: COURSE GENERATION (LangChain)")
    print("=" * 80)
    
    try:
        agent = CourseContentAgentLangChain()
        print("✅ Agent initialized")
        
        # Generate a simple course
        print("\nGenerating course: 'Python Basics'")
        print("Parameters: 2 weeks, beginner, 2 lessons per module")
        
        course = agent.generate_complete_course(
            topic="Python Basics",
            duration_weeks=2,
            difficulty="beginner",
            target_audience="complete beginners",
            lessons_per_module=2  # Small for faster testing
        )
        
        print(f"\n✅ Course generated successfully!")
        print(f"   Title: {course.title}")
        print(f"   Modules: {len(course.modules)}")
        total_lessons = sum(len(module.lessons) for module in course.modules)
        print(f"   Total Lessons: {total_lessons}")
        print(f"   Duration: {course.duration_weeks} weeks")
        
        return course
        
    except Exception as e:
        print(f"\n❌ Course generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_export_formats(course):
    """Test all export formats"""
    print("\n" + "=" * 80)
    print("📝 TEST 2: EXPORT FORMATS")
    print("=" * 80)
    
    if not course:
        print("⚠️  Skipping export test - no course to export")
        return None
    
    try:
        # Create outputs directory
        os.makedirs("test_outputs", exist_ok=True)
        
        # Export to dict
        course_dict = course.model_dump()
        print("✅ Exported to dictionary")
        
        # Generate markdown
        markdown = generate_markdown_course(course_dict)
        print("✅ Generated Markdown format")
        
        # Generate HTML
        html = generate_html_course(course_dict)
        print("✅ Generated HTML format")
        
        # Export all formats
        exports = export_all_formats(course_dict, markdown, html, "test_course", "test_outputs")
        print("\n✅ All formats exported:")
        for format_name, filepath in exports.items():
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"   {format_name.upper()}: {filepath} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚠️  {format_name.upper()}: File not created")
        
        return course_dict
        
    except Exception as e:
        print(f"\n❌ Export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_pdf_generation(course_dict):
    """Test PDF generation"""
    print("\n" + "=" * 80)
    print("📄 TEST 3: PDF GENERATION")
    print("=" * 80)
    
    if not course_dict:
        print("⚠️  Skipping PDF test - no course data")
        return False
    
    try:
        import xhtml2pdf
        print("✅ xhtml2pdf library available")
    except ImportError:
        print("❌ xhtml2pdf not installed - skipping PDF test")
        print("   Install with: pip install xhtml2pdf")
        return False
    
    try:
        pdf_path = "test_outputs/test_course.pdf"
        
        # Generate PDF
        print(f"\nGenerating PDF: {pdf_path}")
        success = export_course_to_pdf(course_dict, pdf_path)
        
        if success and os.path.exists(pdf_path):
            size_kb = os.path.getsize(pdf_path) / 1024
            print(f"✅ PDF generated successfully!")
            print(f"   Location: {pdf_path}")
            print(f"   Size: {size_kb:.1f} KB")
            return True
        else:
            print("❌ PDF generation failed - file not created")
            return False
            
    except Exception as e:
        print(f"\n❌ PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_roadmap_generation(course):
    """Test roadmap generation from course"""
    print("\n" + "=" * 80)
    print("🗺️  TEST 4: ROADMAP GENERATION")
    print("=" * 80)
    
    if not course:
        print("⚠️  Skipping roadmap test - no course available")
        return None
    
    try:
        roadmap_agent = CourseRoadmapAgent()
        print("✅ Roadmap agent initialized")
        
        # Convert course modules to dict format
        modules_data = [module.model_dump() for module in course.modules]
        
        print(f"\nGenerating roadmap for: {course.title}")
        print(f"Modules: {len(modules_data)}")
        
        roadmap = roadmap_agent.generate_roadmap_from_modules(
            course_title=course.title,
            modules=modules_data,
            duration_weeks=course.duration_weeks,
            difficulty=course.difficulty_level,
            hours_per_week=5.0,
            start_date="2026-02-01"
        )
        
        print(f"\n✅ Roadmap generated successfully!")
        print(f"   Duration: {roadmap.total_duration_weeks} weeks")
        print(f"   Total Hours: {roadmap.total_estimated_hours}")
        print(f"   Start: {roadmap.start_date}")
        print(f"   End: {roadmap.end_date}")
        print(f"   Weekly Schedule Entries: {len(roadmap.weekly_schedule)}")
        print(f"   Milestones: {len(roadmap.milestones)}")
        
        # Export roadmap
        roadmap_path = "test_outputs/test_roadmap.json"
        roadmap_agent.export_to_json(roadmap, roadmap_path)
        
        if os.path.exists(roadmap_path):
            size_kb = os.path.getsize(roadmap_path) / 1024
            print(f"\n   Exported to: {roadmap_path} ({size_kb:.1f} KB)")
        
        # Display summary
        print("\n" + format_roadmap_summary(roadmap))
        
        return roadmap
        
    except Exception as e:
        print(f"\n❌ Roadmap generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_custom_parameters():
    """Test course generation with custom parameters"""
    print("\n" + "=" * 80)
    print("⚙️  TEST 5: CUSTOM PARAMETERS")
    print("=" * 80)
    
    try:
        agent = CourseContentAgentLangChain()
        
        custom_outcomes = [
            "Build a REST API using Python",
            "Implement database operations",
            "Deploy applications to cloud"
        ]
        
        detailed_topics = "Flask framework, SQLAlchemy ORM, PostgreSQL, Docker, AWS deployment"
        
        print("Generating course with custom parameters:")
        print(f"   Custom outcomes: {len(custom_outcomes)}")
        print(f"   Detailed topics: {detailed_topics}")
        
        course = agent.generate_complete_course(
            topic="Python Web Development",
            duration_weeks=2,
            difficulty="intermediate",
            target_audience="Python developers",
            lessons_per_module=2,
            custom_learning_outcomes=custom_outcomes,
            detailed_topics=detailed_topics
        )
        
        print(f"\n✅ Custom course generated!")
        print(f"   Title: {course.title}")
        print(f"   Learning outcomes match: {len(course.learning_outcomes)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Custom parameters test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 COURSE CONTENT AGENT - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues and try again.")
        return
    
    # Test results
    results = {
        "Environment": True,
        "Course Generation": False,
        "Export Formats": False,
        "PDF Generation": False,
        "Roadmap Generation": False,
        "Custom Parameters": False
    }
    
    # Run tests
    course = test_course_generation()
    if course:
        results["Course Generation"] = True
        
        course_dict = test_export_formats(course)
        if course_dict:
            results["Export Formats"] = True
            
            if test_pdf_generation(course_dict):
                results["PDF Generation"] = True
        
        if test_roadmap_generation(course):
            results["Roadmap Generation"] = True
    
    if test_custom_parameters():
        results["Custom Parameters"] = True
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("=" * 80)
    
    # Check output files
    if os.path.exists("test_outputs"):
        print("\n📁 Generated test files in 'test_outputs' directory:")
        for file in os.listdir("test_outputs"):
            filepath = os.path.join("test_outputs", file)
            if os.path.isfile(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"   - {file} ({size_kb:.1f} KB)")
    
    print("\n✨ Test suite complete!\n")


if __name__ == "__main__":
    main()
