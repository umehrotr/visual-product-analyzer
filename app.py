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

st.set_page_config(
    page_title="Visual Product Analyzer", 
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Card styling */
    .custom-card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a3e);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .custom-card h3 {
        color: #a78bfa;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Result card */
    .result-card {
        background: linear-gradient(145deg, #1a1a2e, #252538);
        border-left: 4px solid #667eea;
        border-radius: 0 12px 12px 0;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
    }
    
    .result-card h4 {
        color: #a78bfa;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .result-card p {
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Feature list styling */
    .feature-item {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        color: #e2e8f0;
    }
    
    /* Language card */
    .lang-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .lang-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(167, 139, 250, 0.2);
    }
    
    .lang-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .lang-flag {
        font-size: 1.5rem;
    }
    
    .lang-name {
        color: #a78bfa;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d1b4e 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #a78bfa;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 30, 46, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: rgba(30, 30, 46, 0.8);
        border: 2px dashed rgba(167, 139, 250, 0.4);
        border-radius: 12px;
        padding: 2rem;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-radius: 10px;
        font-weight: 600;
        color: #a78bfa;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1));
        border-left: 4px solid #10b981;
        border-radius: 0 10px 10px 0;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.1));
        border-left: 4px solid #ef4444;
        border-radius: 0 10px 10px 0;
    }
    
    /* Footer styling */
    .custom-footer {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d1b4e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 3rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    
    .custom-footer p {
        color: #94a3b8;
        margin: 0;
        font-size: 0.9rem;
    }
    
    .custom-footer a {
        color: #a78bfa;
        text-decoration: none;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Image container */
    .image-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎨 Visual Product Analyzer</h1>
    <p>AI-powered image analysis • Multilingual descriptions • Smart OCR extraction</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Configuration")
    st.markdown("---")
    
    st.markdown("#### 🌐 Languages")
    languages = st.multiselect(
        "Select target languages",
        ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Chinese"],
        default=["English", "Spanish", "French"],
        label_visibility="collapsed"
    )
    
    language_codes = {
        "English": "en",
        "Spanish": "es", 
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Japanese": "ja",
        "Chinese": "zh"
    }
    
    language_flags = {
        "English": "🇺🇸",
        "Spanish": "🇪🇸", 
        "French": "🇫🇷",
        "German": "🇩🇪",
        "Italian": "🇮🇹",
        "Portuguese": "🇵🇹",
        "Japanese": "🇯🇵",
        "Chinese": "🇨🇳"
    }
    
    selected_codes = [language_codes[lang] for lang in languages]
    
    st.markdown("---")
    st.markdown("#### ℹ️ About")
    st.markdown("""
    <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.6;">
    Powered by <strong style="color: #a78bfa;">Claude AI</strong> vision capabilities.
    Upload any product image to get instant analysis, translations, and text extraction.
    </div>
    """, unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Product Analysis", 
    "🔄 Compare Images", 
    "🔤 Text Extraction",
    "🌍 Multilingual"
])

# Helper function to encode image
def encode_image(uploaded_file):
    """Encode uploaded file to base64"""
    uploaded_file.seek(0)
    bytes_data = uploaded_file.read()
    image_data = base64.standard_b64encode(bytes_data).decode("utf-8")
    
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

# Tab 1: Product Analysis
with tab1:
    st.markdown("### 🔍 Analyze Product Images")
    st.markdown("Upload a product image to get AI-powered insights, descriptions, and selling points.")
    
    uploaded_file = st.file_uploader("Drop your image here", type=['png', 'jpg', 'jpeg', 'webp'], key="analysis")
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(uploaded_file, caption="📸 Uploaded Image", use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Ready to analyze")
            st.markdown("Click the button below to start AI analysis of your product image.")
            
            if st.button("🚀 Analyze Product", key="analyze_btn", use_container_width=True):
                with st.spinner("🔮 AI is analyzing your image..."):
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
                        elif "```" in response_text:
                            response_text = response_text.split("```")[1].split("```")[0].strip()
                        
                        analysis = json.loads(response_text)
                        
                        st.success("✨ Analysis Complete!")
                        
                        # Normalize keys
                        analysis_lower = {k.lower().replace(" ", "_"): v for k, v in analysis.items()}
                        
                        # Display results in cards
                        if "suggested_title" in analysis_lower:
                            st.markdown(f"""
                            <div class="result-card">
                                <h4>📌 Suggested Title</h4>
                                <p>{analysis_lower['suggested_title']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if "suggested_description" in analysis_lower:
                            st.markdown(f"""
                            <div class="result-card">
                                <h4>📝 Description</h4>
                                <p>{analysis_lower['suggested_description']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if "key_selling_points" in analysis_lower:
                            st.markdown("#### 🎯 Key Selling Points")
                            for point in analysis_lower['key_selling_points']:
                                st.markdown(f'<div class="feature-item">✓ {point}</div>', unsafe_allow_html=True)
                        
                        with st.expander("📋 View Full Analysis (JSON)"):
                            st.json(analysis)
                        
                        st.download_button(
                            "💾 Download Analysis",
                            json.dumps(analysis, indent=2),
                            file_name="product_analysis.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Tab 2: Compare Images
with tab2:
    st.markdown("### 🔄 Compare Product Images")
    st.markdown("Upload two images to get a detailed comparison for A/B testing or quality control.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### Image A")
        image1 = st.file_uploader("First image", type=['png', 'jpg', 'jpeg', 'webp'], key="img1", label_visibility="collapsed")
        if image1:
            st.image(image1, caption="Image A", use_column_width=True)
    
    with col2:
        st.markdown("#### Image B")
        image2 = st.file_uploader("Second image", type=['png', 'jpg', 'jpeg', 'webp'], key="img2", label_visibility="collapsed")
        if image2:
            st.image(image2, caption="Image B", use_column_width=True)
    
    if image1 and image2:
        if st.button("🔄 Compare Images", key="compare_btn", use_container_width=True):
            with st.spinner("🔮 Comparing images..."):
                try:
                    image1_data, media_type1 = encode_image(image1)
                    image2_data, media_type2 = encode_image(image2)
                    
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    prompt = """Compare these two product images and provide:

1. **Similarities** - What's the same between both images
2. **Differences** - What's different between them
3. **Quality Assessment** - Which image is better for e-commerce and why
4. **Recommendations** - Suggested improvements for each

Be specific and detailed. Format with clear headers."""

                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1500,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Image A:"},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type1,
                                        "data": image1_data,
                                    },
                                },
                                {"type": "text", "text": "Image B:"},
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
                    
                    st.success("✨ Comparison Complete!")
                    st.markdown("---")
                    st.markdown(message.content[0].text)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Tab 3: OCR
with tab3:
    st.markdown("### 🔤 Extract Text from Images")
    st.markdown("Extract all visible text from product packaging, labels, and documents.")
    
    uploaded_file = st.file_uploader("Drop your image here", type=['png', 'jpg', 'jpeg', 'webp'], key="ocr")
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.image(uploaded_file, caption="📸 Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("🔤 Extract Text", key="ocr_btn", use_container_width=True):
                with st.spinner("🔮 Extracting text..."):
                    try:
                        image_data, media_type = encode_image(uploaded_file)
                        client = anthropic.Anthropic(api_key=api_key)
                        
                        prompt = """Extract ALL text visible in this image.

Maintain formatting and structure where possible.
Include:
- Product names and brand names
- Instructions and warnings
- Specifications and ingredients
- Any other visible text

Output as clean, structured plain text."""

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
                        
                        st.success("✨ Text Extracted!")
                        st.text_area("Extracted Text:", extracted_text, height=300)
                        
                        st.download_button(
                            "💾 Download Text",
                            extracted_text,
                            file_name="extracted_text.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Tab 4: Multilingual
with tab4:
    st.markdown("### 🌍 Generate Multilingual Descriptions")
    
    # Show selected languages with flags
    lang_display = " • ".join([f"{language_flags.get(lang, '🌐')} {lang}" for lang in languages])
    st.markdown(f"**Selected languages:** {lang_display}")
    
    uploaded_file = st.file_uploader("Drop your image here", type=['png', 'jpg', 'jpeg', 'webp'], key="multilingual")
    
    if uploaded_file:
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            st.image(uploaded_file, caption="📸 Uploaded Image", use_column_width=True)
        
        with col2:
            if st.button("🌍 Generate Descriptions", key="multilingual_btn", use_container_width=True):
                with st.spinner("🔮 Generating multilingual content..."):
                    try:
                        image_data, media_type = encode_image(uploaded_file)
                        client = anthropic.Anthropic(api_key=api_key)
                        
                        languages_str = ", ".join(selected_codes)
                        
                        prompt = f"""Analyze this product image and provide information in these languages: {languages_str}

For EACH language, provide:
1. title - Product title optimized for that market
2. description - 2-3 sentences, culturally appropriate
3. features - 3-5 key feature bullet points

Format as JSON with lowercase language codes as keys (e.g., "en", "es", "fr").
Use lowercase keys for title, description, and features.
Ensure cultural appropriateness and natural phrasing."""

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
                        elif "```" in response_text:
                            response_text = response_text.split("```")[1].split("```")[0].strip()
                        
                        multilingual_data = json.loads(response_text)
                        
                        st.success("✨ Descriptions Generated!")
                        
                        # Normalize keys
                        normalized_data = {k.lower(): v for k, v in multilingual_data.items()}
                        
                        # Display each language in styled cards
                        for lang_code in selected_codes:
                            if lang_code.lower() in normalized_data:
                                lang_name = [k for k, v in language_codes.items() if v == lang_code][0]
                                flag = language_flags.get(lang_name, "🌐")
                                
                                data = normalized_data[lang_code.lower()]
                                data_lower = {k.lower(): v for k, v in data.items()}
                                
                                with st.expander(f"{flag} {lang_name}", expanded=True):
                                    if "title" in data_lower:
                                        st.markdown(f"""
                                        <div class="result-card">
                                            <h4>📌 Title</h4>
                                            <p>{data_lower['title']}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    if "description" in data_lower:
                                        st.markdown(f"""
                                        <div class="result-card">
                                            <h4>📝 Description</h4>
                                            <p>{data_lower['description']}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    features = data_lower.get('features') or data_lower.get('key_features', [])
                                    if features:
                                        st.markdown("**Features:**")
                                        for feature in features:
                                            st.markdown(f'<div class="feature-item">✓ {feature}</div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            "💾 Download All Descriptions",
                            json.dumps(multilingual_data, indent=2, ensure_ascii=False),
                            file_name="multilingual_descriptions.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("""
<div class="custom-footer">
    <p>Built with ❤️ using <strong>Claude AI</strong> & <strong>Streamlit</strong> | 
    <a href="https://github.com/umehrotr/visual-product-analyzer" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
