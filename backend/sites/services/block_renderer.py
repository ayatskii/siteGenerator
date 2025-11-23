from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import markdown

class BlockRenderer:
    """
    Renders blocks into HTML for preview and final site generation.
    """

    @staticmethod
    def render_block(block_data):
        """
        Dispatches rendering to the appropriate method based on block type.
        block_data can be a Block model instance or a dictionary.
        """
        # Normalize data
        if hasattr(block_data, 'type'):
            block_type = block_data.type
            content = block_data.content
        else:
            block_type = block_data.get('type')
            content = block_data.get('content', {})

        method_name = f"render_{block_type}"
        renderer = getattr(BlockRenderer, method_name, BlockRenderer.render_unknown)
        return renderer(content)

    @staticmethod
    def render_hero(content):
        """
        Renders a Hero block.
        """
        # In a real scenario, we might use Django templates for these chunks too
        # to allow for easier styling overrides. For now, we'll construct HTML or use a simple template string.
        # Let's assume we have some base templates or we build simple HTML.
        
        # For simplicity and flexibility, let's return a structured HTML string.
        # Ideally, these should use the site's template system (e.g. Jinja2 or Django Templates)
        # but since we are generating static HTML, we can just return the HTML string.
        
        headline = content.get('headline', '')
        subheading = content.get('subheading', '')
        image_url = content.get('image_url', '')
        cta_buttons = content.get('cta_buttons', [])
        
        buttons_html = ""
        for btn in cta_buttons:
            text = btn.get('text', 'Click Here')
            link = btn.get('link', '#')
            # Simple button styling
            buttons_html += f'<a href="{link}" class="btn">{text}</a>'

        html = f"""
        <section class="block-hero" style="background-image: url('{image_url}');">
            <div class="container">
                <h1>{headline}</h1>
                <p>{subheading}</p>
                <div class="cta-group">
                    {buttons_html}
                </div>
            </div>
        </section>
        """
        return mark_safe(html)

    @staticmethod
    def render_article(content):
        """
        Renders an Article block.
        """
        html_content = content.get('html_content', '')
        markdown_content = content.get('markdown_content', '')
        use_article_tag = content.get('use_article_tag', False)

        final_content = html_content
        if not final_content and markdown_content:
            final_content = markdown.markdown(markdown_content)

        if use_article_tag:
            return mark_safe(f"<article>{final_content}</article>")
        return mark_safe(f"<div class='block-article'>{final_content}</div>")

    @staticmethod
    def render_image(content):
        """
        Renders an Image block.
        """
        image_url = content.get('image_url', '')
        alt_text = content.get('alt_text', '')
        title = content.get('title_attribute', '')
        width = content.get('width', 'auto')
        height = content.get('height', 'auto')
        
        # Basic lazy loading
        html = f"""
        <div class="block-image">
            <img src="{image_url}" alt="{alt_text}" title="{title}" width="{width}" height="{height}" loading="lazy">
        </div>
        """
        return mark_safe(html)

    @staticmethod
    def render_text_image(content):
        """
        Renders a Text + Image block.
        """
        text = content.get('text', '')
        image_url = content.get('image_url', '')
        position = content.get('position', 'left')
        alt_text = content.get('alt_text', '')
        
        # Simple flex layout
        flex_direction = 'row' if position == 'left' else 'row-reverse'
        
        html = f"""
        <div class="block-text-image" style="display: flex; flex-direction: {flex_direction}; gap: 20px; align-items: center;">
            <div class="image-wrapper" style="flex: 1;">
                <img src="{image_url}" alt="{alt_text}" style="max-width: 100%; height: auto;">
            </div>
            <div class="text-wrapper" style="flex: 1;">
                {text}
            </div>
        </div>
        """
        return mark_safe(html)

    @staticmethod
    def render_cta(content):
        """
        Renders a Call to Action block.
        """
        buttons = content.get('buttons', [])
        layout = content.get('layout', 'horizontal')
        
        buttons_html = ""
        for btn in buttons:
            text = btn.get('text', 'Click Here')
            link = btn.get('link', '#')
            buttons_html += f'<a href="{link}" class="btn">{text}</a>'
            
        flex_direction = 'row' if layout == 'horizontal' else 'column'
        
        html = f"""
        <div class="block-cta" style="display: flex; flex-direction: {flex_direction}; gap: 10px; justify-content: center;">
            {buttons_html}
        </div>
        """
        return mark_safe(html)

    @staticmethod
    def render_faq(content):
        """
        Renders an FAQ block.
        """
        items = content.get('items', [])
        title = content.get('title', '')
        
        items_html = ""
        for item in items:
            question = item.get('question', '')
            answer = item.get('answer', '')
            items_html += f"""
            <details>
                <summary>{question}</summary>
                <div class="answer">{answer}</div>
            </details>
            """
            
        html = f"""
        <div class="block-faq">
            {f'<h2>{title}</h2>' if title else ''}
            {items_html}
        </div>
        """
        return mark_safe(html)

    @staticmethod
    def render_swiper(content):
        """
        Renders a Swiper/Slider block.
        """
        items = content.get('items', [])
        # In a real implementation, we'd include the Swiper.js structure here
        
        slides_html = ""
        for item in items:
            image_url = item.get('image_url', '')
            title = item.get('title', '')
            cta_text = item.get('cta_text', '')
            cta_link = item.get('cta_link', '#')
            
            slides_html += f"""
            <div class="swiper-slide">
                <img src="{image_url}" alt="{title}">
                <div class="slide-content">
                    <h3>{title}</h3>
                    {f'<a href="{cta_link}" class="btn">{cta_text}</a>' if cta_text else ''}
                </div>
            </div>
            """
            
        html = f"""
        <div class="swiper block-swiper">
            <div class="swiper-wrapper">
                {slides_html}
            </div>
            <div class="swiper-pagination"></div>
            <div class="swiper-button-prev"></div>
            <div class="swiper-button-next"></div>
        </div>
        """
        return mark_safe(html)

    @staticmethod
    def render_custom(content):
        """
        Renders Custom HTML block.
        """
        return mark_safe(content.get('html', ''))

    @staticmethod
    def render_unknown(content):
        return mark_safe("<!-- Unknown Block Type -->")
