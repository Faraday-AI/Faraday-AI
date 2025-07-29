"""Template management for notifications and other content."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import jinja2
from app.core.notifications import NotificationTemplate

# Create template manager instance
template_manager = NotificationTemplate()

logger = logging.getLogger(__name__)

class TemplateManager:
    """Template manager for rendering various content types."""
    
    def __init__(self):
        self.logger = logging.getLogger("template_manager")
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("app/templates"),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def render(self, template_name: str, data: Dict[str, Any], format_type: str = 'html') -> str:
        """Render a template with the given data."""
        try:
            template_file = f"{template_name}.{format_type}.j2"
            template = self.env.get_template(template_file)
            return template.render(**data)
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {str(e)}")
            # Return fallback content
            return self._get_fallback_content(template_name, data, format_type)
    
    def _get_fallback_content(self, template_name: str, data: Dict[str, Any], format_type: str) -> str:
        """Get fallback content when template rendering fails."""
        if template_name == 'alert':
            if format_type == 'plain':
                return f"Alert: {data.get('title', 'Unknown Alert')}\n{data.get('message', 'No message provided')}"
            elif format_type == 'html':
                return f"<h2>Alert: {data.get('title', 'Unknown Alert')}</h2><p>{data.get('message', 'No message provided')}</p>"
            elif format_type == 'slack':
                return f"*Alert: {data.get('title', 'Unknown Alert')}*\n{data.get('message', 'No message provided')}"
        elif template_name == 'digest':
            if format_type == 'plain':
                return f"Digest: {data.get('title', 'Daily Digest')}\n{data.get('summary', 'No summary provided')}"
            elif format_type == 'html':
                return f"<h2>Digest: {data.get('title', 'Daily Digest')}</h2><p>{data.get('summary', 'No summary provided')}</p>"
        
        return f"Template {template_name} not available in {format_type} format"
    
    def get_available_templates(self) -> Dict[str, list]:
        """Get list of available templates."""
        try:
            template_dir = Path("app/templates")
            if not template_dir.exists():
                return {}
            
            templates = {}
            for template_file in template_dir.rglob("*.j2"):
                relative_path = template_file.relative_to(template_dir)
                template_name = relative_path.stem
                format_type = relative_path.suffixes[-2] if len(relative_path.suffixes) > 1 else 'html'
                
                if template_name not in templates:
                    templates[template_name] = []
                templates[template_name].append(format_type)
            
            return templates
        except Exception as e:
            self.logger.error(f"Error getting available templates: {str(e)}")
            return {}
    
    def validate_template(self, template_name: str, format_type: str = 'html') -> bool:
        """Validate if a template exists."""
        try:
            template_file = f"{template_name}.{format_type}.j2"
            template = self.env.get_template(template_file)
            return True
        except Exception:
            return False 