import streamlit as st
import pandas as pd
from PIL import Image
import json
import os
from datetime import datetime
import numpy as np
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import glob
import hashlib
import uuid

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
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
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
    }
    
    .browse-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
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
    
    if not image_files:
        return ["sample_pot.jpg", "sample_spoon.jpg", "sample_lamp.jpg"]
    
    return sorted([os.path.basename(f) for f in image_files])

# Initialize image files
if not st.session_state.image_files:
    st.session_state.image_files = load_images_from_folder()

# BLIP Image Captioning Function
@st.cache_resource
def load_blip_model():
    """Load BLIP model and processor"""
    try:
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        return processor, model
    except Exception as e:
        st.error(f"Error loading BLIP model: {str(e)}")
        return None, None

def generate_image_caption(image):
    """Generate caption using BLIP model"""
    if st.session_state.blip_processor is None or st.session_state.blip_model is None:
        processor, model = load_blip_model()
        if processor is None or model is None:
            return "Error: Could not load BLIP model"
        st.session_state.blip_processor = processor
        st.session_state.blip_model = model
    
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        inputs = st.session_state.blip_processor(image, return_tensors="pt")
        
        with torch.no_grad():
            out = st.session_state.blip_model.generate(**inputs, max_length=50, num_beams=5)
        
        caption = st.session_state.blip_processor.decode(out[0], skip_special_tokens=True)
        return caption
        
    except Exception as e:
        return f"Error generating caption: {str(e)}"

def calculate_semantic_similarity(telugu_text, english_caption):
    """Mock function for semantic similarity"""
    return np.random.uniform(0.3, 0.95)

def load_ai_models():
    """Load AI models"""
    if not st.session_state.ai_model_loaded:
        loading_msg = "🤖 మా AI మోడల్‌ను లోడ్ చేస్తున్నాము..." if st.session_state.language == 'telugu' else "🤖 Loading our magical AI brain..."
        success_msg = "✅ AI మోడల్ విజయవంతంగా లోడ్ అయ్యింది!" if st.session_state.language == 'telugu' else "✅ Model loaded successfully!"
        info_msg = "💡 తదుపరిసారి మరింత వేగంగా లోడ్ అవుతుంది!" if st.session_state.language == 'telugu' else "💡 Will load faster next time!"
        error_msg = "❌ AI మోడల్ లోడ్ కాలేదు." if st.session_state.language == 'telugu' else "❌ Failed to load AI model."
        
        with st.spinner(loading_msg):
            processor, model = load_blip_model()
            if processor is not None and model is not None:
                st.session_state.blip_processor = processor
                st.session_state.blip_model = model
                st.session_state.ai_model_loaded = True
                st.success(success_msg)
                st.info(info_msg)
            else:
                st.error(error_msg)
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

