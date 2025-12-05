# Visual Product Analyzer

An AI-powered visual product analysis tool using Claude's vision capabilities. Automatically analyze product images, extract information, generate descriptions, and more.

## Features

- **Product Image Analysis**: Extract structured product information (type, features, colors, materials, condition)
- **Multi-Image Comparison**: Compare two product images for A/B testing or quality control
- **OCR Text Extraction**: Extract text from product packaging, labels, and instructions
- **Alt Text Generation**: Generate SEO-friendly accessibility alt text
- **Multilingual Support**: Generate product descriptions in multiple languages
- **Batch Processing**: Process entire directories of images with parallel execution

## Installation

1. Clone the repository:
```bash
git clone https://github.com/umehrotr/visual-product-analyzer.git
cd visual-product-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key
```

## Usage

### Single Image Analysis

```bash
python visual_product_analyzer.py
```

Enter the path to your product image when prompted. The tool will:
1. Analyze the product and extract structured data
2. Generate accessibility alt text
3. Extract any visible text (OCR)
4. Save results to a JSON file

### Programmatic Usage

```python
from visual_product_analyzer import VisualProductAnalyzer

analyzer = VisualProductAnalyzer()

# Full product analysis
analysis = analyzer.analyze_product_image("product.jpg", product_category="Electronics")
print(analysis)

# Compare two images
comparison = analyzer.compare_product_images("image1.jpg", "image2.jpg")
print(comparison)

# Extract text (OCR)
text = analyzer.extract_text_from_image("packaging.jpg")
print(text)

# Generate alt text
alt_text = analyzer.generate_alt_text("product.jpg")
print(alt_text)

# Multilingual descriptions
descriptions = analyzer.analyze_product_multilingual(
    "product.jpg", 
    target_languages=["en", "es", "fr", "de"]
)
print(descriptions)
```

### Batch Processing

```python
from batch_image_processor import BatchImageProcessor

processor = BatchImageProcessor()
results = processor.process_directory("./product_images", "./analysis_output")
```

This will:
- Process all images in the directory (jpg, jpeg, png, webp, gif)
- Save individual JSON results for each image
- Generate a summary CSV report

## Output Format

### Product Analysis JSON

```json
{
  "product_type": "Wireless Headphones",
  "category": "Electronics/Audio",
  "features": ["Over-ear design", "Active noise cancellation", "Bluetooth 5.0"],
  "colors": ["Matte Black", "Silver accents"],
  "materials": ["Plastic", "Faux leather", "Memory foam"],
  "condition": "New",
  "defects": [],
  "suggested_title": "Premium Wireless ANC Headphones with 30-Hour Battery",
  "suggested_description": "Experience immersive audio with these over-ear wireless headphones featuring active noise cancellation...",
  "key_selling_points": ["Active noise cancellation", "30-hour battery life", "Premium comfort"],
  "target_audience": "Music enthusiasts, remote workers, travelers",
  "comparable_products": ["Sony WH-1000XM5", "Bose QuietComfort"],
  "confidence_score": 0.92
}
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## License

MIT

