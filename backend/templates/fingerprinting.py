import re
import random
import hashlib
from typing import Dict, List

class CSSRandomizer:
    """
    Handles deterministic randomization of CSS class names.
    """
    def __init__(self, seed: str):
        self.seed = seed
        self.rng = random.Random(seed)
        self.class_map = {}

    def generate_class_map(self, css_content: str) -> Dict[str, str]:
        """
        Parses CSS content to find class names and generates a random mapping.
        """
        # Regex to find class definitions like .classname { or .classname,
        # This is a simplified regex and might need refinement for complex CSS
        class_pattern = r'\.([a-zA-Z0-9_-]+)(?=\s*[\{,])'
        matches = set(re.findall(class_pattern, css_content))
        
        for class_name in matches:
            if class_name not in self.class_map:
                self.class_map[class_name] = self._generate_random_name()
        
        return self.class_map

    def _generate_random_name(self) -> str:
        """
        Generates a random class name like _1jhy4_gtw2n.
        """
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        part1 = ''.join(self.rng.choices(chars, k=5))
        part2 = ''.join(self.rng.choices(chars, k=5))
        return f"_{part1}_{part2}"

    def apply_class_map(self, content: str, is_css: bool = False) -> str:
        """
        Replaces class names in content (HTML or CSS) using the generated map.
        """
        if not self.class_map:
            return content

        # Sort by length descending to avoid partial replacements (e.g. replacing 'btn' inside 'btn-primary')
        sorted_classes = sorted(self.class_map.keys(), key=len, reverse=True)
        
        for class_name in sorted_classes:
            new_name = self.class_map[class_name]
            
            if is_css:
                # In CSS, replace .classname
                pattern = r'\.' + re.escape(class_name) + r'(?![a-zA-Z0-9_-])'
                content = re.sub(pattern, '.' + new_name, content)
            else:
                # In HTML, replace class="... classname ..."
                # This is tricky with regex. A safer approach is to replace specific known patterns
                # or use a proper HTML parser. For now, we'll use a robust regex approach.
                
                # Strategy: Find all class="..." or class='...' attributes
                def replace_in_match(match):
                    quote = match.group(1)
                    attr_content = match.group(2)
                    tokens = attr_content.split()
                    new_tokens = [self.class_map.get(t, t) for t in tokens]
                    return f'class={quote}{" ".join(new_tokens)}{quote}'

                content = re.sub(r'class=([\'"])([^\'"]*)[\'"]', replace_in_match, content)
                
        return content


class FootprintManager:
    """
    Manages CMS-specific file structure footprints.
    """
    FOOTPRINTS = {
        'WORDPRESS': 'wp-content/themes/{theme}/assets/',
        'JOOMLA': 'templates/{template}/',
        'CUSTOM': 'assets/'
    }

    def __init__(self, footprint_type: str = 'CUSTOM', theme_name: str = 'default'):
        self.footprint_type = footprint_type.upper()
        self.theme_name = theme_name
        self.base_path = self._get_base_path()

    def _get_base_path(self) -> str:
        pattern = self.FOOTPRINTS.get(self.footprint_type, self.FOOTPRINTS['CUSTOM'])
        return pattern.format(theme=self.theme_name, template=self.theme_name)

    def remap_paths(self, content: str) -> str:
        """
        Remaps generic /assets/ paths to the CMS-specific path.
        """
        # Assuming the template uses a standard placeholder like /assets/ or just assets/
        # We'll replace 'assets/' with the new base path
        
        # This regex looks for src="assets/..." or href="assets/..."
        # It captures the quote to ensure we only replace inside attributes
        
        def replace_path(match):
            quote = match.group(1) # " or '
            rest = match.group(2)  # filename.ext
            return f'src={quote}{self.base_path}{rest}{quote}' if 'src' in match.group(0) else f'href={quote}{self.base_path}{rest}{quote}'

        # Improved pattern to handle both single and double quotes
        # Matches src="assets/..." or src='assets/...'
        pattern = r'(?:src|href)=([\'"])assets/([^\'"]+)\1'
        
        def replace_match(match):
            # Reconstruct the attribute with the new path
            # match.group(0) is the full string e.g. src="assets/file.jpg"
            full_match = match.group(0)
            attr_name = "src" if "src=" in full_match else "href"
            quote = match.group(1)
            path_suffix = match.group(2)
            return f'{attr_name}={quote}{self.base_path}{path_suffix}{quote}'

        content = re.sub(pattern, replace_match, content)
        
        return content
