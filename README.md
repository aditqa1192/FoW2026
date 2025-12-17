# OKIR Course Content Agent

An intelligent agent that automatically generates comprehensive course content based on user-specified topics.

## Features

- 🤖 AI-powered course content generation using Google Gemini
- 📚 Structured curriculum creation (modules, lessons, assessments)
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

1. Enter your Google API key in the sidebar
2. Enter a course topic (e.g., "Python Programming for Beginners")
3. Specify course parameters (duration, difficulty level, target audience)
4. Select a Gemini model (gemini-2.0-flash-exp, gemini-1.5-pro, or gemini-1.5-flash)
5. Click "Generate Course Content"
6. Review and export the generated content

## Project Structure

```
OKIR-Agent UI/
├── app.py                  # Main Streamlit application
├── agent/
│   ├── course_agent.py     # Core course generation agent
│   └── content_generator.py # Content generation utilities
├── templates/
│   └── course_templates.py # Course structure templates
├── utils/
│   └── export.py           # Export utilities
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # This file
```

## License

MIT
