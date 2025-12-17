import { useState } from 'react'
import axios from 'axios'

function CourseDisplay({ courseContent }) {
  const [expandedModules, setExpandedModules] = useState({})
  const [expandedLessons, setExpandedLessons] = useState({})

  const toggleModule = (index) => {
    setExpandedModules(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const toggleLesson = (key) => {
    setExpandedLessons(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const downloadFile = async (format) => {
    try {
      const response = await axios.post(`/api/export/${format}`, courseContent, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_')
      link.setAttribute('download', `course_${timestamp}.${format}`)
      
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error downloading file:', error)
      alert('Error downloading file')
    }
  }

  const formatSummary = () => {
    const modules = courseContent.modules.length
    const totalLessons = courseContent.modules.reduce((sum, m) => sum + m.lessons.length, 0)
    
    return `Course: ${courseContent.title}
Duration: ${courseContent.duration_weeks} weeks
Modules: ${modules}
Total Lessons: ${totalLessons}
Difficulty: ${courseContent.difficulty_level}
Target Audience: ${courseContent.target_audience}`
  }

  return (
    <div className="course-display">
      <hr />
      <h2>📋 Generated Course Content</h2>
      
      <div className="success-box">
        ✅ Course content generated successfully!
      </div>

      {/* Summary */}
      <div className="section">
        <h3>📊 Course Summary</h3>
        <pre className="summary-box">{formatSummary()}</pre>
      </div>

      {/* Course Overview */}
      <div className="section">
        <h3>📚 Course Overview</h3>
        <h4>{courseContent.title}</h4>
        <p>{courseContent.description}</p>
        
        <div className="overview-grid">
          <div>
            <strong>Target Audience:</strong>
            <p>{courseContent.target_audience}</p>
            
            <strong>Difficulty:</strong>
            <p>{courseContent.difficulty_level.charAt(0).toUpperCase() + courseContent.difficulty_level.slice(1)}</p>
            
            <strong>Duration:</strong>
            <p>{courseContent.duration_weeks} weeks</p>
          </div>
          
          <div>
            <strong>Prerequisites:</strong>
            <ul>
              {courseContent.prerequisites.map((prereq, i) => (
                <li key={i}>{prereq}</li>
              ))}
            </ul>
            
            <strong>Learning Outcomes:</strong>
            <ul>
              {courseContent.learning_outcomes.slice(0, 3).map((outcome, i) => (
                <li key={i}>{outcome}</li>
              ))}
              {courseContent.learning_outcomes.length > 3 && (
                <li>...and {courseContent.learning_outcomes.length - 3} more</li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Modules and Lessons */}
      {courseContent.modules.map((module, moduleIdx) => (
        <div key={moduleIdx} className="module-section">
          <div 
            className="module-header"
            onClick={() => toggleModule(moduleIdx)}
          >
            <h3>📦 Module {moduleIdx + 1}: {module.title}</h3>
            <span className="toggle-icon">
              {expandedModules[moduleIdx] ? '▼' : '▶'}
            </span>
          </div>
          
          {expandedModules[moduleIdx] && (
            <div className="module-content">
              <p><strong>Description:</strong> {module.description}</p>
              <p><strong>Duration:</strong> {module.duration_hours} hours</p>
              
              {module.lessons.map((lesson, lessonIdx) => {
                const lessonKey = `${moduleIdx}-${lessonIdx}`
                
                return (
                  <div key={lessonIdx} className="lesson">
                    <div 
                      className="lesson-header"
                      onClick={() => toggleLesson(lessonKey)}
                    >
                      <h4>Lesson {moduleIdx + 1}.{lessonIdx + 1}: {lesson.title}</h4>
                      <span>⏱️ {lesson.duration_minutes} minutes</span>
                    </div>
                    
                    {expandedLessons[lessonKey] && (
                      <div className="lesson-content">
                        <div className="lesson-section">
                          <strong>🎯 Learning Objectives:</strong>
                          <ul>
                            {lesson.learning_objectives.map((obj, i) => (
                              <li key={i}>{obj}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="lesson-section">
                          <strong>📖 Content:</strong>
                          <p>{lesson.content}</p>
                        </div>
                        
                        <div className="lesson-section">
                          <strong>🔑 Key Points:</strong>
                          <div className="key-points-grid">
                            {lesson.key_points.map((point, i) => (
                              <div key={i}>• {point}</div>
                            ))}
                          </div>
                        </div>
                        
                        <div className="lesson-section">
                          <strong>✏️ Activities:</strong>
                          <ol>
                            {lesson.activities.map((activity, i) => (
                              <li key={i}>{activity}</li>
                            ))}
                          </ol>
                        </div>
                        
                        <div className="lesson-section">
                          <strong>📝 Assessment:</strong>
                          {lesson.assessment_questions.map((q, i) => (
                            <details key={i} className="assessment-question">
                              <summary><strong>Q{i + 1}:</strong> {q.question || 'N/A'}</summary>
                              <p className="answer">{q.answer || 'N/A'}</p>
                            </details>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      ))}

      {/* Export Options */}
      <div className="export-section">
        <h3>💾 Export Options</h3>
        <div className="export-buttons">
          <button onClick={() => downloadFile('json')} className="btn-export">
            📄 Download as JSON
          </button>
          <button onClick={() => downloadFile('md')} className="btn-export">
            📝 Download as Markdown
          </button>
          <button onClick={() => downloadFile('html')} className="btn-export">
            🌐 Download as HTML
          </button>
        </div>
      </div>
    </div>
  )
}

export default CourseDisplay
