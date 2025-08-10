import streamlit as st
import pandas as pd
from PIL import Image
import json
import os
from datetime import datetime
import numpy as np
import glob
import hashlib
import uuid
import sys

# Handle PyTorch and Transformers import with error handling for Streamlit Cloud
try:
    import torch
    # Set torch to CPU only to avoid CUDA issues on cloud
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    torch_available = True
except ImportError:
    st.error("PyTorch not available. Please install PyTorch CPU version.")
    torch_available = False

try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    transformers_available = True
except ImportError:
    st.error("Transformers library not available. Please install transformers.")
    transformers_available = False

# Configure page
st.set_page_config(
    page_title="తెలుగు లెన్స్ | Name The Object: Telugu Edition",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize language preference
if 'language' not in st.session_state:
    st.session_state.language = 'telugu'

# Language toggle function
def toggle_language():
    st.session_state.language = 'english' if st.session_state.language == 'telugu' else 'telugu'

# Language content dictionary
CONTENT = {
    'telugu': {
        'app_title': '🏷️ తెలుగు లెన్స్',
        'app_subtitle': '✨ తెలుగు మాండలికాలను భద్రపరచే అద్భుత ప్లాట్‌ఫారమ్ ✨',
        'tagline': 'సాంప్రదాయికత మరియు టెక్నాలజీ కలయిక! 🚀',
        'login': 'ప్రవేశం',
        'register': 'నమోదు',
        'username': 'వినియోగదారు పేరు',
        'password': 'పాస్‌వర్డ్',
        'region': 'మీ ప్రాంతం',
        'welcome_back': 'స్వాగతం!',
        'join_community': 'మా కమ్యూనిటీలో చేరండి!',
        'login_btn': 'ప్రవేశించండి',
        'register_btn': 'నమోదు కండి',
        'fill_all_fields': 'దయచేసి అన్ని ఫీల్డ్‌లను పూరించండి!',
        'navigation': 'నావిగేషన్',
        'hello': 'నమస్కారం',
        'home': 'హోమ్',
        'identify': 'గుర్తించండి',
        'upload': 'అప్‌లోడ్',
        'explore': 'అన్వేషించండి',
        'browse': 'చూడండి',
        'logout': 'లాగ్ అవుట్',
        'our_mission': 'మా లక్ష్యం',
        'mission_desc': 'వివిధ ప్రాంతాల తెలుగు మాండలికాలను భద్రపరచడం మరియు పంచుకోవడం!',
        'ai_power': 'AI శక్తి',
        'ai_desc': 'అత్యాధునిక AI టెక్నాలజీతో మీ మాటలను అర్థం చేసుకుంటుంది!',
        'preserve_dialects': 'మాండలికాలను కాపాడండి',
        'preserve_desc': 'మీ ప్రాంతపు ప్రత్యేకమైన పదాలను మాతో పంచుకోండి!',
        'community_data': 'కమ్యూనిటీ డేటా',
        'community_desc': 'ఇతర ప్రాంతాల పేర్లను చూడండి మరియు నేర్చుకోండి!',
        'how_it_works': 'ఎలా పని చేస్తుంది:',
        'identify_objects': 'వస్తువులను గుర్తించండి',
        'identify_desc': 'చిత్రాలను చూసి మీ మాండలికంలో పేర్లు చెప్పండి!',
        'upload_image': 'చిత్రం అప్‌లోడ్ చేయండి',
        'explore_data': 'కమ్యూనిటీ డేటాను అన్వేషించండి',
        'browse_contributions': 'కృషిని చూడండి',
        'your_dialect_word': 'మీ మాండలిక పదం',
        'what_call_object': 'ఈ వస్తువును మీరు ఏమని పిలుస్తారు?',
        'object_type': 'వస్తువు రకం',
        'type_placeholder': 'ఉదా: వంటగది సామాన్, పూజా వస్తువు...',
        'submit': 'సేవ్ చేయండి',
        'next': 'తదుపరి',
        'ai_caption': 'AI వర్ణన పొందండి',
        'excellent_match': 'అద్భుతం! అద్భుత జతపాటు:',
        'good_match': 'బాగుంది! మంచి జతపాటు:',
        'different_meaning': 'వేరుగా ఉంది! భిన్న అర్థం:',
        'successfully_saved': 'విజయవంతంగా సేవ్ అయ్యింది!',
        'object_uploaded': 'వస్తువు విజయవంతంగా అప్‌లోడ్ అయ్యింది!',
        'your_stats': 'మీ గణాంకాలు',
        'identifications': 'గుర్తింపులు',
        'uploads': 'అప్‌లోడ్‌లు',
        'regions': 'ప్రాంతాలు',
        'members': 'సభ్యులు',
        'by_region': 'ప్రాంతం ప్రకారం',
        'by_object_type': 'వస్తువు రకం ప్రకారం',
        'member_contributions': 'సభ్యుల కృషి',
        'browse_images': 'చిత్రాలను చూడండి',
        'learn_from_others': 'ఇతరుల నుండి నేర్చుకోండి'
    },
    'english': {
        'app_title': '🏷️ Name The Object- Telugu Edition',
        'app_subtitle': '✨ Amazing Platform for Preserving Telugu Dialects ✨',
        'tagline': 'Where tradition meets technology! 🚀',
        'login': 'Login',
        'register': 'Register',
        'username': 'Username',
        'password': 'Password',
        'region': 'Your Region',
        'welcome_back': 'Welcome back!',
        'join_community': 'Join our community!',
        'login_btn': 'Login',
        'register_btn': 'Register',
        'fill_all_fields': 'Please fill all fields!',
        'navigation': 'Navigation',
        'hello': 'Hello',
        'home': 'Home',
        'identify': 'Identify',
        'upload': 'Upload',
        'explore': 'Explore',
        'browse': 'Browse',
        'logout': 'Logout',
        'our_mission': 'Our Mission',
        'mission_desc': 'Preserving and sharing Telugu dialects from different regions!',
        'ai_power': 'AI Power',
        'ai_desc': 'Advanced AI understands your words and meanings!',
        'preserve_dialects': 'Preserve Dialects',
        'preserve_desc': 'Share your region\'s unique vocabulary with us!',
        'community_data': 'Community Data',
        'community_desc': 'Explore and learn names from other regions!',
        'how_it_works': 'How it works:',
        'identify_objects': 'Identify Objects',
        'identify_desc': 'Look at images and tell names in your dialect!',
        'upload_image': 'Upload Image',
        'explore_data': 'Explore Community Data',
        'browse_contributions': 'Browse Contributions',
        'your_dialect_word': 'Your Dialect Word',
        'what_call_object': 'What do you call this object?',
        'object_type': 'Object type',
        'type_placeholder': 'e.g., kitchen item, religious object...',
        'submit': 'Submit',
        'next': 'Next',
        'ai_caption': 'Generate AI Caption',
        'excellent_match': 'Excellent! Perfect match:',
        'good_match': 'Good! Nice match:',
        'different_meaning': 'Different! Different meaning:',
        'successfully_saved': 'Successfully saved!',
        'object_uploaded': 'Object uploaded successfully!',
        'your_stats': 'Your Stats',
        'identifications': 'Identifications',
        'uploads': 'Uploads',
        'regions': 'Regions',
        'members': 'Members',
        'by_region': 'By Region',
        'by_object_type': 'By Object Type',
        'member_contributions': 'Member Contributions',
        'browse_images': 'Browse Images',
        'learn_from_others': 'Learn from Others'
    }
}

def get_text(key):
    """Get text based on current language"""
    return CONTENT[st.session_state.language].get(key, key)

# Apply enhanced theme styles with catchy elements
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .language-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        padding: 8px 16px;
        color: white;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        font-size: 14px;
        min-width: 120px;
    }
    
    .language-toggle:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .feature-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #4ECDC4;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        font-family: 'Poppins', sans-serif;
        transition: transform 0.3s ease;
        color: #2c3e50 !important;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-card h3 {
        color: #1a202c !important;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .feature-card p {
        color: #4a5568 !important;
        line-height: 1.6;
    }
    
    .browse-card {
    background: linear-gradient(145deg, #ffffff, #f8f9fa);
    padding: 1rem;
    border-radius: 12px;
    border: 2px solid #e9ecef;
    margin: 0.5rem 0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    font-family: 'Poppins', sans-serif;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    color: #2c3e50; /* Dark blue-gray for excellent readability */
}

.browse-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border-color: #667eea;
    color: #1a252f; /* Slightly darker on hover for emphasis */
}

