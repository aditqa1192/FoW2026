import { useState } from 'react'
import axios from 'axios'

function CourseForm({ config, isLoading, setIsLoading, setCourseContent, onClear }) {
  const [formData, setFormData] = useState({
    courseTopic: '',
    durationWeeks: 4,
    difficulty: 'beginner',
    targetAudience: 'general learners',
    lessonsPerModule: 4
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'durationWeeks' || name === 'lessonsPerModule' 
        ? parseInt(value) 
        : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!config.apiKey) {
      alert('Please provide a Google API key in the sidebar.')
      return
    }
    
    if (!formData.courseTopic) {
      alert('Please enter a course topic.')
      return
    }

    setIsLoading(true)
    
    try {
      const response = await axios.post('/api/generate-course', {
        ...formData,
        apiKey: config.apiKey,
        model: config.model
      })
      
      setCourseContent(response.data)
    } catch (error) {
      console.error('Error generating course:', error)
      alert(`Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="course-form">
      <h2>🎯 Course Parameters</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Course Topic</label>
          <input
            type="text"
            name="courseTopic"
            value={formData.courseTopic}
            onChange={handleChange}
            placeholder="e.g., Python Programming for Beginners, Digital Marketing Fundamentals"
            disabled={isLoading}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Duration (weeks)</label>
            <input
              type="range"
              name="durationWeeks"
              min="1"
              max="16"
              value={formData.durationWeeks}
              onChange={handleChange}
              disabled={isLoading}
            />
            <span className="range-value">{formData.durationWeeks}</span>
          </div>

          <div className="form-group">
            <label>Difficulty Level</label>
            <select
              name="difficulty"
              value={formData.difficulty}
              onChange={handleChange}
              disabled={isLoading}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Target Audience</label>
            <input
              type="text"
              name="targetAudience"
              value={formData.targetAudience}
              onChange={handleChange}
              placeholder="e.g., college students, professionals, hobbyists"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label>Lessons per Module</label>
            <input
              type="range"
              name="lessonsPerModule"
              min="2"
              max="8"
              value={formData.lessonsPerModule}
              onChange={handleChange}
              disabled={isLoading}
            />
            <span className="range-value">{formData.lessonsPerModule}</span>
          </div>
        </div>

        <div className="button-group">
          <button 
            type="submit" 
            className="btn-primary" 
            disabled={isLoading || !formData.courseTopic || !config.apiKey}
          >
            {isLoading ? '🤖 Generating...' : '🚀 Generate Course Content'}
          </button>
          
          <button 
            type="button" 
            className="btn-secondary" 
            onClick={onClear}
            disabled={isLoading}
          >
            🗑️ Clear
          </button>
        </div>
      </form>
    </div>
  )
}

export default CourseForm
