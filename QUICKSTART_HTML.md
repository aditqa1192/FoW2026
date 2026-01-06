# Quick Start Guide - HTML UI

## 🚀 5-Minute Setup

### Step 1: Check Prerequisites
```bash
# Verify Python 3.11+ is installed
python --version

# You should see: Python 3.11.x or higher
```

### Step 2: Install Flask (if not already installed)
```bash
pip install flask
```

### Step 3: Configure API Key
Create or edit `.env` file:
```env
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=5000
```

### Step 4: Run the Application

**Windows:**
```bash
run_html_ui.bat
```

**Linux/Mac:**
```bash
chmod +x run_html_ui.sh
./run_html_ui.sh
```

**Or manually:**
```bash
python app_flask.py
```

### Step 5: Open Browser
Navigate to: http://localhost:5000

---

## 📋 Quick Command Reference

### Running the App
```bash
# Development mode
python app_flask.py

# With specific port
set PORT=8000 && python app_flask.py  # Windows
PORT=8000 python app_flask.py         # Linux/Mac

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app
```

### Testing the API
```bash
# Test validation endpoint
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Python course for beginners\"}"

# Test course generation
curl -X POST http://localhost:5000/api/generate-course \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Create a Python course for beginners, 4 weeks\"}"
```

---

## 🎯 Common Tasks

### Change the Port
Edit `.env`:
```env
PORT=8000
```

### Enable Debug Mode
Edit `.env`:
```env
FLASK_DEBUG=True
```

### Add Custom Styling
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #your-color;
}
```

### Modify API Endpoints
Edit `app_flask.py`:
```python
@app.route('/api/your-endpoint', methods=['POST'])
def your_function():
    # Your code here
    return jsonify({'success': True})
```

---

## 🐛 Troubleshooting

### Problem: Port already in use
```bash
# Windows - Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac - Find and kill process
lsof -ti:5000 | xargs kill -9
```

### Problem: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: Static files not loading
Check folder structure:
```
static/
├── css/
│   └── style.css
└── js/
    └── app.js
```

### Problem: API key not working
1. Check `.env` file exists
2. Verify API key is correct
3. Restart Flask app
4. Check console for errors

---

## 📚 File Structure Quick Reference

```
FoW2026/
├── app_flask.py              # ← Main Flask app (RUN THIS)
├── templates/web/
│   └── index.html            # ← HTML template
├── static/
│   ├── css/style.css         # ← Styles
│   └── js/app.js             # ← JavaScript
├── utils/
│   └── extract_params.py     # ← Parameter extraction
└── .env                      # ← Configuration
```

---

## 🔥 Quick Examples

### Example 1: Generate Course via API
```python
import requests

response = requests.post('http://localhost:5000/api/generate-course', 
    json={
        'prompt': 'Create a Web Development course for beginners, 6 weeks'
    })

course = response.json()
print(course['course']['title'])
```

### Example 2: Custom JavaScript Function
Add to `static/js/app.js`:
```javascript
function myCustomFunction() {
    console.log('Custom function called');
    // Your code here
}
```

### Example 3: Add New API Endpoint
Add to `app_flask.py`:
```python
@app.route('/api/my-endpoint', methods=['POST'])
def my_endpoint():
    data = request.get_json()
    # Process data
    return jsonify({'success': True, 'result': 'data'})
```

---

## 💡 Tips & Best Practices

1. **Always use .env for secrets** - Never commit API keys
2. **Test locally first** - Before deploying to production
3. **Use version control** - Git is your friend
4. **Check logs** - Flask logs help debug issues
5. **Backup data** - Before major changes

---

## 🆘 Getting Help

1. **Check README_HTML_UI.md** - Comprehensive documentation
2. **Check UI_COMPARISON.md** - Compare with Streamlit
3. **Check console logs** - Browser and server
4. **Review API responses** - Use browser DevTools

---

## 🚢 Deploy to Production

### Option 1: Gunicorn (Linux)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app
```

### Option 2: Docker
```bash
docker build -t lilaq-app .
docker run -p 5000:5000 --env-file .env lilaq-app
```

### Option 3: Cloud Platform
- **Heroku**: Connect repo and deploy
- **AWS**: Use Elastic Beanstalk
- **GCP**: Use App Engine
- **Azure**: Use App Service

---

## ⚡ Performance Tips

1. **Use production WSGI server** (Gunicorn, uWSGI)
2. **Enable gzip compression**
3. **Cache static files**
4. **Use CDN for assets**
5. **Optimize database queries** (if using DB)

---

## 🔒 Security Checklist

- [ ] API key in .env (not in code)
- [ ] Strong SECRET_KEY
- [ ] HTTPS in production
- [ ] Input validation enabled
- [ ] CORS configured properly
- [ ] Rate limiting (if needed)

---

## 📞 Quick Links

- **Main README**: [README_HTML_UI.md](README_HTML_UI.md)
- **Comparison**: [UI_COMPARISON.md](UI_COMPARISON.md)
- **Original Streamlit**: [README.md](README.md)
- **Flask Docs**: https://flask.palletsprojects.com/
- **MDN Web Docs**: https://developer.mozilla.org/

---

**Happy Coding! 🎉**
