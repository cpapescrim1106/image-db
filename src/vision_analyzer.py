import base64
import json
import openai
from src import config

# Initialize OpenAI client
try:
    api_key = config.get_openai_api_key()
    print(f"Initializing OpenAI client with API key: {api_key[:10]}...")
    client = openai.OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

def encode_image(image_path):
    """Encodes a local image file into a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_system_prompt():
    """Returns the detailed system prompt instructing the AI."""
    return """
    You are an expert brand asset analyst. Your task is to analyze the provided image and return a single, valid JSON object that catalogs it according to a specific schema. The JSON output must not be enclosed in markdown backticks.

    The required JSON schema is as follows:
    {
      "image_id": "string (e.g., AI-BG-001)",
      "image_type": "string ('AI-Generated' or 'Real Photograph')",
      "style_name": "string (A formal name for the aesthetic)",
      "composition_structure": "string (Description of element arrangement)",
      "color_palette": "string (Detailed breakdown of primary, accent, and neutral colors with HEX codes if possible)",
      "lighting": "string (Analysis of light source, style, shadows, and contrast)",
      "texture_finish": "string (Description of perceived surface quality, gloss, or grain)",
      "geometry_flow": "string (Dominant shapes, lines, and perceived movement)",
      "primary_emotional_tone": "string (The main feeling the image evokes)",
      "emotional_keyword_tags": "string (A comma-separated list of specific feeling keywords)",
      "narrative_metaphor": "string (The story or concept the image communicates)",
      "ai_generation_prompt": "string (If AI-generated, provide a descriptive prompt to recreate it. Otherwise, N/A)",
      "recreation_guidelines": "string (Key steps for a designer to reproduce the style)",
      "recommended_use_cases": "string (A comma-separated list of practical applications, e.g., 'Website hero sections, Social media quotes')"
    }
    """

def analyze_image_with_gpt(image_path):
    """
    Analyzes an image using GPT-4o and returns a structured dictionary.
    """
    if not client:
        print("OpenAI client not initialized")
        return None
        
    try:
        print(f"Encoding image: {image_path}")
        base64_image = encode_image(image_path)
        print(f"Image encoded successfully, size: {len(base64_image)} characters")
        
        print("Making OpenAI API call...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": get_system_prompt()
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please analyze this image and provide the JSON output."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2000
        )
        
        print("API call successful, parsing response...")
        content = response.choices[0].message.content
        print(f"Raw response: {content[:200]}...")
        
        # Parse the JSON response
        analysis_dict = json.loads(content)
        print("JSON parsed successfully")
        return analysis_dict
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw content: {content}")
        return None
    except Exception as e:
        print(f"OpenAI API error: {type(e).__name__}: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None 