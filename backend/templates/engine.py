import re
from .models import TemplateVariable

def substitute_variables(content, context):
    """
    Substitute variables in the content with values from the context.
    
    Args:
        content (str): The HTML content containing variables like {{VAR_NAME}}.
        context (dict): A dictionary of values to substitute.
    
    Returns:
        str: The content with variables replaced.
    """
    if not content:
        return ""

    # 1. Apply context variables
    for key, value in context.items():
        pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
        content = re.sub(pattern, str(value), content)

    # 2. Apply database-defined default variables if not in context
    # This is useful for global defaults if we implement them later
    # db_vars = TemplateVariable.objects.all()
    # for var in db_vars:
    #     if var.name not in context:
    #         pattern = r'\{\{\s*' + re.escape(var.name) + r'\s*\}\}'
    #         content = re.sub(pattern, var.default_value, content)

    return content

def render_template(template, context):
    """
    Render a template (Monolithic or Sectional) with the given context.
    """
    if template.type == 'MONOLITHIC':
        return substitute_variables(template.content, context)
    
    elif template.type == 'SECTIONAL':
        # Combine sections in order
        sections = template.sections.all().order_by('order')
        full_content = ""
        for section in sections:
            full_content += section.content + "\n"
        
        return substitute_variables(full_content, context)
    
    return ""
