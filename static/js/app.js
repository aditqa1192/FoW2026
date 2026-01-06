// Global state
let courseData = null;
let roadmapData = null;

// DOM Elements
const coursePrompt = document.getElementById('coursePrompt');
const validateBtn = document.getElementById('validateBtn');
const generateBtn = document.getElementById('generateBtn');
const clearBtn = document.getElementById('clearBtn');
const validationResult = document.getElementById('validationResult');
const loadingIndicator = document.getElementById('loadingIndicator');
const statusIndicator = document.getElementById('statusIndicator');
const courseContent = document.getElementById('courseContent');
const roadmapContent = document.getElementById('roadmapContent');

// Event Listeners
validateBtn.addEventListener('click', validateRequirements);
generateBtn.addEventListener('click', generateCourse);
clearBtn.addEventListener('click', clearAll);

// Validate Requirements
async function validateRequirements() {
    const prompt = coursePrompt.value.trim();
    
    if (!prompt) {
        showValidationError('Please enter course requirements');
        return;
    }

    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();

        if (data.success) {
            if (data.is_valid) {
                showValidationSuccess(data.params);
            } else {
                showValidationError(`Missing required information: ${data.missing.join(', ')}`);
            }
        } else {
            showValidationError(data.error);
        }
    } catch (error) {
        console.error('Validation error:', error);
        showValidationError('Error validating requirements. Please try again.');
    }
}

