"""
Natural Language Parameter Extraction
Extract course parameters from user prompts
"""

import re
import logging

logger = logging.getLogger(__name__)


def extract_course_parameters(prompt):
    """
    Extract course parameters from user prompt using enhanced natural language processing.
    Returns a dictionary with extracted parameters and a list of missing required fields.
    """
    params = {
        'topic': None,
        'duration_weeks': None,
        'difficulty': None,
        'target_audience': None,
        'lessons_per_module': None
    }
    
    missing_fields = []
    prompt_lower = prompt.lower()
    
    # Extract topic - refined patterns with better ordering
    topic_patterns = [
        # Pattern 1: "X course/program/training for Y" - capture X before course keyword
        r'(?:create|generate|build|make|design|develop)\s+(?:a\s+)?([^\s]+(?:\s+[^\s]+)*?)\s+(?:course|class|training|program|curriculum)\s+for',
        
        # Pattern 2: "course/program on X" - preposition after course keyword
        r'(?:course|class|training|program|curriculum)\s+(?:on|about|regarding|covering)\s+([^\n,.;]+?)(?:\s+(?:for|over|duration|difficulty|that|which|with|lasting|taking)|[,.\n]|$)',
        
        # Pattern 3: "teach/learn X" - subject after action verb
        r'(?:teach|learn|study|master|understand)\s+(?:about\s+)?([^\n,.;]+?)(?:\s+(?:for|to|over|duration|in|within)|[,.\n]|$)',
        
        # Pattern 4: "create course on X" - with explicit preposition
        r'(?:create|generate|build|make|design|develop)\s+(?:a\s+)?(?:course|class|training|program)\s+(?:on|about|regarding|in)\s+([^\n,.;]+?)(?:\s+(?:for|over|duration)|[,.\n]|$)',
        
        # Pattern 5: Topic label format
        r'topic\s*[:\-]\s*([^\n,.;]+?)(?:\s+(?:for|over|duration)|[,.\n]|$)',
        r'subject\s*[:\-]\s*([^\n,.;]+?)(?:\s+(?:for|over|duration)|[,.\n]|$)',
        
        # Pattern 6: "I want to learn X" - conversational
        r'(?:i\s+)?(?:want|need|would like)\s+(?:to\s+)?(?:learn|study|create|take)\s+(?:a\s+)?(?:course\s+(?:on|in)\s+)?([^\n,.;]+?)(?:\s+(?:for|course|training)|[,.\n]|$)',
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            topic = match.group(1).strip()
            # Clean up common prefixes/suffixes
            topic = re.sub(r'^(?:a|an|the)\s+', '', topic, flags=re.IGNORECASE)
            topic = re.sub(r'\s+(?:course|class|training|program)$', '', topic, flags=re.IGNORECASE)
            # Remove audience-related words that might have been captured
            topic = re.sub(r'\s+(?:for|to|with)\s+.*$', '', topic, flags=re.IGNORECASE)
            if len(topic) > 3:  # Must be meaningful
                params['topic'] = topic
                break
    
    # Extract duration - more flexible
    duration_patterns = [
        r'(\d+)\s*(?:-|to)?\s*weeks?(?:\s+long)?',
        r'(?:duration|lasting|takes?|span(?:ning)?|over|in)\s*[:\-]?\s*(\d+)\s*weeks?',
        r'(?:for|across|throughout)\s+(\d+)\s*weeks?',
        r'(\d+)\s*week\s+(?:course|program|class)',
        r'(?:weekly|week by week)\s+(?:for\s+)?(\d+)\s+weeks?',
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            weeks = int(match.group(1))
            if 1 <= weeks <= 52:  # Sanity check
                params['duration_weeks'] = weeks
                break
    
    # Extract difficulty level - synonyms and variations
    difficulty_mappings = {
        'beginner': ['beginner', 'beginners', 'basic', 'introductory', 'intro', 'fundamental', 'elementary', 'starter', 'novice', 'entry level', 'entry-level', 'starting'],
        'intermediate': ['intermediate', 'mid level', 'mid-level', 'moderate', 'standard', 'regular', 'average'],
        'advanced': ['advanced', 'expert', 'professional', 'senior', 'high level', 'high-level', 'complex', 'sophisticated', 'in-depth', 'in depth', 'deep dive']
    }
    
    for level, keywords in difficulty_mappings.items():
        for keyword in keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                params['difficulty'] = level
                break
        if params['difficulty']:
            break
    
    # Extract target audience - much more comprehensive
    audience_patterns = [
        # Direct patterns
        r'(?:for|aimed at|targeting|designed for|intended for)\s+([^\n,.;]+?)(?:\s+(?:who|that|with|wanting|interested|looking)|[,.\n]|$)',
        r'(?:target|target audience|audience)\s*[:\-]\s*([^\n,.;]+?)(?:[,.\n]|$)',
        # Professional/student indicators
        r'\b((?:college|university|high school|graduate|undergraduate|phd|doctoral|medical|engineering|business|law|nursing)\s+students?)\b',
        r'\b((?:software|web|data|machine learning|ai|cloud|mobile|frontend|backend|full stack|fullstack)\s+(?:developers?|engineers?|programmers?))\b',
        r'\b((?:aspiring|junior|senior|lead|staff|principal)\s+(?:developers?|engineers?|programmers?|professionals?))\b',
        r'\b((?:beginners?|novices?|experts?|professionals?|practitioners?|enthusiasts?|hobbyists?))\b',
        r'\b((?:managers?|leaders?|executives?|analysts?|consultants?|researchers?|scientists?))\b',
    ]
    
    for pattern in audience_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            audience = match.group(1).strip()
            # Clean up
            audience = re.sub(r'^(?:the\s+)?', '', audience)
            if len(audience) > 3:
                params['target_audience'] = audience
                break
    
    # Extract lessons per module
    lessons_patterns = [
        r'(\d+)\s*lessons?\s+(?:per|in\s+each|for\s+each)\s+module',
        r'(?:lessons per module|module lessons)\s*[:\-]?\s*(\d+)',
        r'each\s+module\s+(?:has|contains|includes)\s+(\d+)\s*lessons?',
        r'(\d+)\s*lessons?\s+(?:in|per)\s+(?:each|every)\s+module',
    ]
    
    for pattern in lessons_patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            lessons = int(match.group(1))
            if 1 <= lessons <= 20:  # Sanity check
                params['lessons_per_module'] = lessons
                break
    
    # Set defaults for optional parameters
    if params['duration_weeks'] is None:
        params['duration_weeks'] = 4
        
    if params['difficulty'] is None:
        params['difficulty'] = 'beginner'
        
    if params['target_audience'] is None:
        params['target_audience'] = 'general learners'
        
    if params['lessons_per_module'] is None:
        params['lessons_per_module'] = 4
    
    # Check for required fields
    if not params['topic']:
        missing_fields.append('Course Topic')
    
    return params, missing_fields
