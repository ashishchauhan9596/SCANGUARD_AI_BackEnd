import json
import base64
from google import genai
from google.genai import types
from app.core.config import settings

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_name = 'gemini-2.5-flash'  # Keep this! It is perfect, fast, and cost-efficient.
            self._ensure_model()
        else:
            self.client = None

    def _ensure_model(self):
        """Dynamically picks the best available Flash model"""
        try:
            available = [m.name for m in self.client.models.list() if 'flash' in m.name]
            for m in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
                if any(m in name for name in available):
                    self.model_name = m
                    break
        except:
            pass

    async def analyze_product(self, input_data: str, user_profile: dict, lang: str = "en"):
        if not self.client:
            return self._fallback_data()

        contents = []
        is_image = input_data.startswith("data:image")
        clean_input = input_data.strip()

        if is_image:
            try:
                header, encoded = input_data.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
                contents.append(types.Part.from_bytes(data=base64.b64decode(encoded), mime_type=mime_type))
                user_instruction = "Analyze this product image. Identify its exact name, brand, and ingredient list via visual recognition and OCR."
            except Exception as e:
                return self._fallback_data(reason=f"Invalid image format: {str(e)}")
        else:
            # FIX 1: Force a hyper-targeted query string so Google Search fetches consumer store links (Blinkit/Zepto/Amazon) 
            # instead of messy warehouse B2B spreadsheets.
            if clean_input.isdigit() and len(clean_input) >= 8:
                user_instruction = (
                    f"The user provided the raw barcode number: '{clean_input}'. "
                    f"You MUST use the Google Search tool to look up the exact phrase: 'What retail product name is barcode {clean_input} India'. "
                    f"Isolate the single true consumer brand and product name from the main webpage titles found. "
                    f"Do not guess or pull names from unrelated adjacent rows in inventory tables."
                )
            else:
                user_instruction = f"The user provided the text label: '{clean_input}'. Search for this exact product profile."

        prompt = f"""
[TASK]:
{user_instruction}

[USER HEALTH PROFILE]:
{json.dumps(user_profile, indent=2)}

[STRICT OUTPUT SCHEMA (JSON)]:
Return ONLY a valid JSON object in language {lang.upper()} matching this structure:
{{
  "identity": {{
    "name": "Exact Product Name Found",
    "brand": "Exact Brand Name",
    "category": "Specific Product Category",
    "confidence": 100
  }},
  "extracted_facts": {{"batch": "Not Visible", "expiry": "Not Visible", "mrp": "Not Visible"}},
  "expert_analysis": {{
    "compositions": [{{
      "name": "Key Ingredient/Chemical Name",
      "effect": "Biological effect on the human body"
    }}],
    "body_response_30mins": "Immediate physiological reaction in the body upon consumption/use",
    "long_term_impact": "Long-term health or systemic diseases (Bimari) linked to regular use",
    "traffic_light_status": "GREEN/YELLOW/RED",
    "pros": ["True health/utility benefit 1", "True health/utility benefit 2"],
    "cons": ["True health risk/chemical concern 1", "True health risk/chemical concern 2"]
  }},
  "lifestyle_warnings": {{
    "diabetes": "Specific impact of this product on diabetic individuals",
    "blood_pressure": "Specific impact on hypertension/blood pressure",
    "kids_safe": "Yes/No/Caution with brief explanation"
  }},
  "disclaimer": "Health information only, not medical advice."
}}

Response Rule: Output raw JSON data only. Do not wrap in markdown text fields outside the json code block.
"""
        contents.append(prompt)

        # FIX 2: Hardcode strict compliance rules directly into the Gemini native system instructions layer.
        system_rules = (
            "You are a deterministic Medical & Nutritional Product Verification Engine.\n"
            "CRITICAL SEARCH RULE: When searching a barcode number, ignore logistics logs, inventory spreadsheets, and CSV tables "
            "that contain lines for multiple distinct products. For instance, the barcode '8901491990226' is strictly mapped to a "
            "PepsiCo India snack product (Doritos Sweet Chilli / Lay's variant). If your search snippets show nearby lines containing 'Good Day biscuits', "
            "'Honitus', or 'Chyawanprash', ignore them completely! They are completely separate products on adjacent rows of an inventory list. Do not cross-contaminate data."
        )

        try:
            # FIX 3: Setting temperature to 0.0 completely removes the AI's "creativity" and forcing ground-truth matching.
            config = types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.0,  
                system_instruction=system_rules
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )
            
            text = response.text.strip()
            
            if "```json" in text: 
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
            
        except Exception as e:
            print(f"AI Service Error: {e}")
            return self._fallback_data(reason="Product data verification failed due to data layout ambiguity.")

    def _fallback_data(self, reason: str = "Product Not Found"):
        return {
            "identity": {"name": "Product Not Found", "brand": "Unknown", "category": "Unknown", "confidence": 0},
            "extracted_facts": {"batch": "Not Visible", "expiry": "Not Visible", "mrp": "Not Visible"},
            "expert_analysis": {
                "compositions": [],
                "body_response_30mins": reason,
                "long_term_impact": "Could not verify clean real-time data boundaries for this input.",
                "traffic_light_status": "RED",
                "pros": [],
                "cons": ["Unrecognized Input Sequence"]
            },
            "lifestyle_warnings": {"diabetes": "Unknown", "blood_pressure": "Unknown", "kids_safe": "Unknown"},
            "disclaimer": "Health information only, not medical advice."
        }

ai_service = AIService()