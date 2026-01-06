# HTML UI Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              HTML UI (index.html)                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │    │
│  │  │  Header  │  │ Sidebar  │  │  Main Content    │     │    │
│  │  │  Logo    │  │ Config   │  │  - Input         │     │    │
│  │  │  Title   │  │ About    │  │  - Validation    │     │    │
│  │  └──────────┘  └──────────┘  │  - Generation    │     │    │
│  │                               │  - Display       │     │    │
│  │                               │  - Export        │     │    │
│  │                               └──────────────────┘     │    │
│  └───────────────────┬────────────────────────────────────┘    │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────┐    │
│  │           JavaScript (app.js)                           │    │
│  │  - Event Handlers                                       │    │
│  │  - API Communication (Fetch)                            │    │
│  │  - DOM Manipulation                                     │    │
│  │  - State Management                                     │    │
│  └───────────────────┬────────────────────────────────────┘    │
│                      │                                           │
│  ┌───────────────────▼────────────────────────────────────┐    │
│  │             CSS (style.css)                             │    │
│  │  - Layout (Grid, Flexbox)                               │    │
│  │  - Styling (Colors, Typography)                         │    │
│  │  - Responsive Design                                    │    │
│  │  - Animations                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    FLASK SERVER (app_flask.py)                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Route Handlers                        │  │
│  │                                                           │  │
│  │  GET  /                  → render_template('index.html') │  │
│  │  POST /api/validate      → validate_requirements()       │  │
│  │  POST /api/generate-course → generate_course()           │  │
│  │  POST /api/generate-roadmap → generate_roadmap()         │  │
│  │  GET  /api/export/<fmt>  → export_course(format)         │  │
│  │  GET  /api/export-roadmap/<fmt> → export_roadmap(format) │  │
│  │  POST /api/clear         → clear_data()                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐ │
│  │              In-Memory Storage                            │ │
│  │  course_storage = {                                       │ │
│  │      'course_content': None,                              │ │
│  │      'course_roadmap': None                               │ │
│  │  }                                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      UTILITIES LAYER                             │
│                                                                   │
│  ┌────────────────────┐  ┌────────────────────┐                │
│  │ extract_params.py  │  │   export.py        │                │
│  │ - NLP Extraction   │  │ - JSON Export      │                │
│  │ - Validation       │  │ - Markdown Export  │                │
│  └────────────────────┘  │ - HTML Export      │                │
│                          │ - PDF Export       │                │
│  ┌────────────────────┐  └────────────────────┘                │
│  │ logger_config.py   │                                         │
│  │ - Log Setup        │                                         │
│  │ - File Logging     │                                         │
│  └────────────────────┘                                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        AGENT LAYER                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         CourseContentAgentLangChain                     │    │
│  │  - generate_complete_course()                           │    │
│  │  - generate_module()                                    │    │
│  │  - export_to_dict()                                     │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            CourseRoadmapAgent                           │    │
│  │  - generate_roadmap_from_modules()                      │    │
│  │  - generate_summary_table()                             │    │
│  │  - export_to_dict()                                     │    │
│  │  - export_to_pdf()                                      │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      AI MODEL LAYER                              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Google Gemini API                          │    │
│  │  - Model: gemini-2.5-flash                              │    │
│  │  - Natural Language Processing                          │    │
│  │  - Course Content Generation                            │    │
│  │  - Structured Output                                    │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

## Request Flow

### Course Generation Flow

```
User Action: Click "Generate Course Content"
     │
     ▼
┌─────────────────────────────────────────────┐
│ 1. JavaScript (app.js)                      │
│    - Capture user input                     │
│    - Validate prompt exists                 │
│    - Show loading indicator                 │
└────────┬────────────────────────────────────┘
         │
         │ POST /api/generate-course
         │ { "prompt": "..." }
         ▼
┌─────────────────────────────────────────────┐
│ 2. Flask Route (app_flask.py)               │
│    - Receive JSON request                   │
│    - Check API key configured               │
│    - Extract parameters                     │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 3. Parameter Extraction                     │
│    (extract_course_parameters)              │
│    - Parse prompt with regex                │
│    - Extract topic, duration, etc.          │
│    - Apply defaults                         │
│    - Validate required fields               │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 4. Agent Initialization                     │
│    CourseContentAgentLangChain              │
│    - Configure Gemini API                   │
│    - Set generation parameters              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 5. Course Generation                        │
│    agent.generate_complete_course()         │
│    - Generate outline                       │
│    - Create modules (parallel)              │
│    - Generate lessons                       │
│    - Create assessments                     │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 6. Google Gemini API                        │
│    - Process prompts                        │
│    - Generate structured content            │
│    - Return JSON responses                  │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 7. Export to Dictionary                     │
│    agent.export_to_dict()                   │
│    - Convert Pydantic models to dict        │
│    - Store in course_storage                │
└────────┬────────────────────────────────────┘
         │
         │ JSON Response
         │ { "success": true, "course": {...} }
         ▼
┌─────────────────────────────────────────────┐
│ 8. JavaScript Response Handler              │
│    - Store courseData                       │
│    - Call displayCourse()                   │
│    - Hide loading indicator                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│ 9. DOM Update                               │
│    - Render course summary                  │
│    - Display modules and lessons            │
│    - Create expandable sections             │
│    - Enable export buttons                  │
└─────────────────────────────────────────────┘
```

