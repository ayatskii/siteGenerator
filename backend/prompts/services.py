import logging
from django.conf import settings
from django.template import Template, Context
from tokens.models import APIToken
from .models import TextPrompt

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        pass

    def get_active_token(self, service_type='openai', ai_model=None):
        """
        Retrieve an active API token for the specified service and model.
        Prioritizes tokens that match the specific model if provided.
        """
        tokens = APIToken.objects.filter(service_type=service_type, is_active=True)
        
        if ai_model:
            # Try to find a token specifically for this model
            model_token = tokens.filter(ai_model=ai_model).first()
            if model_token:
                return model_token
        
        # Fallback to any active token for the service
        return tokens.first()

    def substitute_variables(self, prompt_template, context_data):
        """
        Replace {{variable}} placeholders in the prompt template with values from context_data.
        """
        try:
            # Use Django's template engine for robust substitution
            template = Template(prompt_template)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            logger.error(f"Error substituting variables: {str(e)}")
            # Fallback to basic string replacement if template rendering fails
            result = prompt_template
            for key, value in context_data.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result

    def generate_content(self, prompt_id, context_data, service_type='openai'):
        """
        Generate content using the specified prompt and context.
        """
        try:
            prompt = TextPrompt.objects.get(id=prompt_id)
        except TextPrompt.DoesNotExist:
            return {'success': False, 'error': 'Prompt not found'}

        # Prepare the full prompt
        full_prompt_text = self.substitute_variables(prompt.template, context_data)
        
        # Determine service and model
        # If the prompt specifies a model, try to use it.
        # Map prompt models to token service types if needed.
        target_model = prompt.ai_model
        
        # Simple mapping logic - can be expanded
        if 'grok' in target_model:
            service_type = 'grok'
        elif 'claude' in target_model or '/' in target_model: # OpenRouter often uses /
            service_type = 'openrouter'
        else:
            service_type = 'openai'

        token = self.get_active_token(service_type, target_model)
        
        if not token:
            return {'success': False, 'error': f'No active API token found for service: {service_type}'}

        # Execute request based on service
        if service_type == 'openrouter':
            return self._generate_openrouter(token, full_prompt_text, target_model, prompt.temperature)
        elif service_type == 'grok':
             # Grok often uses OpenAI compatible endpoints or specific ones. 
             # Assuming APIToken has a method or we use OpenRouter for it if it's x-ai/grok
             # For now, let's assume we might use OpenRouter for Grok too if configured that way, 
             # or a specific Grok implementation.
             # Re-using OpenRouter logic if the token supports it, otherwise specific.
             # The APIToken model has _test_grok_connection but no generate method yet.
             # Let's use a generic OpenAI-compatible method for Grok as it's often compatible.
             return self._generate_openai_compatible(token, full_prompt_text, target_model, prompt.temperature, base_url="https://api.x.ai/v1")
        else:
            # Default to OpenAI
            return self._generate_openai(token, full_prompt_text, target_model, prompt.temperature)

    def _generate_openrouter(self, token, prompt_text, model, temperature):
        messages = [{'role': 'user', 'content': prompt_text}]
        response = token.make_openrouter_request(
            messages=messages,
            temperature=temperature,
            model=model
        )
        
        if response['success']:
            try:
                content = response['data']['choices'][0]['message']['content']
                return {'success': True, 'content': content}
            except (KeyError, IndexError):
                return {'success': False, 'error': 'Unexpected response format from OpenRouter'}
        else:
            return response

    def _generate_openai(self, token, prompt_text, model, temperature):
        # Using the APIToken's raw value to make a request
        # We could add a make_openai_request to APIToken, but for now implementing here
        import requests
        
        headers = {
            'Authorization': f'Bearer {token.token_value}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt_text}],
            'temperature': temperature,
        }
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # token.increment_usage() # Helper method might not exist
                # APIToken model has current_usage field but maybe not a method? 
                # Checking APIToken code... it has increment_usage call in make_openrouter_request but I didn't see the definition.
                # I will manually update for now to be safe.
                token.current_usage += 1
                token.save(update_fields=['current_usage', 'last_used_at'])
                
                content = data['choices'][0]['message']['content']
                return {'success': True, 'content': content}
            else:
                return {'success': False, 'error': f"OpenAI Error: {response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _generate_openai_compatible(self, token, prompt_text, model, temperature, base_url):
        import requests
        
        headers = {
            'Authorization': f'Bearer {token.token_value}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt_text}],
            'temperature': temperature,
        }
        
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                token.current_usage += 1
                token.save(update_fields=['current_usage', 'last_used_at'])
                
                content = data['choices'][0]['message']['content']
                return {'success': True, 'content': content}
            else:
                return {'success': False, 'error': f"API Error: {response.text}"}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
