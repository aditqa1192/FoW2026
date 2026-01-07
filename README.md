# Lilaq Course Content Agent

An intelligent agent that automatically generates comprehensive course content and learning roadmaps based on user-specified topics.

## Features

- 🤖 AI-powered course content generation using Google Gemini
- 📚 Structured curriculum creation (modules, lessons, assessments)
- 🗺️ **NEW: Learning roadmap generation with weekly schedules and milestones**
- 🎨 Interactive web interface
- 📝 Customizable course templates
- 💾 Export course content in multiple formats (JSON, Markdown, HTML)

## Setup

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and add your Google API key
   - Get your API key from: https://makersuite.google.com/app/apikey

4. Run the application:
```bash
streamlit run app.py
```

## Usage

### Generate Course Content

1. Enter your course requirements in natural language
2. Specify course parameters (duration, difficulty level, target audience)
3. Click "Generate Course Content"
4. Review the generated modules, lessons, and assessments
5. Export in your preferred format (JSON, Markdown, or HTML)

### Generate Learning Roadmap

1. After generating a course, click "Generate Roadmap"
2. View the week-by-week learning schedule
3. Review milestones, deliverables, and pacing recommendations
4. Export the roadmap for students or instructors

## Agents

### Course Content Agent
Generates comprehensive course structures including:
- Course outline and learning outcomes
- Detailed modules and lessons
- Learning objectives
- Activities and hands-on exercises
- Assessment questions with answers
- Key takeaways

### Roadmap Agent (NEW)
Creates structured learning timelines including:
- Week-by-week study schedule
- Module distribution across weeks
- Learning milestones (quizzes, projects, checkpoints)
- Estimated study hours per week
- Pacing recommendations
- Study tips for success

## Project Structure

```
FoW2026/
├── app.py                      # Main Streamlit application
├── example.py                  # Example usage of course agent
├── example_roadmap.py          # Example usage of roadmap agent
├── agent/
│   ├── course_agent.py         # Core course generation agent
│   ├── course_agent_langchain.py # LangChain implementation
│   ├── roadmap_agent.py        # NEW: Roadmap generation agent
│   └── content_generator.py    # Content generation utilities
├── templates/
│   └── course_templates.py     # Course structure templates
├── utils/
│   └── export.py               # Export utilities
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Example Usage

### Command Line Usage

```python
from agent import CourseContentAgentLangChain, CourseRoadmapAgent

# Generate course content
course_agent = CourseContentAgentLangChain()
course = course_agent.generate_complete_course(
    topic="Python Programming",
    duration_weeks=6,
    difficulty="beginner",
    target_audience="college students",
    lessons_per_module=4
)

# Generate learning roadmap
roadmap_agent = CourseRoadmapAgent()
modules_data = [module.model_dump() for module in course.modules]
roadmap = roadmap_agent.generate_roadmap_from_modules(
    course_title=course.title,
    modules=modules_data,
    duration_weeks=6,
    difficulty="beginner",
    hours_per_week=5.0,
    start_date="2026-01-13"
)

# Export
course_agent.export_to_json(course, "my_course.json")
roadmap_agent.export_to_json(roadmap, "my_roadmap.json")
```

See `example.py` and `example_roadmap.py` for more detailed examples.

## License

MIT
