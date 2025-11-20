import re
import json
from typing import Dict, Any, List

class VariableContext:
    """
    Aggregates all context data required for variable substitution.
    """
    def __init__(self, site_data: Dict[str, Any], page_data: Dict[str, Any], global_settings: Dict[str, Any] = None):
        self.site = site_data
        self.page = page_data
        self.global_settings = global_settings or {}
        self.variables = self._build_variables()

    def _build_variables(self) -> Dict[str, Any]:
        """
        Constructs the master dictionary of all available variables.
        """
        vars = {}
        
        # 1. Site Level
        vars['SITE_BRAND'] = self.site.get('brand_name', '')
        vars['SITE_DOMAIN'] = self.site.get('domain', '')
        vars['SITE_LANGUAGE'] = self.site.get('language', 'en')
        vars['LOGO_URL'] = self.site.get('logo_url', '')
        vars['FAVICON_LINKS'] = self.site.get('favicon_links', '') # Pre-rendered HTML
        
        # 2. Page Level
        vars['PAGE_TITLE'] = self.page.get('title', '')
        vars['PAGE_DESCRIPTION'] = self.page.get('description', '')
        vars['PAGE_H1'] = self.page.get('h1', '')
        vars['PAGE_CANONICAL'] = self.page.get('canonical_url', '')
        vars['METADATA'] = self.page.get('metadata', '') # Pre-rendered meta tags
        vars['MICRODATA'] = self.page.get('microdata', '') # JSON-LD
        
        # 3. Content & Assets
        vars['CONTENT'] = self.page.get('content_html', '')
        vars['STYLES_INLINE'] = self.page.get('styles_inline', '')
        vars['SCRIPTS_INLINE'] = self.page.get('scripts_inline', '')
        
        # 4. Navigation & Footer
        vars['HEADER_MENU'] = self.page.get('header_menu_html', '')
        vars['FOOTER_MENU'] = self.page.get('footer_menu_html', '')
        vars['FOOTER_IMAGES'] = self.page.get('footer_images_html', '')
        
        # 5. Affiliate
        # Site level overrides global
        vars['AFFILIATE_LINK'] = self.site.get('affiliate_link') or self.global_settings.get('default_affiliate_link', '#')

        return vars

    def get(self, key: str, default: Any = '') -> Any:
        return self.variables.get(key, default)


def substitute_variables(content: str, context: VariableContext) -> str:
    """
    Substitute variables in the content with values from the context.
    Supports standard {{VAR}} syntax.
    """
    if not content:
        return ""

    # Iterate through all known variables in the context
    # This is safer than regex-finding all {{...}} which might match JS code
    for key, value in context.variables.items():
        pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
        
        # Handle different value types
        if value is None:
            replacement = ""
        elif isinstance(value, (dict, list)):
            replacement = json.dumps(value)
        else:
            replacement = str(value)
            
        content = re.sub(pattern, replacement, content)

    return content

def render_template(template, context: VariableContext) -> str:
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

