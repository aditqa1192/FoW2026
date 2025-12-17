# OKIR Course Content Agent - React UI

A modern web application for generating comprehensive AI-powered course content using React frontend and Flask backend.

## 🚀 Features

- **AI-Powered Generation**: Uses Google Gemini AI to generate complete course content
- **Interactive UI**: Modern React interface with real-time updates
- **Comprehensive Content**: Generates modules, lessons, assessments, and activities
- **Multiple Export Formats**: Export as JSON, Markdown, or HTML
- **Customizable Parameters**: Adjust duration, difficulty, target audience, and more

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Google API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🛠️ Installation

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Start the Flask backend:
```bash
python backend_api.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## 🎯 Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter your Google API Key in the sidebar
3. Fill in the course parameters:
   - Course Topic
   - Duration (weeks)
   - Difficulty Level
   - Target Audience
   - Lessons per Module
4. Click "Generate Course Content"
5. View and explore the generated content
6. Export in your preferred format (JSON, Markdown, or HTML)

## 📁 Project Structure

```
.
├── backend_api.py          # Flask REST API
├── agent/                  # Course generation logic
│   ├── course_agent.py
│   └── content_generator.py
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx         # Main app component
│   │   ├── App.css         # Styles
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── vite.config.js
├── templates/              # Course structure templates
├── utils/                  # Export utilities
├── requirements.txt        # Python dependencies
├── app.py                  # Legacy Streamlit app
└── README.md
```

## 🔧 Configuration

### Backend Configuration

Edit environment variables in `.env`:
- `GOOGLE_API_KEY`: Your Google API key
- `GEMINI_MODEL`: AI model to use (default: gemini-2.0-flash-exp)

### Frontend Configuration

The frontend automatically proxies API requests to `http://localhost:5000`. To change this, edit `frontend/vite.config.js`.

## 🚢 Production Build

### Build Frontend
```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`

### Deploy Backend
```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend_api:app
```

## 🌐 API Endpoints

- `POST /api/generate-course` - Generate course content
- `POST /api/export/json` - Export as JSON
- `POST /api/export/md` - Export as Markdown
- `POST /api/export/html` - Export as HTML
- `GET /api/health` - Health check

## 🎨 Tech Stack

**Frontend:**
- React 18
- Vite
- Axios
- React Markdown

**Backend:**
- Flask
- Flask-CORS
- Google Generative AI
- Pydantic

## 📝 Migration from Streamlit

This project was migrated from Streamlit to React for better performance and customization. The original Streamlit version is preserved in `app.py`.

To run the legacy Streamlit version:
```bash
streamlit run app.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT

## 🆘 Support

For issues and questions, please open an issue on GitHub.

---

**Powered by Google Gemini AI** 🤖
