import markdown

class MarkdownService:
    @staticmethod
    def convert_to_html(markdown_text):
        """
        Convert markdown text to HTML using common extensions.
        """
        if not markdown_text:
            return ""
            
        # Use extra extensions for tables, code highlighting, etc.
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
        ]
        
        return markdown.markdown(markdown_text, extensions=extensions)