elif st.session_state.current_page == "browse":
    st.markdown(f"# 🖼️ {get_text('browse_contributions')}")
    st.markdown(f"### {get_text('learn_from_others')} - Discover how different regions name objects!")
    
    # Get browse data
    browse_data = get_browse_data()
    
    if not browse_data:
        st.info("No contributions yet! Be the first to add some objects and their Telugu names.")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Start Identifying Objects"):
                set_page("identify")
                st.rerun()
        with col2:
            if st.button("📤 Upload Your Images"):
                set_page("upload")
                st.rerun()
        st.stop()
    
    # Filter section
    st.markdown("""
    <div class="filter-section">
        <h4>🔧 Filter & Search Options</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Get all unique regions
        all_regions = sorted(set([item['region'] for item in browse_data if item['region'] != 'Unknown']))
        region_filter = st.selectbox(
            "🌍 Filter by Region",
            ["All Regions"] + all_regions,
            key="browse_region_filter"
        )
    
    with col2:
        # Get all unique object types
        all_types = sorted(set([item['object_type'] for item in browse_data if item['object_type'] not in ['Uncategorized', '']]))
        type_filter = st.selectbox(
            "🏷️ Filter by Type",
            ["All Types"] + all_types,
            key="browse_type_filter"
        )
    
    with col3:
        # Get all unique contributors
        all_contributors = sorted(set([item['username'] for item in browse_data if item['username'] != 'Anonymous']))
        user_filter = st.selectbox(
            "👤 Filter by User",
            ["All Users"] + all_contributors,
            key="browse_user_filter"
        )
    
    with col4:
        # Search by Telugu word
        search_term = st.text_input(
            "🔍 Search Telugu Words",
            placeholder="ముద్ద, గిన్నె, లాంప్...",
            key="browse_search"
        )
    
    # View mode selection
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        view_mode = st.radio(
            "📋 View Mode:",
            ["📱 Gallery View", "📝 List View", "🔍 Comparison View", "🌟 Learning Mode"],
            horizontal=True,
            key="browse_view_mode"
        )
    
    with col2:
        sort_option = st.selectbox(
            "📊 Sort by:",
            ["Newest First", "Oldest First", "A-Z (Telugu)", "Z-A (Telugu)", "By Region"],
            key="browse_sort"
        )
    
    # Apply filters
    filtered_data = browse_data
    
    if region_filter != "All Regions":
        filtered_data = [item for item in filtered_data if item['region'] == region_filter]
    
    if type_filter != "All Types":
        filtered_data = [item for item in filtered_data if item['object_type'] == type_filter]
    
    # Continue from the filter section in browse page
    if user_filter != "All Users":
        filtered_data = [item for item in filtered_data if item['username'] == user_filter]
    
    if search_term:
        filtered_data = [item for item in filtered_data if search_term.lower() in item['telugu_word'].lower()]
    
    # Apply sorting
    if sort_option == "Newest First":
        filtered_data = sorted(filtered_data, key=lambda x: x['timestamp'], reverse=True)
    elif sort_option == "Oldest First":
        filtered_data = sorted(filtered_data, key=lambda x: x['timestamp'])
    elif sort_option == "A-Z (Telugu)":
        filtered_data = sorted(filtered_data, key=lambda x: x['telugu_word'])
    elif sort_option == "Z-A (Telugu)":
        filtered_data = sorted(filtered_data, key=lambda x: x['telugu_word'], reverse=True)
    elif sort_option == "By Region":
        filtered_data = sorted(filtered_data, key=lambda x: x['region'])
    
    # Display results count
    st.markdown(f"**📊 Showing {len(filtered_data)} of {len(browse_data)} contributions**")
    
    if not filtered_data:
        st.warning("No items match your current filters. Try adjusting your search criteria.")
        st.stop()
    
    # Display content based on view mode
    if view_mode == "📱 Gallery View":
        # Gallery view with cards
        items_per_page = 12
        total_pages = (len(filtered_data) + items_per_page - 1) // items_per_page
        
        if 'browse_page' not in st.session_state:
            st.session_state.browse_page = 0
        
        # Pagination controls
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("⬅️ Previous", disabled=st.session_state.browse_page == 0):
                    st.session_state.browse_page = max(0, st.session_state.browse_page - 1)
                    st.rerun()
            
            with col3:
                st.markdown(f"**Page {st.session_state.browse_page + 1} of {total_pages}**")
            
            with col5:
                if st.button("Next ➡️", disabled=st.session_state.browse_page >= total_pages - 1):
                    st.session_state.browse_page = min(total_pages - 1, st.session_state.browse_page + 1)
                    st.rerun()
        
        # Display items for current page
        start_idx = st.session_state.browse_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_data))
        page_items = filtered_data[start_idx:end_idx]
        
        # Display in 3 columns
        for i in range(0, len(page_items), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(page_items):
                    with col:
                        display_browse_card(page_items[i + j])
    
    elif view_mode == "📝 List View":
        # List view with compact display
        for item in filtered_data[:50]:  # Limit to 50 items for performance
            col1, col2 = st.columns([1, 4])
            
            with col1:
                try:
                    image = Image.open(f"images/{item['image_name']}")
                    st.image(image, use_container_width=True)
                except:
                    st.markdown("🖼️ *No image*")
            
            with col2:
                st.markdown(f"""
                **🏷️ {item['telugu_word']}** | 
                📍 {item['region']} | 
                🏷️ {item['object_type']} | 
                👤 {item['username']}
                """)
                
                # Format timestamp
                try:
                    formatted_time = pd.to_datetime(item['timestamp']).strftime('%Y-%m-%d %H:%M')
                    st.caption(f"🕒 Added: {formatted_time}")
                except:
                    st.caption("🕒 Added: Unknown time")
            
            st.markdown("---")
    
    elif view_mode == "🔍 Comparison View":
        # Group by image to show different names for same object
        st.markdown("### 🔍 See how different regions name the same objects:")
        
        # Group items by image
        image_groups = {}
        for item in filtered_data:
            image_name = item['image_name']
            if image_name not in image_groups:
                image_groups[image_name] = []
            image_groups[image_name].append(item)
        
        # Show only images with multiple names
        multi_name_images = {k: v for k, v in image_groups.items() if len(v) > 1}
        
        if not multi_name_images:
            st.info("No objects with multiple names found in current filters. Try broadening your search!")
        else:
            for image_name, items in list(multi_name_images.items())[:10]:  # Limit to 10 for performance
                st.markdown(f"""
                <div class="comparison-section">
                    <h4>🖼️ Different names for the same object:</h4>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    try:
                        image = Image.open(f"images/{image_name}")
                        st.image(image, use_container_width=True)
                    except:
                        st.markdown("🖼️ *Image not available*")
                
                with col2:
                    for item in items:
                        st.markdown(f"""
                        <div class="word-comparison">
                            <strong>🏷️ {item['telugu_word']}</strong><br>
                            📍 Region: {item['region']}<br>
                            👤 By: {item['username']}<br>
                            🏷️ Type: {item['object_type']}
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
    
    elif view_mode == "🌟 Learning Mode":
        # Interactive learning mode with random objects
        st.markdown("### 🌟 Learning Mode: Test Your Knowledge!")
        
        if st.button("🎲 Show Random Object"):
            st.session_state.learning_item = np.random.choice(filtered_data)
            st.rerun()
        
        if hasattr(st.session_state, 'learning_item'):
            item = st.session_state.learning_item
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                try:
                    image = Image.open(f"images/{item['image_name']}")
                    st.image(image, caption="What do you call this in your dialect?", use_container_width=True)
                except:
                    st.markdown("🖼️ *Image not available*")
            
            with col2:
                st.markdown("### 🤔 Think about it...")
                
                if st.button("🔍 Show Answer"):
                    st.markdown(f"""
                    <div class="success-message">
                        <h4>Answer:</h4>
                        <p><strong>🏷️ Telugu Name:</strong> {item['telugu_word']}</p>
                        <p><strong>📍 Region:</strong> {item['region']}</p>
                        <p><strong>🏷️ Category:</strong> {item['object_type']}</p>
                        <p><strong>👤 Contributed by:</strong> {item['username']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show similar objects
                similar_objects = [i for i in filtered_data if i['object_type'] == item['object_type'] and i['id'] != item['id']]
                if similar_objects:
                    st.markdown("#### 🔗 Similar Objects:")
                    for similar in similar_objects[:3]:
                        st.markdown(f"• **{similar['telugu_word']}** ({similar['region']})")

elif st.session_state.current_page == "explore":
    st.markdown(f"# 🌍 {get_text('explore_data')}")
    st.markdown("### Discover insights from our community contributions!")
    
    # Load data for analysis
    submissions = st.session_state.submissions
    uploads = st.session_state.uploads
    users = load_users()
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_identifications = len(submissions)
        st.markdown(f"""
        <div class="stats-card">
            <h2>{total_identifications}</h2>
            <p>🔍 Total Identifications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_uploads = len(uploads)
        st.markdown(f"""
        <div class="stats-card">
            <h2>{total_uploads}</h2>
            <p>📤 Images Uploaded</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_regions = len(set([s.get('region', 'Unknown') for s in submissions] + [u.get('region', 'Unknown') for u in uploads]))
        st.markdown(f"""
        <div class="stats-card">
            <h2>{unique_regions}</h2>
            <p>🌍 {get_text('regions')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_users = len(users)
        st.markdown(f"""
        <div class="stats-card">
            <h2>{total_users}</h2>
            <p>👥 {get_text('members')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts and visualizations
    st.markdown("---")
    
    if submissions:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="category-header">
                <h4>📊 {get_text('by_region')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Create region distribution
            region_counts = {}
            for submission in submissions:
                region = submission.get('region', 'Unknown')
                region_counts[region] = region_counts.get(region, 0) + 1
            
            if region_counts:
                regions_df = pd.DataFrame(list(region_counts.items()), columns=['Region', 'Count'])
                st.bar_chart(regions_df.set_index('Region'))
                
                # Show top regions
                sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
                st.markdown("**🏆 Top Contributing Regions:**")
                for i, (region, count) in enumerate(sorted_regions[:5], 1):
                    st.markdown(f"{i}. **{region}**: {count} contributions")
        
        with col2:
            st.markdown(f"""
            <div class="category-header">
                <h4>🏷️ {get_text('by_object_type')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Create object type distribution
            type_counts = {}
            for submission in submissions:
                obj_type = submission.get('object_type', 'Uncategorized')
                if obj_type.strip():
                    type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
            
            if type_counts:
                types_df = pd.DataFrame(list(type_counts.items()), columns=['Object Type', 'Count'])
                st.bar_chart(types_df.set_index('Object Type'))
                
                # Show top categories
                sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
                st.markdown("**🏆 Popular Object Categories:**")
                for i, (obj_type, count) in enumerate(sorted_types[:5], 1):
                    st.markdown(f"{i}. **{obj_type}**: {count} items")
    
    # Member contributions leaderboard
    st.markdown("---")
    st.markdown(f"""
    <div class="category-header">
        <h4>🏆 {get_text('member_contributions')}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate user contributions
    user_contributions = {}
    for submission in submissions:
        username = submission.get('username', 'Anonymous')
        if username != 'Anonymous':
            user_contributions[username] = user_contributions.get(username, 0) + 1
    
    for upload in uploads:
        username = upload.get('username', 'Anonymous')
        if username != 'Anonymous':
            user_contributions[username] = user_contributions.get(username, 0) + 1
    
    if user_contributions:
        sorted_contributors = sorted(user_contributions.items(), key=lambda x: x[1], reverse=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥇 Top Contributors")
            for i, (username, count) in enumerate(sorted_contributors[:10], 1):
                user_region = users.get(username, {}).get('region', 'Unknown')
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f"{medal} **{username}** ({user_region}): {count} contributions")
        
        with col2:
            st.markdown("### 📈 Contribution Timeline")
            # Create timeline of contributions
            daily_contributions = {}
            
            for submission in submissions:
                try:
                    date = pd.to_datetime(submission.get('timestamp', '')).date()
                    daily_contributions[date] = daily_contributions.get(date, 0) + 1
                except:
                    continue
            
            if daily_contributions:
                timeline_df = pd.DataFrame(list(daily_contributions.items()), columns=['Date', 'Contributions'])
                timeline_df = timeline_df.sort_values('Date')
                st.line_chart(timeline_df.set_index('Date'))
    
    # Regional comparison
    st.markdown("---")
    st.markdown("### 🗺️ Regional Word Variations")
    
    # Find objects with multiple regional names
    object_variations = {}
    for submission in submissions:
        image_name = submission.get('image_name', '')
        region = submission.get('region', 'Unknown')
        telugu_word = submission.get('telugu_word', '')
        
        if image_name and telugu_word:
            if image_name not in object_variations:
                object_variations[image_name] = {}
            object_variations[image_name][region] = telugu_word
    
    # Show objects with multiple regional names
    multi_regional_objects = {k: v for k, v in object_variations.items() if len(v) > 1}
    
    if multi_regional_objects:
        st.markdown("**🔍 Objects with Regional Variations:**")
        
        for i, (image_name, variations) in enumerate(list(multi_regional_objects.items())[:5], 1):
            with st.expander(f"Object #{i} - {len(variations)} regional names"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    try:
                        image = Image.open(f"images/{image_name}")
                        st.image(image, use_container_width=True)
                    except:
                        st.markdown("🖼️ *Image not available*")
                
                with col2:
                    st.markdown("**Regional Names:**")
                    for region, word in variations.items():
                        st.markdown(f"• **{region}**: {word}")
    else:
        st.info("No regional variations found yet. More contributions will reveal interesting dialect differences!")
    
    # Activity insights
    st.markdown("---")
    st.markdown("### 📊 Community Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Most active time analysis
        if submissions:
            hour_activity = {}
            for submission in submissions:
                try:
                    hour = pd.to_datetime(submission.get('timestamp', '')).hour
                    hour_activity[hour] = hour_activity.get(hour, 0) + 1
                except:
                    continue
            
            if hour_activity:
                st.markdown("**⏰ Most Active Hours:**")
                sorted_hours = sorted(hour_activity.items(), key=lambda x: x[1], reverse=True)
                for hour, count in sorted_hours[:3]:
                    time_period = "Morning" if 6 <= hour < 12 else "Afternoon" if 12 <= hour < 18 else "Evening" if 18 <= hour < 22 else "Night"
                    st.markdown(f"• **{hour}:00** ({time_period}): {count} contributions")
    
    with col2:
        # Diversity metrics
        unique_words = len(set([s.get('telugu_word', '') for s in submissions if s.get('telugu_word', '').strip()]))
        unique_objects = len(set([s.get('image_name', '') for s in submissions if s.get('image_name', '')]))
        
        st.markdown("**🌈 Diversity Metrics:**")
        st.markdown(f"• **Unique Telugu Words**: {unique_words}")
        st.markdown(f"• **Unique Objects**: {unique_objects}")
        if unique_objects > 0:
            avg_names_per_object = len(submissions) / unique_objects
            st.markdown(f"• **Avg Names per Object**: {avg_names_per_object:.1f}")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-top: 2rem;">
    <h3>🙏 Thank you for preserving Telugu heritage!</h3>
    <p>Every word you contribute helps keep our beautiful language and dialects alive for future generations.</p>
    <p><strong>మా భాషా వైభవాన్ని కాపాడుతున్న మీకు కృతజ్ఞతలు! 🌟</strong></p>
</div>
""", unsafe_allow_html=True)

# Debug information (only show in development)
if st.sidebar.checkbox("🔧 Debug Info", value=False):
    st.sidebar.markdown("### Debug Information")
    st.sidebar.write(f"Current page: {st.session_state.current_page}")
    st.sidebar.write(f"Authenticated: {st.session_state.authenticated}")
    st.sidebar.write(f"Username: {st.session_state.username}")
    st.sidebar.write(f"Language: {st.session_state.language}")
    st.sidebar.write(f"Image files: {len(st.session_state.image_files)}")
    st.sidebar.write(f"Submissions: {len(st.session_state.submissions)}")
    st.sidebar.write(f"Uploads: {len(st.session_state.uploads)}")
    st.sidebar.write(f"AI Model Loaded: {st.session_state.ai_model_loaded}")