import base64
import json
import openai
from src import config
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store initialization status
client = None
init_error = None

# Initialize OpenAI client
try:
    api_key = config.get_openai_api_key()
    logger.info(f"Initializing OpenAI client with API key: {api_key[:10]}...")
    
    # Simple initialization without extra parameters
    openai.api_key = api_key
    client = openai
    
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    init_error = str(e)
    logger.error(f"Error initializing OpenAI client: {e}")
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
    Returns tuple: (result_dict, debug_info)
    """
    debug_info = []
    
    if not client:
        error_msg = f"OpenAI client not initialized. Init error: {init_error}"
        debug_info.append(error_msg)
        logger.error(error_msg)
        return None, debug_info
        
    try:
        debug_info.append(f"🔍 Encoding image: {image_path}")
        logger.info(f"Encoding image: {image_path}")
        base64_image = encode_image(image_path)
        debug_info.append(f"✅ Image encoded successfully, size: {len(base64_image)} characters")
        logger.info(f"Image encoded successfully, size: {len(base64_image)} characters")
        
        debug_info.append("🚀 Making OpenAI API call...")
        logger.info("Making OpenAI API call...")
        response = client.ChatCompletion.create(
            model="gpt-4-vision-preview",
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
            temperature=0.7,
            max_tokens=2000
        )
        
        debug_info.append("✅ API call successful, parsing response...")
        logger.info("API call successful, parsing response...")
        content = response.choices[0].message.content
        debug_info.append(f"📄 Raw response preview: {content[:200]}...")
        logger.info(f"Raw response: {content[:200]}...")
        
        # Try to parse JSON from the response
        try:
            analysis_dict = json.loads(content)
            debug_info.append("🎉 JSON parsed successfully")
            logger.info("JSON parsed successfully")
            return analysis_dict, debug_info
        except json.JSONDecodeError:
            # If it's not valid JSON, try to extract JSON from the text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    analysis_dict = json.loads(json_match.group())
                    debug_info.append("🎉 JSON extracted and parsed successfully")
                    logger.info("JSON extracted and parsed successfully")
                    return analysis_dict, debug_info
                except:
                    pass
            
            # If we can't parse JSON, create a structured response manually
            debug_info.append("⚠️ Could not parse JSON, creating manual structure")
            analysis_dict = {
                'image_id': f"IMG-{os.path.basename(image_path).split('.')[0]}",
                'image_type': 'Real Photograph',
                'style_name': 'AI Analysis Result',
                'composition_structure': content[:200] + "...",
                'color_palette': 'Unable to analyze',
                'lighting': 'Unable to analyze',
                'texture_finish': 'Unable to analyze',
                'geometry_flow': 'Unable to analyze',
                'primary_emotional_tone': 'Unable to analyze',
                'emotional_keyword_tags': 'ai-generated, analysis',
                'narrative_metaphor': content,
                'ai_generation_prompt': 'N/A',
                'recreation_guidelines': 'See narrative section for AI response',
                'recommended_use_cases': 'General use'
            }
            return analysis_dict, debug_info
        
    except json.JSONDecodeError as e:
        error_msg = f"❌ JSON parsing error: {e}"
        debug_info.append(error_msg)
        debug_info.append(f"Raw content: {content}")
        logger.error(error_msg)
        logger.error(f"Raw content: {content}")
        return None, debug_info
    except Exception as e:
        error_msg = f"❌ OpenAI API error: {type(e).__name__}: {e}"
        debug_info.append(error_msg)
        logger.error(error_msg)
        import traceback
        traceback_str = traceback.format_exc()
        debug_info.append(f"Full traceback: {traceback_str}")
        logger.error(f"Full traceback: {traceback_str}")
        return None, debug_info 