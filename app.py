import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
import json
import base64
from pathlib import Path

load_dotenv()

# Try Streamlit secrets first (for cloud), fall back to .env (for local)
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

st.set_page_config(page_title="Visual Product Analyzer", layout="wide")

st.title("🖼️ Visual Product Analyzer")
st.markdown("*Analyze product images with AI - Generate descriptions in multiple languages*")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    languages = st.multiselect(
        "Target Languages",
        ["English", "Spanish", "French", "German", "Italian"],
        default=["English", "Spanish", "French"]
    )
    
    language_codes = {
        "English": "en",
        "Spanish": "es", 
        "French": "fr",
        "German": "de",
        "Italian": "it"
    }
    
    selected_codes = [language_codes[lang] for lang in languages]

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Product Analysis", 
    "🔄 Compare Images", 
    "🔤 Extract Text (OCR)",
    "🌍 Multilingual Descriptions"
])

# Helper function to encode image
def encode_image(uploaded_file):
    """Encode uploaded file to base64"""
    uploaded_file.seek(0)  # Reset file position to beginning
    bytes_data = uploaded_file.read()
    image_data = base64.standard_b64encode(bytes_data).decode("utf-8")
    
    # Detect media type
    suffix = Path(uploaded_file.name).suffix.lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    media_type = media_types.get(suffix, 'image/jpeg')
    
    return image_data, media_type

# Tab 1: Basic Product Analysis
with tab1:
    st.header("Product Analysis")
    st.markdown("Upload a product image to get detailed analysis")
    
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg', 'webp'], key="analysis")
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("🔍 Analyze Product", key="analyze_btn"):
                with st.spinner("Analyzing product image..."):
                    try:
                        image_data, media_type = encode_image(uploaded_file)
                        
                        client = anthropic.Anthropic(api_key=api_key)
                        
                        prompt = """Analyze this product image and provide detailed information in JSON format.

Extract:
1. Product Type and Category
2. Key Features (visible attributes)
3. Colors (all visible colors)
4. Materials (if identifiable)
5. Condition Assessment
6. Suggested Title (engaging product title)
7. Suggested Description (2-3 sentences)
8. Key Selling Points (3-5 bullet points)
9. Target Audience

Format as valid JSON."""

                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=2000,
                            messages=[{
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
                                    {"type": "text", "text": prompt}
                                ],
                            }],
                        )
                        
                        response_text = message.content[0].text
                        if "```json" in response_text:
                            response_text = response_text.split("```json")[1].split("```")[0].strip()
                        
                        analysis = json.loads(response_text)
                        
                        st.success("✅ Analysis Complete!")
                        
                        # Display results nicely
                        st.subheader("📊 Analysis Results")
                        
                        if "suggested_title" in analysis:
                            st.markdown(f"**Suggested Title:** {analysis['suggested_title']}")
                        
                        if "suggested_description" in analysis:
                            st.markdown(f"**Description:** {analysis['suggested_description']}")
                        
                        if "key_selling_points" in analysis:
                            st.markdown("**Key Selling Points:**")
                            for point in analysis['key_selling_points']:
                                st.markdown(f"- {point}")
                        
                        # Show full JSON
                        with st.expander("📋 View Full Analysis (JSON)"):
                            st.json(analysis)
                        
                        # Download button
                        st.download_button(
                            "💾 Download Analysis",
                            json.dumps(analysis, indent=2),
                            file_name="product_analysis.json",
                            mime="application/json"
                        )
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Tab 2: Compare Images
with tab2:
    st.header("Compare Product Images")
    st.markdown("Upload two product images to compare them")
    
    col1, col2 = st.columns(2)
    
    with col1:
        image1 = st.file_uploader("First Image", type=['png', 'jpg', 'jpeg', 'webp'], key="img1")
        if image1:
            st.image(image1, caption="Image 1", use_column_width=True)
    
    with col2:
        image2 = st.file_uploader("Second Image", type=['png', 'jpg', 'jpeg', 'webp'], key="img2")
        if image2:
            st.image(image2, caption="Image 2", use_column_width=True)
    
    if image1 and image2:
        if st.button("🔄 Compare Images", key="compare_btn"):
            with st.spinner("Comparing images..."):
                try:
                    image1_data, media_type1 = encode_image(image1)
                    image2_data, media_type2 = encode_image(image2)
                    
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    prompt = """Compare these two product images and provide:

1. Similarities (what's the same)
2. Differences (what's different)
3. Quality Assessment (which image is better for e-commerce and why)
4. Recommendations (suggested improvements)

Be specific and detailed."""

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1500,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Image 1:"},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type1,
                                        "data": image1_data,
                                    },
                                },
                                {"type": "text", "text": "Image 2:"},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type2,
                                        "data": image2_data,
                                    },
                                },
                                {"type": "text", "text": prompt}
                            ],
                        }],
                    )
                    
                    comparison = message.content[0].text
                    
                    st.success("✅ Comparison Complete!")
                    st.markdown(comparison)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 3: Extract Text (OCR)