.browse-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
}

/* Additional text styling for better visibility */
.browse-card h1,
.browse-card h2,
.browse-card h3,
.browse-card h4,
.browse-card h5,
.browse-card h6 {
    color: #34495e; /* Darker shade for headings */
    font-weight: 600;
}

.browse-card p {
    color: #2c3e50; /* Main text color */
    line-height: 1.6;
}

.browse-card a {
    color: #667eea; /* Link color matching the gradient */
    text-decoration: none;
    font-weight: 500;
}

.browse-card a:hover {
    color: #764ba2;
    text-decoration: underline;
}
    
    .dialect-input {
        background: linear-gradient(145deg, #fff3cd, #ffeaa7);
        padding: 1.5rem;
        border-radius: 12px;
        border: 3px solid #f39c12;
        box-shadow: 0 5px 15px rgba(243,156,18,0.3);
        font-family: 'Poppins', sans-serif;
    }
    
    .similarity-score {
        font-size: 1.3rem;
        font-weight: bold;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }
    
    .high-similarity {
        background: linear-gradient(145deg, #d4edda, #c3e6cb);
        color: #155724;
        border: 2px solid #28a745;
    }
    
    .medium-similarity {
        background: linear-gradient(145deg, #fff3cd, #ffeaa7);
        color: #856404;
        border: 2px solid #ffc107;
    }
    
    .low-similarity {
        background: linear-gradient(145deg, #f8d7da, #f1aeb5);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    
    .nav-button {
        width: 100%;
        margin-bottom: 0.5rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }
    
    .category-header {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0 0.5rem 0;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .login-container {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 2rem auto;
        font-family: 'Poppins', sans-serif;
    }
    
    .success-message {
        background: linear-gradient(145deg, #d4edda, #c3e6cb);
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        font-family: 'Poppins', sans-serif;
    }
    
    .telugu-support {
        background: linear-gradient(145deg, #e3f2fd, #bbdefb);
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #2196f3;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #1565c0;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .recent-activity {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
        font-family: 'Poppins', sans-serif;
    }
    
    .word-comparison {
        background: linear-gradient(145deg, #e8f5e8, #d4edda);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
        font-family: 'Poppins', sans-serif;
    }
    
    .filter-section {
        background: linear-gradient(145deg, #f0f0f0, #e0e0e0);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .search-tip {
        background: linear-gradient(145deg, #fff3e0, #ffcc02);
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff9800;
        font-size: 0.9rem;
        color: #e65100;
    }
    
    .regional-badge {
        display: inline-block;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .type-badge {
        display: inline-block;
        background: linear-gradient(45deg, #2196F3, #1976D2);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .comparison-section {
        background: linear-gradient(145deg, #f3e5f5, #e1bee7);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #9c27b0;
    }
    
    .error-message {
        background: linear-gradient(145deg, #f8d7da, #f1aeb5);
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        font-family: 'Poppins', sans-serif;
    }
    
    .warning-message {
        background: linear-gradient(145deg, #fff3cd, #ffeaa7);
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        font-family: 'Poppins', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Language toggle button at the top
current_lang_text = "తెలుగు" if st.session_state.language == 'telugu' else "English"
other_lang_text = "English" if st.session_state.language == 'telugu' else "తెలుగు"

st.markdown(f"""
<div style="text-align: right; margin-bottom: 20px;">
    <button class="language-toggle" onclick="document.querySelector('[data-testid=\"baseButton-secondary\"]').click();">
        🌐 Switch to {other_lang_text}
    </button>
</div>
""", unsafe_allow_html=True)

# Create a hidden button that actually triggers the language toggle
if st.button("Toggle Language", key="hidden_toggle", help="Language toggle", type="secondary"):
    toggle_language()
    st.rerun()

# Create directories if they don't exist
os.makedirs("images", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("users", exist_ok=True)

# Authentication functions
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def load_users():
    try:
        with open("users/users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open("users/users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def register_user(username, password, region):
    users = load_users()
    if username in users:
        success_msg = "వినియోగదారు పేరు ఇప్పటికే ఉంది! 😅" if st.session_state.language == 'telugu' else "Username already exists! 😅"
        return False, success_msg
    
    users[username] = {
        "password": hash_password(password),
        "region": region,
        "created_at": datetime.now().isoformat(),
        "submissions": 0
    }
    save_users(users)
    success_msg = "నమోదు విజయవంతం! మా కమ్యూనిటీకి స్వాగతం! 🎉" if st.session_state.language == 'telugu' else "Registration successful! Welcome to our community! 🎉"
    return True, success_msg

def login_user(username, password):
    users = load_users()
    if username not in users:
        error_msg = "వినియోగదారు పేరు కనుగొనబడలేదు! 🤔" if st.session_state.language == 'telugu' else "Username not found! 🤔"
        return False, error_msg
    
    if verify_password(password, users[username]["password"]):
        success_msg = "ప్రవేశం విజయవంతం! తిరిగి స్వాగతం! 👋" if st.session_state.language == 'telugu' else "Login successful! Welcome back! 👋"
        return True, success_msg
    else:
        error_msg = "తప్పు పాస్‌వర్డ్! 🔐" if st.session_state.language == 'telugu' else "Incorrect password! 🔐"
        return False, error_msg

# Data persistence functions
def load_submissions():
    try:
        with open("data/submissions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_submissions(submissions):
    with open("data/submissions.json", "w", encoding="utf-8") as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)

def load_uploads():
    try:
        with open("data/uploads.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_uploads(uploads):
    with open("data/uploads.json", "w", encoding="utf-8") as f:
        json.dump(uploads, f, ensure_ascii=False, indent=2)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

if 'submissions' not in st.session_state:
    st.session_state.submissions = load_submissions()

if 'uploads' not in st.session_state:
    st.session_state.uploads = load_uploads()

if 'blip_model' not in st.session_state:
    st.session_state.blip_model = None
    st.session_state.blip_processor = None

if 'ai_model_loaded' not in st.session_state:
    st.session_state.ai_model_loaded = False

if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0

if 'image_files' not in st.session_state:
    st.session_state.image_files = []

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Load images from folder
@st.cache_data
def load_images_from_folder():
    """Load all images from the images folder"""
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
    image_files = []
    
    for extension in image_extensions:
        image_files.extend(glob.glob(f"images/{extension}"))
    
    # If no images, create some sample data
    if not image_files:
        # Create sample images directory structure
        sample_images = []
        try:
            # Try to create some placeholder images if none exist
            from PIL import Image, ImageDraw, ImageFont
            
            sample_objects = [
                ("sample_pot.jpg", "Traditional Pot", "#8B4513"),
                ("sample_spoon.jpg", "Wooden Spoon", "#DEB887"), 
                ("sample_lamp.jpg", "Oil Lamp", "#FFD700")
            ]
            
            for filename, text, color in sample_objects:
                img = Image.new('RGB', (300, 300), color)
                draw = ImageDraw.Draw(img)
                
                # Try to use a basic font
                try:
                    # Use default PIL font
                    draw.text((50, 150), text, fill='white', anchor='mm')
                except:
                    # If font loading fails, just create colored rectangles
                    pass
                
                img.save(f"images/{filename}")
                sample_images.append(filename)
            
            return sample_images
            
        except Exception as e:
            st.warning(f"Could not create sample images: {str(e)}")
            return []
    
    return sorted([os.path.basename(f) for f in image_files])

# Initialize image files
if not st.session_state.image_files:
    st.session_state.image_files = load_images_from_folder()

# BLIP Image Captioning Function with error handling
@st.cache_resource
def load_blip_model():
    """Load BLIP model and processor with error handling"""
    if not torch_available or not transformers_available:
        return None, None
        
    try:
        # Force CPU usage to avoid CUDA issues on Streamlit Cloud
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Ensure model is on CPU
        model = model.to('cpu')
        model.eval()  # Set to evaluation mode
        
        return processor, model
    except Exception as e:
        st.error(f"Error loading BLIP model: {str(e)}")
        st.error("This might be due to insufficient memory or missing dependencies on Streamlit Cloud.")
        return None, None

def generate_image_caption(image):
    """Generate caption using BLIP model with comprehensive error handling"""
    if not torch_available or not transformers_available:
        return "AI model unavailable: PyTorch or Transformers not installed"
        
    if st.session_state.blip_processor is None or st.session_state.blip_model is None:
        processor, model = load_blip_model()
        if processor is None or model is None:
            return "Error: Could not load BLIP model. This might be due to memory constraints on Streamlit Cloud."
        st.session_state.blip_processor = processor
        st.session_state.blip_model = model
    
    try:
        # Ensure image is in RGB format
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Process the image
        inputs = st.session_state.blip_processor(image, return_tensors="pt")
        
        # Ensure inputs are on CPU
        if torch_available:
            inputs = {k: v.to('cpu') for k, v in inputs.items() if hasattr(v, 'to')}
        
        # Generate caption with error handling
        with torch.no_grad():
            output = st.session_state.blip_model.generate(
                **inputs, 
                max_length=50, 
                num_beams=5,
                do_sample=False,  # Disable sampling for more stable results
                early_stopping=True
            )
        
        caption = st.session_state.blip_processor.decode(output[0], skip_special_tokens=True)
        return caption
        
    except Exception as e:
        error_msg = f"Error generating caption: {str(e)}"
        st.warning("AI model encountered an issue. This might be due to memory constraints on Streamlit Cloud.")
        return error_msg

def calculate_semantic_similarity(telugu_text, english_caption):
    """Mock function for semantic similarity"""
    return np.random.uniform(0.3, 0.95)

def load_ai_models():
    """Load AI models with comprehensive error handling"""
    if not torch_available or not transformers_available:
        error_msg = "❌ AI libraries not available" if st.session_state.language == 'english' else "❌ AI లైబ్రరీలు అందుబాటులో లేవు"
        st.error(error_msg)
        st.error("Please ensure PyTorch and Transformers are installed. Add them to your requirements.txt file.")
        return False
        
    if not st.session_state.ai_model_loaded:
        loading_msg = "🤖 మా AI మోడల్‌ను లోడ్ చేస్తున్నాము..." if st.session_state.language == 'telugu' else "🤖 Loading our magical AI brain..."
        success_msg = "✅ AI మోడల్ విజయవంతంగా లోడ్ అయ్యింది!" if st.session_state.language == 'telugu' else "✅ Model loaded successfully!"
        info_msg = "💡 తదుపరిసారి మరింత వేగంగా లోడ్ అవుతుంది!" if st.session_state.language == 'telugu' else "💡 Will load faster next time!"
        error_msg = "❌ AI మోడల్ లోడ్ కాలేదు." if st.session_state.language == 'telugu' else "❌ Failed to load AI model."
        
        with st.spinner(loading_msg):
            try:
                processor, model = load_blip_model()
                if processor is not None and model is not None:
                    st.session_state.blip_processor = processor
                    st.session_state.blip_model = model
                    st.session_state.ai_model_loaded = True
                    st.success(success_msg)
                    st.info(info_msg)
                    return True
                else:
                    st.error(error_msg)
                    st.error("This might be due to insufficient memory on Streamlit Cloud. The app will continue without AI features.")
                    return False
            except Exception as e:
                st.error(f"{error_msg} Error: {str(e)}")
                return False
    return True

def save_uploaded_image(uploaded_file):
    """Save uploaded image to images folder"""
    try:
        # Generate unique filename
        file_extension = uploaded_file.name.split('.')[-1]
        unique_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Save to images folder
        image_path = f"images/{unique_filename}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Add to image files list
        if unique_filename not in st.session_state.image_files:
            st.session_state.image_files.append(unique_filename)
        
        return unique_filename
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return None

def save_camera_image(camera_image):
    """Save camera captured image to images folder"""
    try:
        # Generate unique filename
        unique_filename = f"camera_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"
        
        # Save to images folder
        image_path = f"images/{unique_filename}"
        image = Image.open(camera_image)
        image.save(image_path)
        
        # Add to image files list
        if unique_filename not in st.session_state.image_files:
            st.session_state.image_files.append(unique_filename)
        
        return unique_filename
    except Exception as e:
        st.error(f"Error saving camera image: {str(e)}")
        return None

def set_page(page_name):
    st.session_state.current_page = page_name

def get_browse_data():
    """Get combined data for browsing"""
    browse_data = []
    
    # Add submissions with images
    for submission in st.session_state.submissions:
        if submission.get('image_name') and submission.get('telugu_word'):
            browse_data.append({
                'type': 'identification',
                'image_name': submission.get('image_name'),
                'telugu_word': submission.get('telugu_word'),
                'object_type': submission.get('object_type', 'Uncategorized'),
                'region': submission.get('region', 'Unknown'),
                'username': submission.get('username', 'Anonymous'),
                'timestamp': submission.get('timestamp', ''),
                'source': 'identification',
                'id': submission.get('id', str(uuid.uuid4()))
            })
    
    # Add uploaded images with their details
    for upload in st.session_state.uploads:
        if upload.get('filename') and upload.get('telugu_name'):
            browse_data.append({
                'type': 'upload',
                'image_name': upload.get('filename'),
                'telugu_word': upload.get('telugu_name'),
                'object_type': upload.get('category', 'Uncategorized'),
                'region': upload.get('region', 'Unknown'),
                'username': upload.get('username', 'Anonymous'),
                'timestamp': upload.get('timestamp', ''),
                'description': upload.get('description', ''),
                'display_name': upload.get('image_name', upload.get('filename')),
                'source': upload.get('source', 'upload'),
                'id': upload.get('id', str(uuid.uuid4()))
            })
    
    return browse_data

def display_browse_card(item, show_comparison=False):
    """Display a browse card for an item"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image_path = f"images/{item['image_name']}"
        try:
            image = Image.open(image_path)
            st.image(image, use_container_width=True)
        except:
            st.markdown("🖼️ *Image not available*")
    
    with col2:
        # Format timestamp
        try:
            formatted_time = pd.to_datetime(item['timestamp']).strftime('%Y-%m-%d %H:%M') if item['timestamp'] else 'Unknown time'
        except:
            formatted_time = 'Unknown time'
        
        st.markdown(f"""
        <div class="browse-card">
            <h3 style="color: #667eea; margin-top: 0; font-size: 1.4rem;">{item['telugu_word']}</h3>
            <div style="margin: 8px 0;">
                <span class="regional-badge">📍 {item['region']}</span>
                <span class="type-badge">🏷️ {item['object_type']}</span>
            </div>
            <p style="margin: 8px 0;"><strong>👤 Contributed by:</strong> {item['username']}</p>
            <p style="margin: 8px 0;"><strong>📸 Source:</strong> {item['source'].title()}</p>
            {f"<p style='margin: 8px 0;'><strong>📝 Description:</strong> {item.get('description', 'No description available')}</p>" if item.get('description') else ""}
            <p style="font-size: 0.85rem; color: #666; margin: 8px 0;">
                <strong>🕒 Added:</strong> {formatted_time}
            </p>
        </div>
        """, unsafe_allow_html=True)

# Show dependency status
if not torch_available or not transformers_available:
    st.markdown(f"""
    <div class="warning-message">
        <h4>⚠️ AI Model Dependencies Missing</h4>
        <p>Some AI features may not work due to missing dependencies:</p>
        <ul>
            <li>PyTorch: {"✅ Available" if torch_available else "❌ Missing"}</li>
            <li>Transformers: {"✅ Available" if transformers_available else "❌ Missing"}</li>
        </ul>
        <p>To enable AI features, add these to your requirements.txt:</p>
        <code>
        torch<br>
        transformers<br>
        </code>
        <p>The app will continue to work without AI features.</p>
    </div>
    """, unsafe_allow_html=True)

# Authentication UI
if not st.session_state.authenticated:
    st.markdown(f"""
    <div class="main-header">
        <h1>{get_text('app_title')}</h1>
        <h3>{get_text('app_subtitle')}</h3>
        <p>{get_text('tagline')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs([f"🔐 {get_text('login')}", f"📝 {get_text('register')}"])
        
        with tab1:
            st.markdown(f"### 👋 {get_text('welcome_back')}")
            username = st.text_input(get_text('username'), key="login_username")
            password = st.text_input(get_text('password'), type="password", key="login_password")
            
            if st.button(f"🚀 {get_text('login_btn')}", key="login_btn"):
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning(get_text('fill_all_fields'))
        
        with tab2:
            st.markdown(f"### 🌟 {get_text('join_community')}")
            new_username = st.text_input(get_text('username'), key="reg_username")
            new_password = st.text_input(get_text('password'), type="password", key="reg_password")
            region_placeholder = "ఉదా: గుంటూరు, వరంగల్, హైదరాబాద్..." if st.session_state.language == 'telugu' else "e.g., Guntur, Warangal, Hyderabad..."
            user_region = st.text_input(
                get_text('region'),
                placeholder=region_placeholder,
                key="reg_region"
            )
            
            if st.button(f"✨ {get_text('register_btn')}", key="register_btn"):
                if new_username and new_password and user_region:
                    success, message = register_user(new_username, new_password, user_region)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning(get_text('fill_all_fields'))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# Main app (authenticated users only)
users = load_users()
user_info = users.get(st.session_state.username, {})

# Sidebar navigation
st.sidebar.markdown(f"## 🧭 {get_text('navigation')}")
st.sidebar.markdown(f"**👋 {get_text('hello')}, {st.session_state.username}!**")
st.sidebar.markdown(f"📍 **Region:** {user_info.get('region', 'Unknown')}")

if st.sidebar.button(f"🏠 {get_text('home')}", key="nav_home"):
    set_page("home")

if st.sidebar.button(f"🔍 {get_text('identify')}", key="nav_identify"):
    set_page("identify")

if st.sidebar.button(f"📤 {get_text('upload')}", key="nav_upload"):
    set_page("upload")

if st.sidebar.button(f"🌍 {get_text('explore')}", key="nav_explore"):
    set_page("explore")

if st.sidebar.button(f"🖼️ {get_text('browse')}", key="nav_browse"):
    set_page("browse")

if st.sidebar.button(f"🚪 {get_text('logout')}", key="logout_btn"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

st.sidebar.markdown("---")

# User stats in sidebar
user_submissions = len([s for s in st.session_state.submissions if s.get('username') == st.session_state.username])
user_uploads = len([u for u in st.session_state.uploads if u.get('username') == st.session_state.username])

st.sidebar.markdown(f"""
<div class="stats-card">
    <h4>📊 {get_text('your_stats')}</h4>
    <p>🔍 {get_text('identifications')}: {user_submissions}</p>
    <p>📤 {get_text('uploads')}: {user_uploads}</p>
</div>
""", unsafe_allow_html=True)

# Main content area based on current page
if st.session_state.current_page == "home":
    # Home page content
    st.markdown(f"""
    <div class="main-header">
        <h1>{get_text('app_title')}</h1>
        <h3>{get_text('app_subtitle')}</h3>
        <p>{get_text('tagline')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <h3>🎯 {get_text('our_mission')}</h3>
            <p>{get_text('mission_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="feature-card">
            <h3>🧠 {get_text('ai_power')}</h3>
            <p>{get_text('ai_desc')}</p>
            <p style="font-size: 0.9rem; color: #666;">
                {"✅ AI Available" if torch_available and transformers_available else "⚠️ Limited AI (Dependencies Missing)"}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <h3>🏛️ {get_text('preserve_dialects')}</h3>
            <p>{get_text('preserve_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="feature-card">
            <h3>👥 {get_text('community_data')}</h3>
            <p>{get_text('community_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown(f"""
    <div class="category-header">
        <h2>{get_text('how_it_works')}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"🔍 {get_text('identify_objects')}", key="home_identify"):
            set_page("identify")
            st.rerun()
        st.markdown(f"<p style='text-align: center;'>{get_text('identify_desc')}</p>", unsafe_allow_html=True)
    
    with col2:
        if st.button(f"📤 {get_text('upload_image')}", key="home_upload"):
            set_page("upload")
            st.rerun()
        st.markdown(f"<p style='text-align: center;'>Upload your own images to expand our collection!</p>", unsafe_allow_html=True)
    
    with col3:
        if st.button(f"🖼️ {get_text('browse_images')}", key="home_browse"):
            set_page("browse")
            st.rerun()
        st.markdown(f"<p style='text-align: center;'>{get_text('learn_from_others')}</p>", unsafe_allow_html=True)
    
    with col4:
        if st.button(f"🌍 {get_text('explore_data')}", key="home_explore"):
            set_page("explore")
            st.rerun()
        st.markdown(f"<p style='text-align: center;'>View statistics and analytics!</p>", unsafe_allow_html=True)
    
    # Recent activity preview
    st.markdown("---")
    st.markdown(f"### 🕒 Recent Community Activity")
    
    recent_submissions = sorted(st.session_state.submissions, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    
    if recent_submissions:
        for submission in recent_submissions:
            username = submission.get('username', 'Unknown User')
            region = submission.get('region', 'Unknown Region')
            telugu_word = submission.get('telugu_word', 'Unknown Word')
            object_type = submission.get('object_type', 'Unknown Type')
            
            st.markdown(f"""
            <div class="recent-activity">
                <strong>👤 {username}</strong> from <em>{region}</em> 
                called an object <strong>"{telugu_word}"</strong> 
                <small>(Category: {object_type})</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Be the first to contribute!")

elif st.session_state.current_page == "identify":
    st.markdown(f"# 🔍 {get_text('identify_objects')}")
    
    if not st.session_state.image_files:
        st.warning("No images found! Please upload some images first.")
        if st.button("Go to Upload"):
            set_page("upload")
            st.rerun()
        st.stop()
    
    # Image navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_image_index == 0):
            st.session_state.current_image_index = max(0, st.session_state.current_image_index - 1)
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <p>Image {st.session_state.current_image_index + 1} of {len(st.session_state.image_files)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ➡️", disabled=st.session_state.current_image_index >= len(st.session_state.image_files) - 1):
            st.session_state.current_image_index = min(len(st.session_state.image_files) - 1, st.session_state.current_image_index + 1)
            st.rerun()
    
    # Display current image
    current_image_name = st.session_state.image_files[st.session_state.current_image_index]
    image_path = f"images/{current_image_name}"
    
    try:
        image = Image.open(image_path)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption=f"What is this object called in your dialect?", use_container_width=True)
    except FileNotFoundError:
        st.error(f"Image not found: {current_image_name}")
        st.stop()
    
    # Show existing names for this image if available
    existing_names = [s for s in st.session_state.submissions if s.get('image_name') == current_image_name]
    if existing_names:
        st.markdown("### 🏷️ Existing Names for This Object:")
        for name_entry in existing_names[-3:]:  # Show last 3 entries
            st.markdown(f"""
            <div class="word-comparison">
                <strong>{name_entry['telugu_word']}</strong> - 
                <em>{name_entry['region']}</em> by {name_entry['username']}
            </div>
            """, unsafe_allow_html=True)
    
    # AI Caption Generation
    if torch_available and transformers_available:
        st.markdown(f"""
        <div class="category-header">
            <h3>🤖 {get_text('ai_caption')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🧠 Generate AI Description"):
            if load_ai_models():
                with st.spinner("🤖 AI is analyzing the image..."):
                    try:
                        caption = generate_image_caption(image)
                        st.markdown(f"""
                        <div class="success-message">
                            <strong>AI Description:</strong> {caption}
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating caption: {str(e)}")
    else:
        st.markdown(f"""
        <div class="warning-message">
            <h4>⚠️ AI Features Unavailable</h4>
            <p>AI image description is not available due to missing dependencies. The identification feature still works!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dialect input form
    st.markdown(f"""
    <div class="dialect-input">
        <h3>🏷️ {get_text('your_dialect_word')}</h3>
        <p>{get_text('what_call_object')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("dialect_form"):
        telugu_word = st.text_input(
            get_text('your_dialect_word'),
            placeholder="ఉదా: గిన్నె, కలశం, దీపం..." if st.session_state.language == 'telugu' else "e.g., pot, vessel, lamp...",
            key=f"telugu_word_{st.session_state.current_image_index}"
        )
        
        object_type = st.text_input(
            get_text('object_type'),
            placeholder=get_text('type_placeholder'),
            key=f"object_type_{st.session_state.current_image_index}"
        )
        
        submitted = st.form_submit_button(f"💾 {get_text('submit')}")
        
        if submitted and telugu_word.strip():
            # Save submission
            new_submission = {
                "id": str(uuid.uuid4()),
                "username": st.session_state.username,
                "region": user_info.get('region', 'Unknown'),
                "image_name": current_image_name,
                "telugu_word": telugu_word.strip(),
                "object_type": object_type.strip(),
                "timestamp": datetime.now().isoformat()
            }
            
            st.session_state.submissions.append(new_submission)
            save_submissions(st.session_state.submissions)
            
            # Update user submission count
            users[st.session_state.username]["submissions"] = users[st.session_state.username].get("submissions", 0) + 1
            save_users(users)
            
            st.markdown(f"""
            <div class="success-message">
                🎉 {get_text('successfully_saved')}
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-move to next image
            if st.session_state.current_image_index < len(st.session_state.image_files) - 1:
                st.session_state.current_image_index += 1
                st.rerun()

elif st.session_state.current_page == "upload":
    st.markdown(f"# 📤 {get_text('upload_image')}")
    
    st.markdown(f"""
    <div class="feature-card">
        <h3>📸 Upload Your Own Images</h3>
        <p>Help expand our collection by uploading images of objects with unique Telugu names!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Choose input method
    upload_method = st.radio(
        "Choose how to add an image:",
        ["📁 Upload from device", "📸 Take photo with camera"],
        horizontal=True
    )
    
    uploaded_file = None
    camera_image = None
    
    if upload_method == "📁 Upload from device":
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['png', 'jpg', 'jpeg'],
            help="Upload clear images of objects with interesting Telugu names"
        )
    else:
        st.markdown("### 📸 Camera Capture")
        camera_image = st.camera_input(
            "Take a photo of an object",
            help="Make sure the object is clearly visible and well-lit"
        )
    
    # Use whichever image source is available
    image_source = uploaded_file or camera_image
    
    if image_source is not None:
        # Display the image
        image = Image.open(image_source)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            caption_text = "Uploaded Image" if uploaded_file else "Captured Photo"
            st.image(image, caption=caption_text, use_container_width=True)
        
        # Form to add details
        with st.form("upload_form"):
            st.markdown("### Add Details")
            
            image_name = st.text_input("Image Name (optional)", placeholder="e.g., Traditional Pot")
            description = st.text_area("Description (optional)", placeholder="Brief description of the object...")
            
            col1, col2 = st.columns(2)
            with col1:
                telugu_name = st.text_input(
                    "Telugu Name",
                    placeholder="ఈ వస్తువు యొక్క తెలుగు పేరు..."
                )
            
            with col2:
                category = st.selectbox(
                    "Category",
                    ["Kitchen Items", "Religious Objects", "Tools", "Decorative Items", "Household Items", "Traditional Items", "Other"]
                )
            
            upload_submitted = st.form_submit_button("📤 Upload Image")
            
            if upload_submitted:
                # Save image with appropriate method
                if uploaded_file:
                    saved_filename = save_uploaded_image(uploaded_file)
                    original_name = uploaded_file.name
                else:
                    # Handle camera image
                    saved_filename = save_camera_image(camera_image)
                    original_name = f"camera_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                
                if saved_filename:
                    # Save upload details
                    new_upload = {
                        "id": str(uuid.uuid4()),
                        "username": st.session_state.username,
                        "region": user_info.get('region', 'Unknown'),
                        "filename": saved_filename,
                        "original_name": original_name,
                        "image_name": image_name or original_name,
                        "description": description,
                        "telugu_name": telugu_name,
                        "category": category,
                        "source": "upload" if uploaded_file else "camera",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    st.session_state.uploads.append(new_upload)
                    save_uploads(st.session_state.uploads)
                    
                    st.markdown(f"""
                    <div class="success-message">
                        🎉 {get_text('object_uploaded')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Refresh image files list
                    st.session_state.image_files = load_images_from_folder()
                    
                    st.balloons()
    else:
        # Show instructions based on selected method
        if upload_method == "📁 Upload from device":
            st.info("👆 Click 'Browse files' above to select an image from your device")
        else:
            st.info("📸 Click 'Take Photo' above to capture an image using your camera")
    
    # Tips section
    st.markdown("""
    <div class="feature-card">
        <h4>📝 Tips for Great Photos:</h4>
        <ul>
            <li>🔆 Ensure good lighting</li>
            <li>🎯 Focus on the main object</li>
            <li>📐 Keep the object centered</li>
            <li>🔍 Make sure text/details are readable</li>
            <li>🌟 Capture unique or traditional items</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
elif st.session_state.current_page == "explore":
    st.markdown(f"# 🌍 {get_text('explore_data')}")
    
    # Overview statistics
    total_submissions = len(st.session_state.submissions)
    total_uploads = len(st.session_state.uploads)
    total_users = len(users)
    unique_regions = len(set([s.get('region', 'Unknown') for s in st.session_state.submissions] + 
                            [u.get('region', 'Unknown') for u in st.session_state.uploads]))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📊</h3>
            <h2>{total_submissions}</h2>
            <p>{get_text('identifications')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📤</h3>
            <h2>{total_uploads}</h2>
            <p>{get_text('uploads')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <h3>🌍</h3>
            <h2>{unique_regions}</h2>
            <p>{get_text('regions')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3>👥</h3>
            <h2>{total_users}</h2>
            <p>{get_text('members')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if total_submissions > 0 or total_uploads > 0:
        # Regional distribution
        st.markdown(f"""
        <div class="category-header">
            <h3>📍 {get_text('by_region')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Count submissions by region
        region_counts = {}
        for submission in st.session_state.submissions:
            region = submission.get('region', 'Unknown')
            region_counts[region] = region_counts.get(region, 0) + 1
        
        for upload in st.session_state.uploads:
            region = upload.get('region', 'Unknown')
            region_counts[region] = region_counts.get(region, 0) + 1
        
        if region_counts:
            # Create a simple bar chart representation
            max_count = max(region_counts.values())
            for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                bar_width = (count / max_count) * 100
                st.markdown(f"""
                <div class="feature-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>📍 {region}</strong>
                        <span>{count} contributions</span>
                    </div>
                    <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 8px;">
                        <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: {bar_width}%; transition: width 0.5s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Object type distribution
        st.markdown(f"""
        <div class="category-header">
            <h3>🏷️ {get_text('by_object_type')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        type_counts = {}
        for submission in st.session_state.submissions:
            obj_type = submission.get('object_type', 'Uncategorized')
            if obj_type:
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        for upload in st.session_state.uploads:
            obj_type = upload.get('category', 'Uncategorized')
            if obj_type:
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        if type_counts:
            max_count = max(type_counts.values())
            for obj_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                bar_width = (count / max_count) * 100
                st.markdown(f"""
                <div class="feature-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>🏷️ {obj_type}</strong>
                        <span>{count} items</span>
                    </div>
                    <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; margin-top: 8px;">
                        <div style="background: linear-gradient(90deg, #4ECDC4, #44A08D); height: 100%; width: {bar_width}%; transition: width 0.5s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Top contributors
        st.markdown(f"""
        <div class="category-header">
            <h3>🌟 {get_text('member_contributions')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        contributor_counts = {}
        for submission in st.session_state.submissions:
            username = submission.get('username', 'Unknown')
            contributor_counts[username] = contributor_counts.get(username, 0) + 1
        
        for upload in st.session_state.uploads:
            username = upload.get('username', 'Unknown')
            contributor_counts[username] = contributor_counts.get(username, 0) + 1
        
        if contributor_counts:
            top_contributors = sorted(contributor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for i, (username, count) in enumerate(top_contributors):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🏅"
                user_region = users.get(username, {}).get('region', 'Unknown Region')
                
                st.markdown(f"""
                <div class="feature-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{medal} {username}</strong>
                            <br><small>📍 {user_region}</small>
                        </div>
                        <span style="font-size: 1.2rem; font-weight: bold; color: #667eea;">{count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.info("No data available yet. Start contributing to see analytics!")

elif st.session_state.current_page == "browse":
    st.markdown(f"# 🖼️ {get_text('browse_images')}")
    
    # Get all browse data
    browse_data = get_browse_data()
    
    if not browse_data:
        st.info("No images to browse yet. Upload some images or start identifying objects!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Start Identifying"):
                set_page("identify")
                st.rerun()
        with col2:
            if st.button("📤 Upload Image"):
                set_page("upload")
                st.rerun()
        st.stop()
    
    # Filters
    st.markdown(f"""
    <div class="filter-section">
        <h4>🔍 Filter Images</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Region filter
        all_regions = sorted(set([item.get('region', 'Unknown') for item in browse_data]))
        selected_regions = st.multiselect(
            "📍 Filter by Region",
            options=all_regions,
            default=all_regions,
            key="region_filter"
        )
    
    with col2:
        # Object type filter
        all_types = sorted(set([item.get('object_type', 'Uncategorized') for item in browse_data]))
        selected_types = st.multiselect(
            "🏷️ Filter by Type",
            options=all_types,
            default=all_types,
            key="type_filter"
        )
    
    with col3:
        # Source filter
        source_options = ['identification', 'upload', 'camera']
        selected_sources = st.multiselect(
            "📸 Filter by Source",
            options=source_options,
            default=source_options,
            key="source_filter"
        )
    
    with col4:
        # Search by Telugu word
        search_term = st.text_input(
            "🔍 Search Telugu Word",
            placeholder="తెలుగు పదం వెతకండి...",
            key="search_filter"
        )
    
    # Apply filters
    filtered_data = browse_data
    
    if selected_regions:
        filtered_data = [item for item in filtered_data if item.get('region') in selected_regions]
    
    if selected_types:
        filtered_data = [item for item in filtered_data if item.get('object_type') in selected_types]
    
    if selected_sources:
        filtered_data = [item for item in filtered_data if item.get('source') in selected_sources]
    
    if search_term:
        filtered_data = [item for item in filtered_data 
                        if search_term.lower() in item.get('telugu_word', '').lower()]
    
    # Sort options
    sort_option = st.selectbox(
        "🔄 Sort by",
        ["Latest First", "Oldest First", "A-Z (Telugu)", "Z-A (Telugu)", "Region", "Type"],
        key="sort_option"
    )
    
    if sort_option == "Latest First":
        filtered_data = sorted(filtered_data, key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_option == "Oldest First":
        filtered_data = sorted(filtered_data, key=lambda x: x.get('timestamp', ''))
    elif sort_option == "A-Z (Telugu)":
        filtered_data = sorted(filtered_data, key=lambda x: x.get('telugu_word', ''))
    elif sort_option == "Z-A (Telugu)":
        filtered_data = sorted(filtered_data, key=lambda x: x.get('telugu_word', ''), reverse=True)
    elif sort_option == "Region":
        filtered_data = sorted(filtered_data, key=lambda x: x.get('region', ''))
    elif sort_option == "Type":
        filtered_data = sorted(filtered_data, key=lambda x: x.get('object_type', ''))
    
    # Display results
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <h3>Found {len(filtered_data)} images</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if filtered_data:
        # Pagination
        items_per_page = 10
        total_pages = (len(filtered_data) - 1) // items_per_page + 1
        
        if 'browse_page' not in st.session_state:
            st.session_state.browse_page = 1
        
        # Page navigation
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.browse_page <= 1):
                    st.session_state.browse_page -= 1
                    st.rerun()
            
            with col2:
                if st.button("⏮️ First", disabled=st.session_state.browse_page <= 1):
                    st.session_state.browse_page = 1
                    st.rerun()
            
            with col3:
                st.markdown(f"""
                <div style="text-align: center; padding: 5px;">
                    Page {st.session_state.browse_page} of {total_pages}
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if st.button("⏭️ Last", disabled=st.session_state.browse_page >= total_pages):
                    st.session_state.browse_page = total_pages
                    st.rerun()
            
            with col5:
                if st.button("Next ➡️", disabled=st.session_state.browse_page >= total_pages):
                    st.session_state.browse_page += 1
                    st.rerun()
        
        # Calculate slice for current page
        start_idx = (st.session_state.browse_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = filtered_data[start_idx:end_idx]
        
        # Display items
        for item in page_items:
            with st.container():
                display_browse_card(item)
                st.markdown("---")
    
    else:
        st.info("No images match your filters. Try adjusting the filter criteria.")
    
    # Quick stats for current view
    if filtered_data:
        st.markdown("### 📊 Current View Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            unique_regions_filtered = len(set([item.get('region') for item in filtered_data]))
            st.metric("Regions", unique_regions_filtered)
        
        with col2:
            unique_types_filtered = len(set([item.get('object_type') for item in filtered_data]))
            st.metric("Object Types", unique_types_filtered)
        
        with col3:
            unique_contributors = len(set([item.get('username') for item in filtered_data]))
            st.metric("Contributors", unique_contributors)

# Bottom credits and info
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 20px;">
    <p>🏛️ తెలుగు లెన్స్ - Preserving Telugu Heritage Through Technology</p>
    <p>Made with ❤️ for the Telugu community | Current Language: {'తెలుగు' if st.session_state.language == 'telugu' else 'English'}</p>
    <p>Total Images: {len(st.session_state.image_files)} | Total Contributions: {len(st.session_state.submissions) + len(st.session_state.uploads)}</p>
</div>
""", unsafe_allow_html=True)

# Debug information (only show in development)
if st.sidebar.checkbox("🔧 Debug Info", value=False):
    with st.sidebar.expander("Debug Information"):
        st.write("Current Page:", st.session_state.current_page)
        st.write("Language:", st.session_state.language)
        st.write("User:", st.session_state.username)
        st.write("Image Files Count:", len(st.session_state.image_files))
        st.write("Submissions Count:", len(st.session_state.submissions))
        st.write("Uploads Count:", len(st.session_state.uploads))
        st.write("AI Model Loaded:", st.session_state.ai_model_loaded)
        st.write("PyTorch Available:", torch_available)
        st.write("Transformers Available:", transformers_available)

# Auto-refresh data periodically (every 60 seconds)
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

current_time = datetime.now()
if (current_time - st.session_state.last_refresh).seconds > 60:
    # Refresh data from files
    st.session_state.submissions = load_submissions()
    st.session_state.uploads = load_uploads()
    st.session_state.image_files = load_images_from_folder()
    st.session_state.last_refresh = current_time

