# Lilaq Course Content Agent - HTML UI

## Overview

This is a modern HTML-based web interface for the Lilaq Course Content Agent, built with Flask and vanilla JavaScript as a replacement for the Streamlit UI. It provides a clean, responsive interface for generating AI-powered course content.

## Features

- **Modern HTML/CSS/JavaScript Interface**: Clean, responsive design that works on all devices
- **Natural Language Input**: Describe your course in plain English
- **Real-time Validation**: Validate course requirements before generation
- **Course Content Generation**: Generate comprehensive course outlines with modules and lessons
- **Roadmap Generation**: Create detailed learning roadmaps with weekly schedules
- **Multiple Export Formats**: Export to JSON, Markdown, HTML, and PDF
- **Interactive Display**: Expandable sections, collapsible modules, and interactive elements
- **No External Dependencies**: Uses vanilla JavaScript (no frameworks required)

## Architecture

### Backend (Flask)
- **app_flask.py**: Main Flask application
- **API Endpoints**:
  - `GET /`: Main page
  - `POST /api/validate`: Validate course requirements
  - `POST /api/generate-course`: Generate course content
  - `POST /api/generate-roadmap`: Generate course roadmap
  - `GET /api/export/<format>`: Export course (json, markdown, html, pdf)
  - `GET /api/export-roadmap/<format>`: Export roadmap (json, markdown, pdf)
  - `POST /api/clear`: Clear stored data

### Frontend
- **templates/web/index.html**: Main HTML template
- **static/css/style.css**: Responsive CSS styles
- **static/js/app.js**: JavaScript application logic

### Utilities
- **utils/extract_params.py**: Natural language parameter extraction

## Setup and Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The key new dependency is Flask:
- `flask==3.0.0`

### 2. Configure Environment

Create or update your `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
```

### 3. Run the Application

```bash
python app_flask.py
```

Or with Flask CLI:

```bash
set FLASK_APP=app_flask.py
flask run
```

The application will be available at: `http://localhost:5000`

## Usage

### 1. Enter Course Requirements

Describe your course in natural language in the text area. For example:

- "Create a Data engineering course for college students. Should be intermediate level and last 6 weeks."
- "I want to learn Python programming for data science. Make it 8 weeks for complete beginners."
- "Build a Web development course for aspiring developers. Intermediate level, 6 weeks."

### 2. Validate Requirements (Optional)

Click "Validate Requirements" to check if all required information has been extracted:
- Course Topic
- Duration (defaults to 4 weeks if not specified)
- Difficulty Level (defaults to beginner)
- Target Audience (defaults to "general learners")
- Lessons per Module (defaults to 4)

### 3. Generate Course Content

Click "Generate Course Content" to create the full course. This will:
- Generate a course outline
- Create detailed modules with lessons
- Include learning objectives, activities, and assessments
- Display the content in an expandable, interactive format

### 4. Generate Roadmap (Optional)

After generating course content, click "Generate Roadmap" to create:
- Weekly schedule
- Study milestones
- Time estimates
- Pacing recommendations

### 5. Export Content

Export your course or roadmap in various formats:
- **JSON**: Machine-readable format
- **Markdown**: For documentation and editing
- **HTML**: Standalone web page
- **PDF**: Printable format (requires xhtml2pdf)

## API Reference

### Validate Requirements

```http
POST /api/validate
Content-Type: application/json

{
  "prompt": "Create a Python course for beginners"
}
```

Response:
```json
{
  "success": true,
  "params": {
    "topic": "Python",
    "duration_weeks": 4,
    "difficulty": "beginner",
    "target_audience": "beginners",
    "lessons_per_module": 4
  },
  "missing": [],
  "is_valid": true
}
```

### Generate Course

```http
POST /api/generate-course
Content-Type: application/json

{
  "prompt": "Create a Python course for beginners, 4 weeks"
}
```

Response:
```json
{
  "success": true,
  "course": {
    "title": "...",
    "description": "...",
    "modules": [...]
  }
}
```

### Generate Roadmap

```http
POST /api/generate-roadmap
Content-Type: application/json
```

