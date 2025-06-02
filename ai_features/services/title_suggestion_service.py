import groq
from typing import List, Dict, Any
from django.conf import settings # Assuming you're using Django settings
import re
import os # While settings is used, os.environ.get is good for robust env var checks

class TitleSuggestionService:
    def __init__(self):
        # Initialize Groq if API key is available from Django settings
        self.groq_client = None
        # It's good practice to ensure the attribute exists and is not a placeholder/empty
        if hasattr(settings, 'GROQ_API_KEY') and settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here':
            try:
                self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
                print(" Groq client initialized successfully using Django settings.")
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
                self.groq_client = None
        else:
            print(" GROQ_API_KEY not found in Django settings or is placeholder.")
            print(" Title generation will fail as Groq is the only method configured and its client couldn't be initialized.")
    
    def generate_title_suggestions(self, content: str) -> Dict[str, Any]:
        try:
            cleaned_content = self._clean_content(content)
            
            if len(cleaned_content.strip()) < 30: # Adjusted minimum length slightly
                return {
                    "success": False,
                    "error": "Content too short for meaningful title generation via Groq API. Minimum 30 characters required.",
                    "suggestions": []
                }
            
            suggestions = []
            method_used = "none" # Default if Groq client isn't available

            if not self.groq_client:
                return {
                    "success": False,
                    "error": "Groq API client not initialized. Please ensure GROQ_API_KEY is set correctly in your Django settings.",
                    "suggestions": []
                }
            
            try:
                print(" Attempting title generation with Groq API...")
                groq_suggestions = self._generate_with_groq(cleaned_content)
                suggestions.extend(groq_suggestions)
                method_used = "groq_api"
                print(f" Generated {len(groq_suggestions)} titles using Groq API.")
            except Exception as e:
                print(f" Groq generation failed: {e}")
                return {
                    "success": False,
                    "error": f"Groq API call failed: {e}",
                    "suggestions": []
                }
            
            # Ensure uniqueness and basic validity (not empty, more than one word)
            unique_suggestions = list(dict.fromkeys(s for s in suggestions if s and len(s.split()) > 1)) 

            final_suggestions = unique_suggestions[:3] # Take up to 3 suggestions from Groq
            
            # If Groq didn't return enough titles, we just return what we have,
            # as fallbacks are explicitly removed.
            if len(final_suggestions) < 3:
                print(f"ℹ Groq API returned {len(final_suggestions)} suggestions, less than the desired 3.")

            return {
                "success": True,
                "suggestions": final_suggestions,
                "content_length": len(content),
                "cleaned_content_length": len(cleaned_content),
                "method_used": method_used
            }
            
        except Exception as e:
            print(f"Error in generate_title_suggestions: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": []
            }

    def _clean_content(self, content: str) -> str:
        if not isinstance(content, str): return ""
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[^\w\s.,!?’\'":-]', '', content) # Added colon, quotes
        
        # Truncate for model input. Groq can handle a lot, but still good to prevent excessively huge inputs.
        max_chars_for_processing = 8000 
        if len(content) > max_chars_for_processing:
            content = content[:max_chars_for_processing] + "..."
        return content.strip()

    def _generate_with_groq(self, content: str) -> List[str]:
        prompt_content = content
        # Groq's Mixtral model has a 32k context window, 8000 chars is safe for input.
        if len(prompt_content) > 8000: 
            prompt_content = prompt_content[:7997] + "..."

        prompt = f"""Generate exactly 3 distinct, engaging, and SEO-friendly blog post titles based on the following content.
Each title should be between 40-70 characters.
Return only the titles, one title per line. Do not use numbering, bullet points, or quotation marks around the titles.

Content:
\"\"\"
{prompt_content}
\"\"\"

Titles:"""
        
        response = self.groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are an expert copywriter specializing in crafting compelling blog post titles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150, # Enough tokens for 3 titles
            temperature=0.7,
            n=1
        )
        
        raw_titles = response.choices[0].message.content.strip()
        titles = [
            title.strip() for title in raw_titles.split('\n') 
            if title.strip() and 5 < len(title.strip()) < 100 # Basic sanity check for title length
        ]
        return [t for t in titles if t][:3]