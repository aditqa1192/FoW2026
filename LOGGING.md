# Logging Documentation

## Overview
The Course Content Agent application now includes comprehensive logging functionality to track all major operations, debug issues, and monitor system behavior.

## Log Configuration

### Location
- **Log Directory:** `logs/`
- **Log File Format:** `course_agent_YYYYMMDD_HHMMSS.log`
- **Example:** `logs/course_agent_20260102_233823.log`

### Log Levels
- **DEBUG:** Detailed information for diagnosing problems (parameters, intermediate values)
- **INFO:** Confirmation that things are working as expected (operations started/completed)
- **WARNING:** An indication that something unexpected happened
- **ERROR:** A serious problem that prevented a function from completing

### Log Format
```
YYYY-MM-DD HH:MM:SS - module_name - LEVEL - function_name:line_number - message
```

**Example:**
```
2026-01-02 23:38:23 - __main__ - INFO - <module>:25 - Starting Lilaq Course Content Agent application
```

## Logged Operations

### Application Lifecycle
- ✅ Application startup
- ✅ Logging system initialization
- ✅ Configuration loading

### Course Generation
- ✅ Course generation request start (topic, parameters)
- ✅ Module generation progress (module title, count)
- ✅ Lesson generation (lessons per module)
- ✅ Course generation completion (total modules, lessons)
- ✅ Topic validation and mismatch warnings

### Roadmap Generation
- ✅ Roadmap generation start (course title, duration, parameters)
- ✅ Roadmap generation completion (weeks, milestones, total hours)
- ✅ Weekly schedule creation

### PDF Export
- ✅ PDF generation requests (course/roadmap)
- ✅ Temporary file paths
- ✅ PDF generation success/failure
- ✅ Error details for troubleshooting

### UI Operations
- ✅ User button clicks (Generate Course, Generate Roadmap, Generate PDF)
- ✅ Parameter extraction from user input
- ✅ Export operations (JSON, Markdown, HTML, PDF)
- ✅ Error handling and user feedback

## Usage

### Viewing Logs

**View latest log file:**
```powershell
# PowerShell
Get-Content (Get-ChildItem logs/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

**View last 50 lines:**
```powershell
Get-Content (Get-ChildItem logs/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Tail 50
```

**Search for errors:**
```powershell
Select-String -Path "logs/*.log" -Pattern "ERROR"
```

### Log Rotation
Logs are automatically created with timestamps. Old logs are retained for troubleshooting historical issues.

**Manual cleanup (optional):**
```powershell
# Remove logs older than 30 days
Get-ChildItem logs/ -Filter "*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item
```

## Implementation Details

### Logger Configuration (`utils/logger_config.py`)
- Centralized logging setup
- File and console handlers
- Configurable log levels
- Automatic log directory creation

### Module-Level Loggers
Each module uses its own logger:
```python
import logging
logger = logging.getLogger(__name__)

# Usage
logger.info("Operation completed")
logger.debug(f"Parameters: {params}")
logger.error("An error occurred", exc_info=True)
```

### Logged Modules
- ✅ `app.py` - Streamlit UI operations
- ✅ `agent/course_agent.py` - Course generation
- ✅ `agent/roadmap_agent.py` - Roadmap generation
- ✅ `agent/content_generator.py` - Content export
- ✅ `utils/logger_config.py` - Logging configuration

## Example Log Session

```log
2026-01-02 23:38:23 - root - INFO - setup_logging:57 - Logging initialized - Log file: logs\course_agent_20260102_233823.log
2026-01-02 23:38:23 - __main__ - INFO - <module>:25 - Starting Lilaq Course Content Agent application
2026-01-02 23:38:23 - __main__ - INFO - <module>:381 - Starting course generation from UI for topic: prompt engineering
2026-01-02 23:38:23 - __main__ - DEBUG - <module>:382 - Generation parameters: {'topic': 'prompt engineering', 'duration_weeks': 4, 'difficulty': 'beginner', 'target_audience': 'college students', 'lessons_per_module': 4}
2026-01-02 23:40:34 - __main__ - INFO - <module>:400 - Course content generated successfully from UI
```

## Troubleshooting

### Finding Errors
```powershell
# Search all logs for errors
Select-String -Path "logs/*.log" -Pattern "ERROR|WARNING"

# View specific error context
Get-Content logs/course_agent_YYYYMMDD_HHMMSS.log | Select-String -Pattern "ERROR" -Context 5
```

### Debug Mode
The logger is configured with `DEBUG` level by default. To change:

Edit `app.py`:
```python
setup_logging(log_dir="logs", log_level=logging.INFO)  # Less verbose
```

## Best Practices

1. **Regular Monitoring:** Check logs periodically for errors and warnings
2. **Log Retention:** Keep logs for at least 30 days for troubleshooting
3. **Error Investigation:** Use `exc_info=True` in error logs for full stack traces
4. **Performance:** DEBUG logs may impact performance in production; consider INFO level

## Version Control

Log files are excluded from Git via `.gitignore`:
```gitignore
# Logs
logs/
*.log
```

This ensures sensitive data and large log files don't get committed to the repository.
