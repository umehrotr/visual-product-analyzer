import anthropic
import base64
import os
from dotenv import load_dotenv
from pathlib import Path
import json
from typing import Dict, List
load_dotenv()
class VisualProductAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
    
    def encode_image(self, image_path: str) -> tuple:
        """
        Encode image to base64 and detect media type
        """
        with open(image_path, "rb") as image_file:
            image_data = base64.standard_b64encode(image_file.read()).decode("utf-8")
        
        # Detect media type
        suffix = Path(image_path).suffix.lower()
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_types.get(suffix, 'image/jpeg')
        
        return image_data, media_type
    
    def analyze_product_image(self, image_path: str, product_category: str = None) -> Dict:
        """
        Analyze a product image and extract structured information
        """
        image_data, media_type = self.encode_image(image_path)
        
        prompt = f"""Analyze this product image and provide detailed information in JSON format.
Product Category: {product_category or "Unknown"}
Extract:
1. Product Type and Category
2. Key Features (visible attributes)
3. Colors (all visible colors)
4. Materials (if identifiable)
5. Condition Assessment (new/used, any defects)
6. Suggested Title (engaging product title)
7. Suggested Description (2-3 sentences)
8. Key Selling Points (3-5 bullet points)
9. Target Audience
10. Comparable Products
Format as valid JSON with these fields:
{{
  "product_type": "",
  "category": "",
  "features": [],
  "colors": [],
  "materials": [],
  "condition": "",
  "defects": [],
  "suggested_title": "",
  "suggested_description": "",
  "key_selling_points": [],
  "target_audience": "",
  "comparable_products": [],
  "confidence_score": 0.0
}}"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        # Parse JSON response
        response_text = message.content[0].text
        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    
    def compare_product_images(self, image1_path: str, image2_path: str) -> str:
        """
        Compare two product images (useful for A/B testing, quality control)
        """
        image1_data, media_type1 = self.encode_image(image1_path)
        image2_data, media_type2 = self.encode_image(image2_path)
        
        prompt = """Compare these two product images and provide:
1. Similarities (what's the same)
2. Differences (what's different)
3. Quality Assessment (which image is better for e-commerce and why)
4. Recommendations (suggested improvements)
Be specific and detailed."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Image 1:"
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type1,
                                "data": image1_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Image 2:"
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type2,
                                "data": image2_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        OCR - Extract text from product packaging, labels, etc.
        """
        image_data, media_type = self.encode_image(image_path)
        
        prompt = """Extract ALL text visible in this image.
Maintain formatting where possible.
Include:
- Product names
- Brand names
- Instructions
- Warnings
- Specifications
- Any other text
Output as plain text, maintaining structure."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text
    
    def generate_alt_text(self, image_path: str, context: str = None) -> str:
        """
        Generate accessibility alt text for images
        """
        image_data, media_type = self.encode_image(image_path)
        
        prompt = f"""Generate accessibility alt text for this image.
Context: {context or "Product image for e-commerce"}
Requirements:
- Concise (50-125 characters)
- Descriptive of key visual elements
- Useful for screen readers
- SEO-friendly
Provide 3 options:
1. Short (for quick scanning)
2. Medium (balanced)
3. Long (detailed)"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        return message.content[0].text

    def analyze_product_multilingual(self, image_path: str, target_languages: List[str]) -> Dict:
        """
        Analyze product and generate descriptions in multiple languages
        """
        image_data, media_type = self.encode_image(image_path)
        
        languages_str = ", ".join(target_languages)
        
        prompt = f"""Analyze this product image and provide information in these languages: {languages_str}
For EACH language, provide:
1. Product Title (optimized for that market)
2. Product Description (2-3 sentences, culturally appropriate)
3. Key Features (3-5 bullet points)
Languages: {languages_str}
Format as JSON:
{{
  "en": {{
    "title": "",
    "description": "",
    "features": []
  }},
  "es": {{...}},
  "fr": {{...}}
}}
Ensure cultural appropriateness and natural phrasing for each language."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        response_text = message.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        
        return json.loads(response_text)


def main():
    analyzer = VisualProductAnalyzer()
    
    print("Visual Product Analyzer")
    print("=" * 60)
    
    # Example: Analyze a product image
    image_path = input("Enter path to product image: ")
    
    if not os.path.exists(image_path):
        print("❌ Image not found!")
        return
    
    print("\n🔍 Analyzing product image...")
    
    try:
        # Full analysis
        analysis = analyzer.analyze_product_image(image_path)
        
        print("\n" + "=" * 60)
        print("PRODUCT ANALYSIS")
        print("=" * 60)
        print(json.dumps(analysis, indent=2))
        
        # Generate alt text
        print("\n" + "=" * 60)
        print("ACCESSIBILITY ALT TEXT")
        print("=" * 60)
        alt_text = analyzer.generate_alt_text(image_path)
        print(alt_text)
        
        # Extract text (if any)
        print("\n" + "=" * 60)
        print("TEXT EXTRACTION (OCR)")
        print("=" * 60)
        text = analyzer.extract_text_from_image(image_path)
        print(text)
        
        # Save results
        output_file = f"analysis_{Path(image_path).stem}.json"
        with open(output_file, "w") as f:
            json.dump({
                "analysis": analysis,
                "alt_text": alt_text,
                "extracted_text": text
            }, f, indent=2)
        
        print(f"\n✅ Full analysis saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
if __name__ == "__main__":
    main()