with tab3:
    st.header("Extract Text from Product Images")
    st.markdown("Extract all visible text from product packaging, labels, etc.")
    
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg', 'webp'], key="ocr")
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("🔤 Extract Text", key="ocr_btn"):
                with st.spinner("Extracting text..."):
                    try:
                        image_data, media_type = encode_image(uploaded_file)
                        
                        client = anthropic.Anthropic(api_key=api_key)
                        
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

                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=2000,
                            messages=[{
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
                                    {"type": "text", "text": prompt}
                                ],
                            }],
                        )
                        
                        extracted_text = message.content[0].text
                        
                        st.success("✅ Text Extracted!")
                        st.text_area("Extracted Text:", extracted_text, height=300)
                        
                        st.download_button(
                            "💾 Download Text",
                            extracted_text,
                            file_name="extracted_text.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Tab 4: Multilingual Descriptions
with tab4:
    st.header("Generate Multilingual Product Descriptions")
    st.markdown(f"Generate descriptions in: {', '.join(languages)}")
    
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg', 'webp'], key="multilingual")
    
    if uploaded_file:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("🌍 Generate Multilingual Descriptions", key="multilingual_btn"):
                with st.spinner("Generating descriptions in multiple languages..."):
                    try:
                        image_data, media_type = encode_image(uploaded_file)
                        
                        client = anthropic.Anthropic(api_key=api_key)
                        
                        languages_str = ", ".join(selected_codes)
                        
                        prompt = f"""Analyze this product image and provide information in these languages: {languages_str}

For EACH language, provide:
1. Product Title (optimized for that market)
2. Product Description (2-3 sentences, culturally appropriate)
3. Key Features (3-5 bullet points)

Languages: {languages_str}

Format as JSON with language codes as keys.
Ensure cultural appropriateness and natural phrasing for each language."""

                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=3000,
                            messages=[{
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
                                    {"type": "text", "text": prompt}
                                ],
                            }],
                        )
                        
                        response_text = message.content[0].text
                        if "```json" in response_text:
                            response_text = response_text.split("```json")[1].split("```")[0].strip()
                        
                        multilingual_data = json.loads(response_text)
                        
                        st.success("✅ Multilingual Descriptions Generated!")
                        
                        # Normalize language code keys to lowercase
                        normalized_data = {k.lower(): v for k, v in multilingual_data.items()}
                        
                        # Display each language
                        for lang_code in selected_codes:
                            if lang_code.lower() in normalized_data:
                                lang_name = [k for k, v in language_codes.items() if v == lang_code][0]
                                
                                with st.expander(f"🌐 {lang_name} ({lang_code.upper()})", expanded=True):
                                    data = normalized_data[lang_code.lower()]
                                    
                                    # Normalize inner keys to lowercase for matching
                                    data_lower = {k.lower(): v for k, v in data.items()}
                                    
                                    if "title" in data_lower:
                                        st.markdown(f"**Title:** {data_lower['title']}")
                                    
                                    if "description" in data_lower:
                                        st.markdown(f"**Description:** {data_lower['description']}")
                                    
                                    if "features" in data_lower:
                                        st.markdown("**Features:**")
                                        for feature in data_lower['features']:
                                            st.markdown(f"- {feature}")
                                    
                                    # Also check for key_features (alternative name)
                                    if "key_features" in data_lower:
                                        st.markdown("**Features:**")
                                        for feature in data_lower['key_features']:
                                            st.markdown(f"- {feature}")
                        
                        # Download button
                        st.download_button(
                            "💾 Download All Descriptions",
                            json.dumps(multilingual_data, indent=2, ensure_ascii=False),
                            file_name="multilingual_descriptions.json",
                            mime="application/json"
                        )
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Built with Anthropic Claude & Streamlit | Part of AI-First PM Study Plan*")