function Sidebar({ config, setConfig }) {
  const handleChange = (e) => {
    const { name, value } = e.target
    setConfig(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <aside className="sidebar">
      <h2>⚙️ Configuration</h2>
      
      <div className="form-group">
        <label>Google API Key</label>
        <input
          type="password"
          name="apiKey"
          value={config.apiKey}
          onChange={handleChange}
          placeholder="Enter your API key"
        />
        <small>Get your API key at <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">makersuite.google.com</a></small>
      </div>

      <div className="form-group">
        <label>AI Model</label>
        <select
          name="model"
          value={config.model}
          onChange={handleChange}
        >
          <option value="gemini-2.0-flash-exp">gemini-2.0-flash-exp</option>
          <option value="gemini-2.5-flash">gemini-2.5-flash</option>
          <option value="gemini-1.5-pro">gemini-1.5-pro</option>
          <option value="gemini-1.5-flash">gemini-1.5-flash</option>
          <option value="gemma-3-12b">gemma-3-12b</option>
        </select>
      </div>

      <hr />

      <h3>📖 About</h3>
      <div className="about-content">
        <p>This agent generates comprehensive course content including:</p>
        <ul>
          <li>Course outline and structure</li>
          <li>Detailed modules and lessons</li>
          <li>Learning objectives</li>
          <li>Activities and assessments</li>
          <li>Key takeaways</li>
        </ul>
        <p>Simply enter a course topic and customize the parameters to get started!</p>
      </div>

      <div className="quick-tips">
        <h3>💡 Quick Tips</h3>
        <ul>
          <li>Be specific with course topics</li>
          <li>Adjust duration based on content depth</li>
          <li>Match difficulty to audience</li>
          <li>Review and customize generated content</li>
        </ul>
      </div>
    </aside>
  )
}

export default Sidebar
