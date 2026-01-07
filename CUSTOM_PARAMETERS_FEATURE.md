# Custom Learning Outcomes & Detailed Topics Feature

## Overview
This document describes the enhancement that allows users to input custom learning outcomes and detailed topic specifications for course generation.

## Feature Description
Users can now provide:
1. **Custom Learning Outcomes**: Specific learning objectives they want the course to achieve
2. **Detailed Topics**: A detailed description of specific topics or subtopics to cover in the course

These custom parameters are parsed and used by both the Course Content Agent and Roadmap Agent to generate more tailored and relevant course content.

## User Interface Changes

### Streamlit UI (app.py)
Added an "Advanced Options" expander section with two text areas:

1. **Learning Outcomes** text area:
   - Users can enter one learning outcome per line
   - Example format:
     ```
     Understand the fundamentals of machine learning
     Build and train neural networks
     Deploy ML models to production
     ```

2. **Detailed Topics** text area:
   - Users can enter a detailed description of topics to cover
   - Example:
     ```
     Focus on supervised learning, including linear regression,
     logistic regression, decision trees, and ensemble methods.
     Include practical examples using scikit-learn.
     ```

### Data Flow
1. User inputs custom parameters in UI
2. Parameters are parsed in `extract_course_parameters()`:
   - Learning outcomes: Split by newlines and cleaned
   - Detailed topics: Used as-is (string)
3. Parameters stored in session state
4. Passed to agents during course generation

## Backend Changes

### 1. Course Content Agent (agent/course_agent_langchain.py)

#### New Method: `generate_course_outline_with_details()`
- Accepts custom learning outcomes and detailed topics
- Incorporates them into the prompt for better course outline generation
- Builds detailed topic specification string
- Adds required learning outcomes to prompt

#### Updated Method: `generate_complete_course()`
- New parameters:
  - `custom_learning_outcomes: Optional[List[str]] = None`
  - `detailed_topics: Optional[str] = None`
- Calls `generate_course_outline_with_details()` instead of `generate_course_outline()`
- Uses custom learning outcomes if provided, otherwise uses generated ones
- Passes custom parameters to module content generation

### 2. Roadmap Agent (agent/roadmap_agent.py)

#### Updated Method: `generate_roadmap_from_modules()`
- New parameters:
  - `custom_learning_outcomes: Optional[List[str]] = None`
  - `detailed_topics: Optional[str] = None`
- Adds custom parameters to roadmap generation prompt
- Includes learning outcomes and detailed topics in course context

### 3. Streamlit App (app.py)

#### Updated Function: `extract_course_parameters()`
- Now accepts:
  - `learning_outcomes: Optional[List[str]] = None`
  - `detailed_topics: Optional[str] = None`
- Includes custom parameters in returned dictionary

#### Updated UI Section: Parameter Validation
- Displays count of custom learning outcomes if provided
- Shows preview of detailed topics if provided

#### Updated Course Generation
- Passes custom parameters to `generate_complete_course()`
- Passes custom parameters to `generate_roadmap_from_modules()`

## Technical Implementation Details

### Prompt Engineering
Both agents incorporate custom parameters into their prompts:

**Course Content Agent:**
```python
topic_details = f"{topic}. Specifically cover: {detailed_topics}"
outcomes_spec = "\n\nREQUIRED LEARNING OUTCOMES (must include these):\n" + 
                "\n".join([f"- {outcome}" for outcome in custom_learning_outcomes])
```

**Roadmap Agent:**
```python
outcomes_info = "\n\nLearning Outcomes to Achieve:\n" + 
                "\n".join([f"- {outcome}" for outcome in custom_learning_outcomes])
topics_info = f"\n\nDetailed Topics to Cover:\n{detailed_topics}"
```

### Data Validation
- Learning outcomes are stripped of whitespace and empty lines are filtered
- Detailed topics accept any string input
- Both parameters are optional (None by default)

## Usage Example

### Input
**Topic:** Machine Learning  
**Difficulty:** Intermediate  
**Duration:** 6 weeks  

**Custom Learning Outcomes:**
```
Master supervised learning algorithms
Implement neural networks from scratch
Evaluate model performance using metrics
Deploy ML models using Flask
```

**Detailed Topics:**
```
Cover linear regression, logistic regression, decision trees,
random forests, and neural networks. Include practical
implementations using Python, NumPy, and scikit-learn.
Focus on real-world applications.
```

### Result
The agents will generate:
- Course content that covers all specified topics
- Learning outcomes that include the custom objectives
- Roadmap that paces the learning to achieve stated outcomes
- Modules organized around the detailed topic structure

## Benefits
1. **Personalization**: Users can tailor courses to specific needs
2. **Precision**: More control over what the course covers
3. **Relevance**: Course content aligns better with user goals
4. **Flexibility**: Optional parameters don't affect basic usage

## Files Modified
1. `agent/course_agent_langchain.py` - Added custom parameter support
2. `agent/roadmap_agent.py` - Added custom parameter support  
3. `app.py` - Updated UI and parameter extraction

## Testing Recommendations
1. Test with no custom parameters (backward compatibility)
2. Test with only learning outcomes
3. Test with only detailed topics
4. Test with both parameters
5. Verify parsing of multi-line learning outcomes
6. Check prompt generation includes custom parameters
7. Validate generated course content matches specifications

## Future Enhancements
- Add validation for learning outcomes format
- Support importing outcomes from file
- Allow outcomes to be edited after initial input
- Add templates for common learning outcome types
- Support multiple topic specification formats
