import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import CourseForm from './components/CourseForm'
import CourseDisplay from './components/CourseDisplay'

function App() {
  const [courseContent, setCourseContent] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [config, setConfig] = useState({
    apiKey: '',
    model: 'gemini-2.0-flash-exp'
  })

  const handleClear = () => {
    setCourseContent(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="main-header">📚 OKIR Course Content Agent</h1>
        <p className="sub-header">AI-Powered Course Content Generation</p>
      </header>
      
      <div className="app-container">
        <Sidebar config={config} setConfig={setConfig} />
        
        <main className="main-content">
          <CourseForm 
            config={config}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
            setCourseContent={setCourseContent}
            onClear={handleClear}
          />
          
          {courseContent && (
            <CourseDisplay courseContent={courseContent} />
          )}
        </main>
      </div>
      
      <footer className="app-footer">
        <p>OKIR Course Content Agent | Powered by Google Gemini</p>
      </footer>
    </div>
  )
}

export default App