// Generate Course
async function generateCourse() {
    const prompt = coursePrompt.value.trim();
    
    if (!prompt) {
        showError('Please enter course requirements');
        return;
    }

    // Show loading
    loadingIndicator.style.display = 'block';
    generateBtn.disabled = true;
    courseContent.style.display = 'none';
    roadmapContent.style.display = 'none';

    try {
        const response = await fetch('/api/generate-course', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();

        if (data.success) {
            courseData = data.course;
            displayCourse(courseData);
            showStatus('✅ Course content generated successfully!', 'success');
        } else {
            showError(data.error);
        }
    } catch (error) {
        console.error('Generation error:', error);
        showError('Error generating course. Please try again.');
    } finally {
        loadingIndicator.style.display = 'none';
        generateBtn.disabled = false;
    }
}

// Generate Roadmap
async function generateRoadmap() {
    if (!courseData) {
        showError('Please generate course content first');
        return;
    }

    // Show loading
    showStatus('🗺️ Generating course roadmap...', 'info');

    try {
        const response = await fetch('/api/generate-roadmap', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            roadmapData = data.roadmap;
            displayRoadmap(roadmapData, data.summary_table);
            showStatus('✨ Roadmap generated successfully!', 'success');
        } else {
            showError(data.error);
        }
    } catch (error) {
        console.error('Roadmap generation error:', error);
        showError('Error generating roadmap. Please try again.');
    }
}

// Display Course Content
function displayCourse(course) {
    // Show course content section
    courseContent.style.display = 'block';
    
    // Display summary
    const summary = formatCourseSummary(course);
    document.getElementById('courseSummary').textContent = summary;
    
    // Display overview
    displayCourseOverview(course);
    
    // Display modules
    displayModules(course.modules);
    
    // Scroll to content
    courseContent.scrollIntoView({ behavior: 'smooth' });
}

// Format Course Summary
function formatCourseSummary(course) {
    return `Course: ${course.title}
Target Audience: ${course.target_audience}
Difficulty: ${course.difficulty_level.charAt(0).toUpperCase() + course.difficulty_level.slice(1)}
Duration: ${course.duration_weeks} weeks
Modules: ${course.modules.length}
Total Lessons: ${course.modules.reduce((sum, m) => sum + m.lessons.length, 0)}`;
}

// Display Course Overview
function displayCourseOverview(course) {
    const overviewHtml = `
        <h4>${course.title}</h4>
        <p>${course.description}</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
            <div>
                <strong>Target Audience:</strong>
                <p>${course.target_audience}</p>
                
                <strong>Difficulty:</strong>
                <p>${course.difficulty_level.charAt(0).toUpperCase() + course.difficulty_level.slice(1)}</p>
                
                <strong>Duration:</strong>
                <p>${course.duration_weeks} weeks</p>
            </div>
            
            <div>
                <strong>Prerequisites:</strong>
                <ul>
                    ${course.prerequisites.map(p => `<li>${p}</li>`).join('')}
                </ul>
                
                <strong>Learning Outcomes:</strong>
                <ul>
                    ${course.learning_outcomes.slice(0, 3).map(o => `<li>${o}</li>`).join('')}
                    ${course.learning_outcomes.length > 3 ? `<li>...and ${course.learning_outcomes.length - 3} more</li>` : ''}
                </ul>
            </div>
        </div>
    `;
    
    document.getElementById('courseOverview').innerHTML = overviewHtml;
}

// Display Modules
function displayModules(modules) {
    const modulesHtml = modules.map((module, moduleIdx) => `
        <div class="expandable-section">
            <div class="section-header" onclick="toggleSection('module${moduleIdx}')">
                <h3>📦 Module ${moduleIdx + 1}: ${module.title}</h3>
                <i class="fas fa-chevron-down"></i>
            </div>
            <div id="module${moduleIdx}" class="section-content">
                <p><strong>Description:</strong> ${module.description}</p>
                <p><strong>Duration:</strong> ${module.duration_hours} hours</p>
                
                ${module.lessons.map((lesson, lessonIdx) => `
                    <div class="lesson-card">
                        <div class="lesson-header">
                            Lesson ${moduleIdx + 1}.${lessonIdx + 1}: ${lesson.title}
                        </div>
                        <div class="lesson-duration">⏱️ Duration: ${lesson.duration_minutes} minutes</div>
                        
                        <div class="lesson-section">
                            <h4>🎯 Learning Objectives:</h4>
                            <ul class="objectives-list">
                                ${lesson.learning_objectives.map(obj => `<li>${obj}</li>`).join('')}
                            </ul>
                        </div>
                        
                        <div class="lesson-section">
                            <h4>📖 Content:</h4>
                            <p>${lesson.content}</p>
                        </div>
                        
                        <div class="lesson-section">
                            <h4>🔑 Key Points:</h4>
                            <div class="key-points-grid">
                                ${lesson.key_points.map(point => `<div>• ${point}</div>`).join('')}
                            </div>
                        </div>
                        
                        <div class="lesson-section">
                            <h4>✏️ Activities:</h4>
                            <ol class="activity-list">
                                ${lesson.activities.map(activity => `<li>${activity}</li>`).join('')}
                            </ol>
                        </div>
                        
                        <div class="lesson-section">
                            <h4>📝 Assessment:</h4>
                            ${lesson.assessment_questions.map((q, qIdx) => `
                                <div class="assessment-question">
                                    <strong>Q${qIdx + 1}:</strong> ${q.question || 'N/A'}
                                    <button class="btn btn-secondary" style="margin-top: 8px; padding: 6px 12px; font-size: 0.85rem;" onclick="toggleAnswer('answer${moduleIdx}_${lessonIdx}_${qIdx}')">
                                        Show Answer
                                    </button>
                                    <div id="answer${moduleIdx}_${lessonIdx}_${qIdx}" class="assessment-answer">
                                        ${q.answer || 'N/A'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
    
    document.getElementById('modulesContainer').innerHTML = modulesHtml;
}

// Display Roadmap
function displayRoadmap(roadmap, summaryTable) {
    roadmapContent.style.display = 'block';
    
    // Display summary table
    document.getElementById('roadmapTable').innerHTML = summaryTable;
    
    // Display roadmap details
    displayRoadmapDetails(roadmap);
    
    // Scroll to roadmap
    roadmapContent.scrollIntoView({ behavior: 'smooth' });
}

// Display Roadmap Details
function displayRoadmapDetails(roadmap) {
    const detailsHtml = `
        <div class="expandable-section">
            <div class="section-header" onclick="toggleSection('roadmapOverview')">
                <h3>📊 Roadmap Overview</h3>
                <i class="fas fa-chevron-down"></i>
            </div>
            <div id="roadmapOverview" class="section-content">
                <div class="roadmap-overview">
                    <div class="metric-card">
                        <div class="metric-value">${roadmap.total_duration_weeks}</div>
                        <div class="metric-label">Weeks</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${roadmap.total_estimated_hours}</div>
                        <div class="metric-label">Total Hours</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${roadmap.total_modules}</div>
                        <div class="metric-label">Modules</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${roadmap.milestones.length}</div>
                        <div class="metric-label">Milestones</div>
                    </div>
                </div>
                
                ${roadmap.start_date && roadmap.end_date ? `
                    <div class="info-box" style="margin-top: 20px;">
                        📅 <strong>Timeline:</strong> ${roadmap.start_date} to ${roadmap.end_date}
                    </div>
                ` : ''}
                
                ${roadmap.pacing_recommendations ? `
                    <div style="margin-top: 20px;">
                        <strong>💡 Pacing Recommendations:</strong>
                        <p>${roadmap.pacing_recommendations}</p>
                    </div>
                ` : ''}
            </div>
        </div>
        
        <div class="expandable-section">
            <div class="section-header" onclick="toggleSection('weeklySchedule')">
                <h3>📅 Weekly Schedule Details</h3>
                <i class="fas fa-chevron-down"></i>
            </div>
            <div id="weeklySchedule" class="section-content">
                ${roadmap.weekly_schedule.map(week => `
                    <div class="week-card">
                        <h4>${week.week_title}</h4>
                        
                        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 15px;">
                            <div>
                                ${week.topics && week.topics.length > 0 ? `
                                    <strong>Topics:</strong>
                                    <ul>
                                        ${week.topics.map(topic => `<li>${topic}</li>`).join('')}
                                    </ul>
                                ` : ''}
                                
                                ${week.modules_covered && week.modules_covered.length > 0 ? `
                                    <strong>Modules:</strong>
                                    <ul>
                                        ${week.modules_covered.map(module => `<li>📦 ${module}</li>`).join('')}
                                    </ul>
                                ` : ''}
                            </div>
                            
                            <div>
                                <div class="metric-card">
                                    <div class="metric-value">${week.estimated_hours}</div>
                                    <div class="metric-label">Hours</div>
                                </div>
                                
                                ${week.deliverables && week.deliverables.length > 0 ? `
                                    <div style="margin-top: 15px;">
                                        <strong>📝 Due:</strong>
                                        <ul>
                                            ${week.deliverables.map(d => `<li>${d}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        
                        ${week.milestones && week.milestones.length > 0 ? `
                            <div class="milestone-badge">
                                🎯 Milestone: ${week.milestones[0]}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
        
        ${roadmap.milestones && roadmap.milestones.length > 0 ? `
            <div class="expandable-section">
                <div class="section-header" onclick="toggleSection('milestones')">
                    <h3>🎯 Key Milestones</h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div id="milestones" class="section-content">
                    ${roadmap.milestones.map(milestone => {
                        const icons = {quiz: '📝', project: '🚀', assignment: '✍️', checkpoint: '✅'};
                        const icon = icons[milestone.type] || '🎯';
                        return `
                            <div style="margin: 15px 0;">
                                <strong>Week ${milestone.week}: ${icon} ${milestone.title}</strong>
                                <p style="font-style: italic; color: var(--secondary-color);">${milestone.description}</p>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        ` : ''}
        
        ${roadmap.study_tips && roadmap.study_tips.length > 0 ? `
            <div class="expandable-section">
                <div class="section-header" onclick="toggleSection('studyTips')">
                    <h3>💡 Study Tips for Success</h3>
                    <i class="fas fa-chevron-down"></i>
                </div>
                <div id="studyTips" class="section-content">
                    <ol>
                        ${roadmap.study_tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ol>
                </div>
            </div>
        ` : ''}
    `;
    
    document.getElementById('roadmapDetails').innerHTML = detailsHtml;
}

// Export Functions
async function exportCourse(format) {
    if (!courseData) {
        showError('No course content to export');
        return;
    }

    try {
        window.location.href = `/api/export/${format}`;
    } catch (error) {
        console.error('Export error:', error);
        showError('Error exporting course. Please try again.');
    }
}

async function exportRoadmap(format) {
    if (!roadmapData) {
        showError('No roadmap to export');
        return;
    }

    try {
        window.location.href = `/api/export-roadmap/${format}`;
    } catch (error) {
        console.error('Export error:', error);
        showError('Error exporting roadmap. Please try again.');
    }
}

// Clear All
async function clearAll() {
    if (confirm('Are you sure you want to clear all data?')) {
        try {
            await fetch('/api/clear', { method: 'POST' });
            
            courseData = null;
            roadmapData = null;
            coursePrompt.value = '';
            validationResult.style.display = 'none';
            courseContent.style.display = 'none';
            roadmapContent.style.display = 'none';
            statusIndicator.style.display = 'none';
            
            showStatus('Data cleared successfully', 'success');
        } catch (error) {
            console.error('Clear error:', error);
            showError('Error clearing data. Please try again.');
        }
    }
}

// Helper Functions
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.previousElementSibling;
    
    if (section.classList.contains('expanded')) {
        section.classList.remove('expanded');
        header.classList.add('collapsed');
    } else {
        section.classList.add('expanded');
        header.classList.remove('collapsed');
    }
}

function toggleAnswer(answerId) {
    const answer = document.getElementById(answerId);
    answer.classList.toggle('show');
}

function showValidationSuccess(params) {
    validationResult.className = 'validation-result validation-success';
    validationResult.innerHTML = `
        <strong>✅ All required parameters detected!</strong>
        <div style="margin-top: 10px;">
            <strong>Extracted Parameters:</strong>
            <ul style="margin-top: 8px;">
                <li><strong>Topic:</strong> ${params.topic}</li>
                <li><strong>Duration:</strong> ${params.duration_weeks} weeks</li>
                <li><strong>Difficulty:</strong> ${params.difficulty}</li>
                <li><strong>Target Audience:</strong> ${params.target_audience}</li>
                <li><strong>Lessons per Module:</strong> ${params.lessons_per_module}</li>
            </ul>
        </div>
    `;
    validationResult.style.display = 'block';
}

function showValidationError(message) {
    validationResult.className = 'validation-result validation-error';
    validationResult.innerHTML = `<strong>❌ ${message}</strong>`;
    validationResult.style.display = 'block';
}

function showError(message) {
    statusIndicator.className = 'alert alert-error';
    statusIndicator.innerHTML = `❌ ${message}`;
    statusIndicator.style.display = 'block';
    
    setTimeout(() => {
        statusIndicator.style.display = 'none';
    }, 5000);
}

function showStatus(message, type) {
    statusIndicator.className = `alert alert-${type}`;
    statusIndicator.innerHTML = message;
    statusIndicator.style.display = 'block';
    
    setTimeout(() => {
        statusIndicator.style.display = 'none';
    }, 5000);
}