## Component Interaction

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ User clicks "Generate"
       ▼
┌──────────────────────────────┐
│  JavaScript Event Handler    │
│  (generateBtn.click)          │
└──────┬───────────────────────┘
       │
       │ fetch('/api/generate-course')
       ▼
┌──────────────────────────────┐
│    Flask Route Handler       │
│    @app.route('/api/...')    │
└──────┬───────────────────────┘
       │
       │ extract_course_parameters()
       ▼
┌──────────────────────────────┐
│  Parameter Extraction        │
│  (utils/extract_params.py)   │
└──────┬───────────────────────┘
       │
       │ CourseContentAgentLangChain()
       ▼
┌──────────────────────────────┐
│   Agent Initialization       │
│   (agent/course_agent_...)   │
└──────┬───────────────────────┘
       │
       │ generate_complete_course()
       ▼
┌──────────────────────────────┐
│   Google Gemini API Call     │
│   (google.generativeai)      │
└──────┬───────────────────────┘
       │
       │ JSON Response
       ▼
┌──────────────────────────────┐
│  Store in course_storage     │
│  Return JSON to client       │
└──────┬───────────────────────┘
       │
       │ Response JSON
       ▼
┌──────────────────────────────┐
│  JavaScript Process Response │
│  displayCourse(courseData)   │
└──────┬───────────────────────┘
       │
       │ Update DOM
       ▼
┌──────────────────────────────┐
│  Render Course Content       │
│  Show on Page                │
└──────────────────────────────┘
```

## Data Flow

```
User Input (Natural Language)
    │
    ├─→ [JavaScript] Capture & Validate
    │
    ├─→ [Flask API] Receive Request
    │
    ├─→ [Extraction] Parse Parameters
    │        │
    │        ├─ Topic: "Python"
    │        ├─ Duration: 4 weeks
    │        ├─ Difficulty: "beginner"
    │        ├─ Audience: "beginners"
    │        └─ Lessons: 4 per module
    │
    ├─→ [Agent] Generate Course
    │        │
    │        ├─ Outline
    │        ├─ Modules (4)
    │        │    └─ Lessons (4 each)
    │        │         ├─ Objectives
    │        │         ├─ Content
    │        │         ├─ Activities
    │        │         └─ Assessments
    │        │
    │        └─→ [Gemini API] AI Generation
    │
    ├─→ [Storage] Store course_storage
    │
    └─→ [Response] JSON to Browser
             │
             └─→ [Display] Render HTML
```

## File Dependencies

```
app_flask.py
    ├── depends on: flask
    ├── depends on: agent.CourseContentAgentLangChain
    ├── depends on: agent.roadmap_agent
    ├── depends on: utils.extract_params
    ├── depends on: utils.export
    └── depends on: utils.logger_config

templates/web/index.html
    ├── depends on: static/css/style.css
    └── depends on: static/js/app.js

static/js/app.js
    └── makes API calls to: app_flask.py routes

utils/extract_params.py
    └── standalone (regex-based)

agent/course_agent_langchain.py
    ├── depends on: langchain
    ├── depends on: google.generativeai
    └── depends on: pydantic models

agent/roadmap_agent.py
    ├── depends on: langchain
    └── depends on: agent.CourseContent (for type hints)
```

## State Management

```
Client Side (JavaScript):
┌────────────────────┐
│ Global Variables   │
│ - courseData       │
│ - roadmapData      │
└────────────────────┘

Server Side (Python):
┌────────────────────┐
│ In-Memory Dict     │
│ course_storage = { │
│   'course_content',│
│   'course_roadmap' │
│ }                  │
└────────────────────┘

Note: For production, use:
- Redis for caching
- PostgreSQL for persistence
- Sessions for user data
```

## Security Architecture

```
┌──────────────────┐
│   .env File      │  ← API Keys, Secrets
│   (Not in Git)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Environment     │
│  Variables       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Flask Config    │  ← Load secrets
│  app.config[]    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Request         │  ← Validate input
│  Validation      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  API Call        │  ← Use secret key
│  (Gemini)        │
└──────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│           Production Setup               │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────┐      ┌──────────────┐  │
│  │   Nginx    │──────▶│  Gunicorn   │  │
│  │  (Proxy)   │      │  (4 workers) │  │
│  └────────────┘      └──────┬───────┘  │
│                             │           │
│                      ┌──────▼───────┐  │
│                      │ Flask App    │  │
│                      │ app_flask.py │  │
│                      └──────┬───────┘  │
│                             │           │
│                      ┌──────▼───────┐  │
│                      │  Gemini API  │  │
│                      └──────────────┘  │
│                                          │
└─────────────────────────────────────────┘
```

This architecture provides a scalable, maintainable, and performant HTML-based UI for the Lilaq Course Content Agent!
