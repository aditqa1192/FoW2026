"""
Export utilities for course content
"""

import os
import json
from typing import Dict
from datetime import datetime


def ensure_export_dir(export_dir: str = "exports") -> str:
    """
    Ensure export directory exists
    
    Args:
        export_dir: Directory path for exports
        
    Returns:
        Absolute path to export directory
    """
    if not os.path.isabs(export_dir):
        export_dir = os.path.join(os.getcwd(), export_dir)
    
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def export_json(course_dict: Dict, filename: str = None, export_dir: str = "exports") -> str:
    """
    Export course content to JSON file
    
    Args:
        course_dict: Course content dictionary
        filename: Output filename (auto-generated if None)
        export_dir: Directory for exports
        
    Returns:
        Path to exported file
    """
    export_path = ensure_export_dir(export_dir)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"course_{timestamp}.json"
    
    filepath = os.path.join(export_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(course_dict, f, indent=2, ensure_ascii=False)
    
    return filepath


def export_markdown(course_dict: Dict, markdown_content: str, 
                   filename: str = None, export_dir: str = "exports") -> str:
    """
    Export course content to Markdown file
    
    Args:
        course_dict: Course content dictionary
        markdown_content: Markdown formatted content
        filename: Output filename (auto-generated if None)
        export_dir: Directory for exports
        
    Returns:
        Path to exported file
    """
    export_path = ensure_export_dir(export_dir)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"course_{timestamp}.md"
    
    filepath = os.path.join(export_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return filepath


def export_html(course_dict: Dict, html_content: str, 
                filename: str = None, export_dir: str = "exports") -> str:
    """
    Export course content to HTML file
    
    Args:
        course_dict: Course content dictionary
        html_content: HTML formatted content
        filename: Output filename (auto-generated if None)
        export_dir: Directory for exports
        
    Returns:
        Path to exported file
    """
    export_path = ensure_export_dir(export_dir)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"course_{timestamp}.html"
    
    filepath = os.path.join(export_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath


def export_all_formats(course_dict: Dict, markdown_content: str, html_content: str,
                      base_filename: str = None, export_dir: str = "exports") -> Dict[str, str]:
    """
    Export course content in all available formats
    
    Args:
        course_dict: Course content dictionary
        markdown_content: Markdown formatted content
        html_content: HTML formatted content
        base_filename: Base filename (without extension)
        export_dir: Directory for exports
        
    Returns:
        Dictionary mapping format names to file paths
    """
    if base_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"course_{timestamp}"
    
    exports = {
        "json": export_json(course_dict, f"{base_filename}.json", export_dir),
        "markdown": export_markdown(course_dict, markdown_content, 
                                   f"{base_filename}.md", export_dir),
        "html": export_html(course_dict, html_content, 
                          f"{base_filename}.html", export_dir)
    }
    
    return exports