Response:
```json
{
  "success": true,
  "roadmap": {
    "course_title": "...",
    "weekly_schedule": [...],
    "milestones": [...]
  },
  "summary_table": "..."
}
```

### Export Course

```http
GET /api/export/{format}
```

Where `format` is one of: `json`, `markdown`, `html`, `pdf`

Returns the course content in the specified format.

### Export Roadmap

```http
GET /api/export-roadmap/{format}
```

Where `format` is one of: `json`, `markdown`, `pdf`

Returns the roadmap in the specified format.

## Comparison: Streamlit vs HTML UI

| Feature | Streamlit UI | HTML UI |
|---------|-------------|---------|
| **Technology** | Streamlit | Flask + HTML/CSS/JS |
| **Deployment** | Streamlit Cloud or server | Any web server |
| **Customization** | Limited | Full control |
| **Performance** | Good | Excellent |
| **Browser Support** | Modern browsers | All browsers |
| **Mobile Support** | Limited | Fully responsive |
| **State Management** | Session state | Client/Server |
| **API Access** | No | Yes (RESTful) |
| **Extensibility** | Moderate | High |

## Advantages of HTML UI

1. **Full Control**: Complete control over UI/UX design
2. **RESTful API**: Can be used by other applications
3. **Better Performance**: No Python overhead for UI rendering
4. **Mobile-Friendly**: Fully responsive design
5. **Standard Web Stack**: Uses familiar web technologies
6. **Easy Deployment**: Deploy to any web server (Apache, Nginx, etc.)
7. **Better SEO**: Can be indexed by search engines
8. **No Session Limitations**: More flexible state management

## File Structure

```
FoW2026/
├── app_flask.py              # Flask application
├── app.py                    # Original Streamlit app (keep for reference)
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
├── templates/
│   └── web/
│       └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css         # Styles
│   └── js/
│       └── app.js            # Client-side logic
├── utils/
│   ├── extract_params.py     # Parameter extraction
│   ├── export.py             # Export utilities
│   └── logger_config.py      # Logging configuration
└── agent/
    ├── course_agent.py       # Course generation
    ├── course_agent_langchain.py
    └── roadmap_agent.py      # Roadmap generation
```

## Customization

### Changing Colors

Edit `static/css/style.css` and modify the CSS variables:

```css
:root {
    --primary-color: #4a90e2;    /* Change this */
    --secondary-color: #7f8c8d;
    --success-color: #28a745;
    /* ... */
}
```

### Adding New Features

1. Add API endpoint in `app_flask.py`
2. Add JavaScript function in `static/js/app.js`
3. Update UI in `templates/web/index.html`

### Custom Styling

Add your styles to `static/css/style.css` or create a new CSS file and link it in the HTML template.

## Troubleshooting

### Port Already in Use

Change the port in `.env`:
```env
PORT=8000
```

### API Key Not Working

1. Check `.env` file exists and has correct API key
2. Restart the Flask application
3. Check console for error messages

### PDF Export Not Working

Install the required library:
```bash
pip install xhtml2pdf
```

### Static Files Not Loading

Check that the `static` folder structure is correct:
```
static/
├── css/
│   └── style.css
└── js/
    └── app.js
```

## Production Deployment

### Using Gunicorn (Recommended)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app_flask:app"]
```

Build and run:
```bash
docker build -t lilaq-course-agent .
docker run -p 5000:5000 --env-file .env lilaq-course-agent
```

### Environment Variables for Production

```env
GOOGLE_API_KEY=your_production_api_key
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
FLASK_DEBUG=False
SECRET_KEY=your-strong-secret-key-here
```

## Security Considerations

1. **Never commit `.env` file** to version control
2. **Use strong SECRET_KEY** in production
3. **Enable HTTPS** in production
4. **Implement rate limiting** for API endpoints
5. **Validate all user inputs** (already implemented)
6. **Set up CORS properly** if using from different domains

## License

Same as the main project.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask and API documentation
3. Check browser console for JavaScript errors
4. Review server logs for backend errors

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Database integration for persistent storage
- [ ] Real-time progress updates with WebSockets
- [ ] Course version history
- [ ] Collaborative editing
- [ ] Advanced analytics and reporting
- [ ] Course templates library
- [ ] Multi-language support
