"""
COMPLETE AI CURRICULUM GENERATOR - FULLY FIXED VERSION
========================================================
Phase 1: Imports and Configuration

Features:
- Fixed LaTeX equation rendering
- Automatic timestamped Google Drive subfolders
- Image generation prompts and upload
- Enhanced error handling
- Complete academic content generation
"""

import streamlit as st
import requests
import json
import time
import os
import re
from datetime import datetime
from io import BytesIO
from PIL import Image as PilImage

# PDF imports
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    st.warning("⚠️ PyPDF2 not installed - PDF upload disabled")

# Google Drive imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    st.warning("⚠️ Google Drive libraries not installed")

# ReportLab imports for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak,
        Table, TableStyle, Image, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    st.error("❌ ReportLab not installed - PDF generation disabled")

# DOCX imports for editable output
try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("⚠️ python-docx not installed - DOCX generation disabled")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Grok API Configuration
DEFAULT_API_KEY = "xai-6QJwG3u6540lVZyXbFBArvLQ43ZyJsrnq65pyCWhxh5zXqNvtwe6LdTURbTwvE2sA3Uxlb9gn82Vamgu"
API_URL = "https://api.x.ai/v1/chat/completions"

# Google Drive Service Account Credentials
GDRIVE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "dynamic-wording-475018-e2",
    "private_key_id": "2e97986797c2f143cc94209e0b0f97922146c958",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCJ/1wVoHvZvFvM\nxXxq1Zzd3XsC5g24nw9/TUdIvAvGsZU+6ZF9fxYScHpQzy2LpEwKYtaHmxsm/Ia8\n4eX33tcysd7K9vEWCPW1RckbNlzuLbCUHm5WU7pxhCB8AEBy2roD82RRkZvGhzgs\nBQFK4AbDEbuglT1BPej5+pSwJti4JaGjkozgum8ecvaZv3FLof5zp2/s0LDICOGB\nUVZCXvXDKetMLoZYJRm/W41T074NUXdmCCFtuyiXszNzzQa/HVy7yqo/5UxXQyRs\nZgAKSmp7EhtXkEozlBoMGhFXQHH6oIs9j4FtFKZ3w7/oLgCg2MqgX+G/1W7znaK6\n4i+vjrWTAgMBAAECggEAIzWh96yqXQxHufAbhiC5tQwpMjyjfJss95SunvrH4Gr4\nAwTSR9xws8S6GLs7yjjh4/aC+TeUjnZ5JGFY7U0QyFEE4PFv4ujnVFiZbtWIkYbb\n2ncHPQSA+iy1ox3nU8bGFnL4Ai3uOpHOvcCLK2EMqKHyJw9dATP8KSgL3wQSYK1t\nbbJQbuBec1W92//i1x2S2Ac0ppWyP379K3BiVcqPUUN83cqvklCeAdUNOfNro4o6\nSVgrAx4NF+EhnO158CNvJ70cKhY1Cyz3+ihPg2Z6UDL8RpcddrCScKYJqHp1Vsz+\nWHngLqR0InLCefcY16Pd90yFDWFlwm7xCUPjdOYAPQKBgQC9F66IHAvrLdGSz9OO\nxUuZQNPDU18/KUjO74/KNF4vSzd2Ye65rY5ai/BNeGNCUxRVyiUwlsdaEplPhEce\n7+3U0sP0NoxrOCYh0r0sBd7QpZWx5YBFsz/s3MVe10BvFaZWUOqUQHHOQRquyeEu\nCHsx2s5D86Zl6wNG9XSESV9A/wKBgQC602fqsWza40zqeqzN0YY/Bb0+LJoGSfwh\nMuWRAyhjJHGV/LomA2uLuwvLAaJ5vOOv+tCGhnQPV4s8P5NlNXDOggq7OTUBxWgG\nZxpJBop0RtV71M2/v6v/iyKpI05cc6prGRWv56oFQ3vdyB79EXBJx3epRBrW+URt\nDXgRq7b3bQKBgGAImvc9Z0A1sO4i5orn4JEgv2u/9+uYCAYw3JIRLpROWwigjCF4\n54dM8uolbiPNFdLMKz8WFIDGWV5tC8HGkL85m5N38LCzf4pGARVOle7ZacFDkXXU\np26gYQzdvTetgyDrT3ejkyjxH6ANn3NFk2uqeH9CSwwP40Yyes6EhP/5AoGAZ2Cj\nl9IlkdlErlrDVAAkcKsUVFsJv4Eg6p3nOZ6tsm5wC7aUqoQp9l/B3stAxGwo8S+w\nQ0AS6IpgmS30uYQgr6R1m7PECP7a2PAkM1RTOJQZfTP7xaah3f13aHAI5E98dVak\nEXn3MoJtAAPEYfRMVgbxx8/PqjS0EEPrtJt32uECgYEAi/8JnI8MAhq+eDcVuO45\nu/itREj4sHS/4dcTtL2mbUz8DKWyDpe6LC7/oMIl4459Ktp7MOanR/yPIvJfU8t6\ni+05OoFDvrDkXraE28wIHO0qIT1NY/htaNByBHNvs9b1Rj99O7o2sH8k8fG2OM0u\nxTEWjBaUn1bG59flELY88zk=\n-----END PRIVATE KEY-----\n",
    "client_email": "curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com",
    "client_id": "113202445348377169696",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/curriculum-generator%40dynamic-wording-475018-e2.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        # Navigation
        'step': 'syllabus_upload',
        
        # API Configuration
        'api_key': DEFAULT_API_KEY,
        
        # Course Information
        'course_title': 'Organizational Behaviour',
        'course_code': 'MBA101',
        'credits': 3,
        'target_audience': 'Postgraduate (MBA)',
        
        # Structure Configuration
        'num_units': 4,
        'sections_per_unit': 8,
        
        # Academic Mappings
        'program_objectives': '',
        'program_outcomes': '',
        'course_outcomes': '',
        'specialized_outcomes': '',
        
        # Document Customization
        'use_egyankosh_style': True,
        'document_heading': '',
        'logo': None,
        
        # Google Drive
        'gdrive_folder_url': '',
        'gdrive_folder_id': '',
        
        # Content Storage
        'content': {},
        'images': {},  # section_key: {image_data, prompt}
        'image_prompts': {},  # section_key: prompt for image generation
        
        # Generation Control
        'paused': False,
        'extracted_structure': None,
        'outline': None,
        'approved_outline': None,
        'sections_to_process': [],
        'generation_start_time': None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# Phase 1 Complete
# ============================================================================
print("Phase 1: Imports and Configuration loaded successfully")
"""
PHASE 2: HELPER FUNCTIONS
==========================
- API communication with detailed logging
- PDF extraction and syllabus parsing
- LaTeX equation handling (FIXED)
- Google Drive operations with auto-subfolder (FIXED)
- Text cleaning and formatting
"""

# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================

def get_api_headers():
    """Get API headers with current API key"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.api_key}"
    }

def make_api_call(messages, retries=3, timeout=120, max_tokens=2000):
    """
    Make API call to Grok with detailed logging and error handling
    
    Args:
        messages: List of message dicts with role and content
        retries: Number of retry attempts
        timeout: Request timeout in seconds
        max_tokens: Maximum tokens in response
        
    Returns:
        str: API response content or None if failed
    """
    headers = get_api_headers()
    
    payload = {
        "messages": messages,
        "model": "grok-2-1212",
        "stream": False,
        "temperature": 0.3,
        "max_tokens": max_tokens
    }
    
    for attempt in range(retries):
        try:
            st.write(f"🔄 API Call Attempt {attempt + 1}/{retries}")
            st.write(f"📤 Sending to: {API_URL}")
            st.write(f"🎯 Model: grok-2-1212")
            st.write(f"📊 Max tokens: {max_tokens}")
            
            # Show first 200 chars of prompt
            if messages:
                prompt_preview = messages[-1].get('content', '')[:200]
                st.write(f"📝 Prompt preview: {prompt_preview}...")
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            
            st.write(f"📡 Response Status: {response.status_code}")
            
            # Show response time
            if response.headers:
                st.write(f"⏱️ Response time: {response.elapsed.total_seconds():.2f}s")
            
            response.raise_for_status()
            result = response.json()
            
            # Detailed response analysis
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Analyze response quality
                word_count = len(content.split())
                char_count = len(content)
                has_structure = any(keyword in content.upper() for keyword in ['INTRODUCTION', 'LEARNING OBJECTIVES', 'CHECK YOUR PROGRESS'])
                has_blooms = any(keyword in content.upper() for keyword in ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE'])
                
                st.write("✅ **API Response Analysis:**")
                st.write(f"   📊 Words: {word_count:,}")
                st.write(f"   📝 Characters: {char_count:,}")
                st.write(f"   📚 Has Structure: {'✅' if has_structure else '❌'}")
                st.write(f"   🎯 Has Bloom's Taxonomy: {'✅' if has_blooms else '❌'}")
                
                if word_count < 800:
                    st.warning(f"⚠️ Response seems short ({word_count} words). Expected 1,000+")
                    st.write("🔍 First 500 characters of response:")
                    st.code(content[:500])
                elif word_count < 1200:
                    st.warning(f"⚠️ Response shorter than expected ({word_count} words). Expected 1,000-1,500")
                else:
                    st.success(f"✅ Good response length: {word_count:,} words")
                
                return content
            else:
                st.error(f"❌ Unexpected response format")
                st.json(result)
                
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ HTTP Error {e.response.status_code}")
            try:
                error_detail = e.response.json()
                st.json(error_detail)
            except:
                st.error(e.response.text[:500])
            
            if e.response.status_code == 401:
                st.error("🔑 Invalid API Key - Check your configuration")
                return None
            elif e.response.status_code == 429:
                st.warning("⏳ Rate limited - waiting before retry...")
                time.sleep(10)
            else:
                if attempt < retries - 1:
                    st.warning(f"⏳ Retrying in 3 seconds...")
                    time.sleep(3)
                    
        except requests.exceptions.Timeout:
            st.error(f"⏱️ Request timeout after {timeout}s")
            if attempt < retries - 1:
                st.warning("⏳ Retrying with longer timeout...")
                timeout += 30
                time.sleep(2)
                
        except requests.exceptions.ConnectionError as e:
            st.error(f"🔌 Connection error: {str(e)}")
            if attempt < retries - 1:
                st.warning("⏳ Retrying connection...")
                time.sleep(3)
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)
    
    st.error("❌ All API attempts failed - check logs above for details")
    return None

# ============================================================================
# PDF AND SYLLABUS PROCESSING
# ============================================================================

def extract_pdf_text(pdf_file):
    """
    Extract text from uploaded PDF file
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        str: Extracted text or None if failed
    """
    if not PYPDF2_AVAILABLE:
        st.error("PyPDF2 not installed - cannot extract PDF")
        return None
        
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += page_text + "\n"
            
        st.success(f"✅ Extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
        return text
        
    except Exception as e:
        st.error(f"❌ Error extracting PDF: {str(e)}")
        return None

def parse_syllabus_structure(text):
    """
    Parse syllabus text to extract course structure
    
    Args:
        text: Syllabus text content
        
    Returns:
        dict: Structured syllabus data with course_info and units
    """
    structure = {'course_info': {}, 'units': []}
    
    # Extract course information
    patterns = {
        'title': r'(?:Course|Subject)\s*(?:Title|Name)?\s*:?\s*(.+)',
        'code': r'(?:Course|Subject)\s*Code\s*:?\s*([A-Z0-9]+)',
        'credits': r'Credits?\s*:?\s*(\d+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            structure['course_info'][key] = match.group(1).strip()
    
    # Extract units with their topics
    unit_pattern = r'UNIT[\s-]*(\d+)\s*:?\s*(.+?)(?=UNIT[\s-]*\d+|$)'
    units = re.finditer(unit_pattern, text, re.IGNORECASE | re.DOTALL)
    
    for unit_match in units:
        unit_num = unit_match.group(1)
        unit_content = unit_match.group(2)
        
        # Extract unit title (first line)
        title_match = re.search(r'^(.+?)(?:\n|$)', unit_content)
        unit_title = title_match.group(1).strip() if title_match else f"Unit {unit_num}"
        
        # Extract topics (numbered lines)
        topics = []
        lines = unit_content.split('\n')
        for line in lines:
            if re.match(r'^\s*[\d.]+\s+(.+?)$', line):
                topic = re.match(r'^\s*[\d.]+\s+(.+?)$', line).group(1).strip()
                if 5 < len(topic) < 200:  # Filter reasonable topic lengths
                    topics.append(topic)
        
        structure['units'].append({
            'unit_number': int(unit_num),
            'unit_title': unit_title,
            'topics': topics
        })
    
    return structure

# ============================================================================
# TEXT CLEANING AND FORMATTING (FIXED LATEX HANDLING)
# ============================================================================

def clean_text_for_pdf(text):
    """
    Clean text for PDF with HTML tags for bold/italic and handle LaTeX equations
    
    Args:
        text: Raw text with markdown and LaTeX
        
    Returns:
        str: Cleaned text with HTML formatting
    """
    if not text:
        return ""
    
    # Convert LaTeX equations to readable format
    # Inline math: \( ... \) or $ ... $
    text = re.sub(r'\\\((.*?)\\\)', r'[\1]', text)
    text = re.sub(r'\$([^\$]+?)\$', r'[\1]', text)
    
    # Display math: \[ ... \] or $$ ... $$
    text = re.sub(r'\\\[(.*?)\\\]', r'[\1]', text, flags=re.DOTALL)
    text = re.sub(r'\$\$(.*?)\$\$', r'[\1]', text, flags=re.DOTALL)
    
    # Common LaTeX commands to Unicode symbols
    latex_replacements = {
        r'\\leq': '≤',
        r'\\geq': '≥',
        r'\\neq': '≠',
        r'\\approx': '≈',
        r'\\equiv': '≡',
        r'\\times': '×',
        r'\\div': '÷',
        r'\\pm': '±',
        r'\\mp': '∓',
        r'\\sum': 'Σ',
        r'\\prod': 'Π',
        r'\\int': '∫',
        r'\\infty': '∞',
        r'\\partial': '∂',
        r'\\nabla': '∇',
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\gamma': 'γ',
        r'\\delta': 'δ',
        r'\\epsilon': 'ε',
        r'\\theta': 'θ',
        r'\\lambda': 'λ',
        r'\\mu': 'μ',
        r'\\pi': 'π',
        r'\\sigma': 'σ',
        r'\\tau': 'τ',
        r'\\phi': 'φ',
        r'\\omega': 'ω',
        r'\\Gamma': 'Γ',
        r'\\Delta': 'Δ',
        r'\\Theta': 'Θ',
        r'\\Lambda': 'Λ',
        r'\\Sigma': 'Σ',
        r'\\Phi': 'Φ',
        r'\\Omega': 'Ω',
        r'\\rightarrow': '→',
        r'\\leftarrow': '←',
        r'\\Rightarrow': '⇒',
        r'\\Leftarrow': '⇐',
        r'\\leftrightarrow': '↔',
        r'\\Leftrightarrow': '⇔',
        r'\\forall': '∀',
        r'\\exists': '∃',
        r'\\in': '∈',
        r'\\notin': '∉',
        r'\\subset': '⊂',
        r'\\subseteq': '⊆',
        r'\\supset': '⊃',
        r'\\supseteq': '⊇',
        r'\\cup': '∪',
        r'\\cap': '∩',
        r'\\emptyset': '∅',
        r'\\_': '_',
        r'\\{': '{',
        r'\\}': '}',
        r'\\%': '%',
    }
    
    for latex, symbol in latex_replacements.items():
        text = re.sub(latex, symbol, text)
    
    # Handle subscripts and superscripts (simplified)
    text = re.sub(r'_\{([^}]+)\}', r'_\1', text)
    text = re.sub(r'\^\{([^}]+)\}', r'^\1', text)
    
    # Remove remaining LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Handle markdown bold and italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    return text

# ============================================================================
# GOOGLE DRIVE OPERATIONS (FIXED WITH AUTO-SUBFOLDER)
# ============================================================================

def setup_google_drive_connection():
    """
    Setup Google Drive API connection with service account
    
    Returns:
        Google Drive service object or None if failed
    """
    if not GDRIVE_AVAILABLE:
        st.error("Google Drive libraries not installed")
        return None
        
    try:
        credentials = service_account.Credentials.from_service_account_info(
            GDRIVE_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=credentials)
        
        # Test connection
        service.files().list(pageSize=1).execute()
        
        return service
        
    except Exception as e:
        st.error(f"❌ Google Drive connection failed: {str(e)}")
        st.error("💡 Make sure the service account has access to the folder")
        st.info("📧 Share folder with: curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com")
        return None

def extract_folder_id_from_url(url):
    """
    Extract Google Drive folder ID from URL
    
    Args:
        url: Google Drive folder URL or ID
        
    Returns:
        str: Folder ID or None if invalid
    """
    patterns = [
        r'folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'https://drive\.google\.com/drive/[^/]+/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Check if it's already just an ID
    if re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url
    
    return None

def create_or_use_folder(service, folder_name, parent_id=None):
    """
    Create new folder or use existing one in Google Drive
    
    Args:
        service: Google Drive service object
        folder_name: Name of folder to create
        parent_id: Parent folder ID (optional)
        
    Returns:
        str: Folder ID or None if failed
    """
    try:
        # Check if folder already exists
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(
            q=query,
            fields="files(id, name, webViewLink)",
            spaces='drive'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
            folder_link = folders[0].get('webViewLink', '')
            st.info(f"✅ Using existing folder: {folder_name}")
            if folder_link:
                st.info(f"🔗 Folder: {folder_link}")
            return folder_id
        
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = service.files().create(
            body=file_metadata,
            fields='id,webViewLink'
        ).execute()
        
        folder_id = folder.get('id')
        folder_link = folder.get('webViewLink')
        
        st.success(f"✅ Created new folder: {folder_name}")
        if folder_link:
            st.info(f"🔗 Folder: {folder_link}")
        
        return folder_id
        
    except Exception as e:
        st.error(f"❌ Error with folder '{folder_name}': {str(e)}")
        
        # Check for permission errors
        error_str = str(e).lower()
        if 'insufficient permissions' in error_str or 'forbidden' in error_str or '403' in error_str:
            st.error("🔒 PERMISSION ERROR!")
            st.error("The service account doesn't have access to this folder.")
            st.info("📋 **Steps to fix:**")
            st.info("1. Open your Google Drive folder")
            st.info("2. Click the 'Share' button")
            st.info("3. Add: curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com")
            st.info("4. Give 'Editor' permissions")
            st.info("5. Click 'Send'")
            st.info("6. Try again")
        
        return None

def upload_to_gdrive(service, file_buffer, filename, folder_id, mime_type='application/pdf'):
    """
    Upload file to Google Drive with retry logic
    
    Args:
        service: Google Drive service object
        file_buffer: BytesIO buffer with file content
        filename: Name for the file
        folder_id: Destination folder ID
        mime_type: MIME type of file
        
    Returns:
        str: Web view link or None if failed
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            file_buffer.seek(0)  # Reset buffer position
            
            media = MediaIoBaseUpload(
                file_buffer,
                mimetype=mime_type,
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            file_id = file.get('id')
            web_link = file.get('webViewLink')
            
            # Optionally make file accessible to anyone with link
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                service.permissions().create(
                    fileId=file_id,
                    body=permission
                ).execute()
            except:
                pass  # Ignore permission errors for sharing
            
            return web_link
            
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ Upload attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
            else:
                st.error(f"❌ Upload failed after {max_retries} attempts: {str(e)}")
                return None
    
    return None

def setup_gdrive_for_compilation():
    """
    Setup Google Drive with automatic timestamped subfolder creation
    
    Returns:
        tuple: (service, folder_id) or (None, None) if failed
    """
    with st.spinner("🔗 Connecting to Google Drive..."):
        gdrive_service = setup_google_drive_connection()
        
        if not gdrive_service:
            st.error("❌ Google Drive connection failed")
            return None, None
        
        st.success("✅ Connected to Google Drive")
        
        # Create timestamped subfolder automatically
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_name = f"{st.session_state.course_code}_{timestamp}"
        
        st.info(f"📁 Creating subfolder: {folder_name}")
        
        # Create subfolder inside the provided parent folder
        gdrive_folder_id = create_or_use_folder(
            gdrive_service,
            folder_name,
            st.session_state.gdrive_folder_id  # Parent folder ID from URL
        )
        
        if gdrive_folder_id:
            st.success(f"✅ Subfolder created: {folder_name}")
            st.info(f"📂 All files will be uploaded here")
            return gdrive_service, gdrive_folder_id
        else:
            st.error("❌ Could not create subfolder - check permissions above")
            st.error("Make sure you shared the folder with the service account")
            return None, None

# ============================================================================
# Phase 2 Complete
# ============================================================================
print("Phase 2: Helper Functions loaded successfully")"""
PHASE 3: CONTENT GENERATION AND COMPILATION
============================================
- AI content generation with image prompts
- Outline generation
- PDF compilation with images and LaTeX support
- DOCX compilation with images
- Header/footer with logo support
"""

# ============================================================================
# CONTENT GENERATION
# ============================================================================

def generate_content(section_info, course_context):
    """
    Generate academic content for a section with image suggestions
    
    Args:
        section_info: Dict with section_number, section_title, description
        course_context: Dict with course details and outcomes
        
    Returns:
        str: Generated content
    """
    system_prompt = f"""You are an expert academic content developer for {course_context['target_audience']}.

Generate comprehensive content following eGyankosh standards:
- 4-5 pages (1,000-1,500 words)
- Grade 5 English, Academic tone
- Readability: 10-12
- Suggest 1-2 relevant image placements with descriptions (e.g., "Image: Diagram of organizational structure")

STRUCTURE (MUST INCLUDE ALL):
1. Introduction (2-3 paragraphs introducing the topic)
2. Learning Objectives (5-7 objectives mapped to Blooms Taxonomy: Remember, Understand, Apply, Analyze, Evaluate, Create)
3. Detailed Content (Main body with subsections, definitions, explanations)
4. Examples & Case Studies (Practical real-world examples)
5. CHECK YOUR PROGRESS (5-7 questions for self-assessment)
6. Summary (Concise recap of key points)
7. Key Terms (Glossary of important terms)

Map to:
- PO: {course_context.get('program_outcomes', 'N/A')}
- CO: {course_context.get('course_outcomes', 'N/A')}
- PSO: {course_context.get('specialized_outcomes', 'N/A')}

For mathematical content, use plain text format: write equations as "Z = c1*x1 + c2*x2 + ... + cn*xn" instead of LaTeX."""

    user_prompt = f"""Write comprehensive academic content for:

**Topic:** {section_info['section_number']} {section_info['section_title']}
**Course:** {course_context['course_title']}
**Description:** {section_info['description']}

Requirements:
- Include clear definitions with **bold key terms**
- Provide detailed explanations with examples
- Add case studies relevant to {course_context['target_audience']}
- Include practical applications
- Use *italics* for emphasis
- Write equations in plain text format (no LaTeX)
- Suggest image placements with descriptions

Make it engaging, informative, and academically rigorous."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return make_api_call(messages, max_tokens=2500)

def generate_outline_with_ai():
    """
    Generate course outline using AI based on course configuration
    
    Returns:
        list: Outline with units and sections, or None if failed
    """
    num_units = st.session_state.get('num_units', 4)
    sections_per_unit = st.session_state.get('sections_per_unit', 8)
    
    st.write(f"🎯 Generating {num_units} units with {sections_per_unit} sections each...")
    
    # Build outcomes context
    outcomes_context = ""
    if st.session_state.program_objectives:
        outcomes_context += f"\n**Program Objectives:** {st.session_state.program_objectives}"
    if st.session_state.program_outcomes:
        outcomes_context += f"\n**Program Outcomes:** {st.session_state.program_outcomes}"
    if st.session_state.course_outcomes:
        outcomes_context += f"\n**Course Outcomes:** {st.session_state.course_outcomes}"
    if st.session_state.specialized_outcomes:
        outcomes_context += f"\n**Specialized Outcomes:** {st.session_state.specialized_outcomes}"
    
    system_prompt = """You are an expert curriculum designer with deep knowledge of educational standards and course design.

Create a comprehensive, well-structured course outline that follows academic best practices.

CRITICAL: Output ONLY valid JSON in this EXACT format:
[
  {
    "unit_number": 1,
    "unit_title": "Descriptive, Engaging Unit Title",
    "sections": [
      {
        "section_number": "1.1",
        "section_title": "Clear Section Title",
        "description": "Detailed 2-3 sentence description of what this section covers, including key concepts and learning goals"
      }
    ]
  }
]

REQUIREMENTS:
- Create academically rigorous, engaging titles
- Make descriptions detailed and specific (not generic)
- Ensure logical progression and flow between topics
- Cover the subject comprehensively
- Use proper academic terminology
- Build complexity progressively from foundational to advanced
- Ensure each description is at least 2-3 sentences explaining WHAT will be covered"""

    user_prompt = f"""Create a comprehensive course outline for:

**Course Title:** {st.session_state.course_title}
**Course Code:** {st.session_state.course_code}
**Target Audience:** {st.session_state.target_audience}
**Credits:** {st.session_state.credits}

{outcomes_context}

**STRUCTURE REQUIREMENTS:**
- Generate EXACTLY {num_units} units
- Each unit must have EXACTLY {sections_per_unit} sections
- Section numbering: 1.1 to 1.{sections_per_unit}, 2.1 to 2.{sections_per_unit}, etc.
- Total sections must be: {num_units * sections_per_unit}

**CONTENT REQUIREMENTS:**
- Make unit titles specific to {st.session_state.course_title}
- Create logical flow from basics to advanced concepts
- Ensure comprehensive coverage of the subject
- Make descriptions specific and detailed (NOT generic like "First topic", "Overview")
- Each description should explain WHAT concepts/theories/applications will be covered

Return ONLY the JSON array. No additional text, no markdown code blocks, just pure JSON."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    with st.expander("🔍 AI Outline Generation Details", expanded=True):
        outline_str = make_api_call(messages, max_tokens=3000, retries=3)
    
    if outline_str:
        try:
            # Clean response
            outline_str = outline_str.strip()
            
            # Remove markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', outline_str, re.DOTALL)
            if json_match:
                outline_str = json_match.group(1)
            
            outline_str = outline_str.strip()
            
            # Parse JSON
            parsed_outline = json.loads(outline_str)
            
            if isinstance(parsed_outline, list) and len(parsed_outline) > 0:
                actual_units = len(parsed_outline)
                actual_sections = sum(len(u.get('sections', [])) for u in parsed_outline)
                
                st.success(f"✅ AI generated {actual_units} units with {actual_sections} sections!")
                
                # Verify structure
                if actual_units != num_units:
                    st.warning(f"⚠️ Expected {num_units} units, got {actual_units}")
                
                if actual_sections < (num_units * sections_per_unit * 0.8):
                    st.warning(f"⚠️ Expected ~{num_units * sections_per_unit} sections, got {actual_sections}")
                
                # Show preview
                with st.expander("📋 Preview Generated Outline", expanded=False):
                    for unit in parsed_outline[:2]:
                        st.write(f"**Unit {unit['unit_number']}: {unit['unit_title']}**")
                        for section in unit.get('sections', [])[:3]:
                            st.write(f"  - {section['section_number']} {section['section_title']}")
                
                return parsed_outline
            else:
                st.error("❌ Invalid outline format - not a valid list")
                return None
                
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON parsing failed: {str(e)}")
            st.write("**Raw AI Response:**")
            st.code(outline_str[:1000], language="json")
            st.error("💡 Try regenerating or check API response format")
            return None
    
    st.error("❌ AI did not return any content")
    return None

def generate_image_prompt_for_section(section_info, course_context):
    """
    Generate a detailed image generation prompt for a section
    
    Args:
        section_info: Dict with section details
        course_context: Dict with course context
        
    Returns:
        str: Image generation prompt
    """
    system_prompt = """You are an expert at creating detailed image generation prompts for educational content.

Create a detailed, specific prompt that can be used with AI image generators like DALL-E, Midjourney, or Stable Diffusion.

The prompt should:
- Be specific and descriptive
- Include style (e.g., "professional diagram", "infographic", "illustration")
- Mention colors if relevant
- Specify composition and layout
- Be suitable for educational materials
- Be 2-3 sentences maximum"""

    user_prompt = f"""Create an image generation prompt for this educational section:

**Section:** {section_info['section_number']} {section_info['section_title']}
**Course:** {course_context['course_title']}
**Description:** {section_info['description']}
**Audience:** {course_context['target_audience']}

Generate a detailed prompt for ONE relevant educational image."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    prompt = make_api_call(messages, max_tokens=200)
    return prompt if prompt else f"Educational diagram about {section_info['section_title']}"

# ============================================================================
# PDF COMPILATION WITH IMAGES
# ============================================================================

def add_header_footer(canvas, doc, course_info, logo=None):
    """
    Add header and footer to PDF pages
    
    Args:
        canvas: ReportLab canvas
        doc: Document template
        course_info: Course information dict
        logo: Logo image file or None
    """
    canvas.saveState()
    
    # Header - Document heading
    heading = st.session_state.get('document_heading', course_info.get('course_title', ''))
    if heading:
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(72, doc.height + 50, heading[:80])
    
    # Logo in header (top right)
    if logo:
        try:
            logo.seek(0)
            logo_bytes = logo.read()
            logo_buffer = BytesIO(logo_bytes)
            img = PilImage.open(logo_buffer)
            
            # Save as temporary file for ReportLab
            temp_logo = BytesIO()
            img.save(temp_logo, format='PNG')
            temp_logo.seek(0)
            
            canvas.drawImage(
                temp_logo,
                doc.width - 1.5*inch + 72,
                doc.height + 30,
                width=1.2*inch,
                height=0.6*inch,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            pass  # Ignore logo errors
    
    # Footer - Page number and date
    canvas.setFont("Helvetica", 9)
    page_text = f"Page {doc.page}"
    canvas.drawString(doc.width / 2 + 20, 40, page_text)
    
    date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d')}"
    canvas.drawString(72, 40, date_text)
    
    canvas.restoreState()

def create_decorative_line():
    """Create decorative line table for PDF"""
    if not REPORTLAB_AVAILABLE:
        return None
        
    line_table = Table([['']], colWidths=[6.5*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1f77b4'))
    ]))
    return line_table

def compile_unit_pdf(unit_data, course_info, content_dict):
    """
    Compile a single unit into PDF with images and formatting
    
    Args:
        unit_data: Unit information dict
        course_info: Course information dict
        content_dict: Dictionary of generated content
        
    Returns:
        BytesIO: PDF buffer or None if failed
    """
    if not REPORTLAB_AVAILABLE:
        st.error("ReportLab not available")
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=1.2*inch,
        bottomMargin=1*inch
    )
    
    # Add header/footer callback
    def add_page_elements(canvas, doc):
        add_header_footer(canvas, doc, course_info, st.session_state.get('logo'))
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=30,
        spaceBefore=20
    )
    
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold',
        spaceAfter=12,
        spaceBefore=12
    )
    
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#34495e'),
        fontName='Helvetica-Bold',
        spaceAfter=10,
        spaceBefore=10
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
        fontName='Helvetica'
    )
    
    # Cover page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(f"UNIT {unit_data['unit_number']}", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(unit_data['unit_title'].upper(), title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Decorative line
    if create_decorative_line():
        story.append(create_decorative_line())
        story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(course_info.get('course_title', ''), styles['Heading3']))
    story.append(Paragraph(f"Course Code: {course_info.get('course_code', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"Credits: {course_info.get('credits', 3)}", styles['Normal']))
    story.append(PageBreak())
    
    # Content sections
    for section in unit_data.get('sections', []):
        sec_key = f"{section['section_number']} {section['section_title']}"
        
        # Section heading
        story.append(Paragraph(f"<b>{sec_key}</b>", section_style))
        if create_decorative_line():
            story.append(create_decorative_line())
        story.append(Spacer(1, 0.2*inch))
        
        # Add image if available
        image_data = st.session_state.images.get(sec_key)
        if image_data:
            try:
                image_data.seek(0)
                img_bytes = image_data.read()
                img_buffer = BytesIO(img_bytes)
                
                # Add image to PDF
                story.append(Image(img_buffer, width=4*inch, height=2.5*inch))
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                st.warning(f"⚠️ Could not add image for {sec_key}: {str(e)}")
        
        # Content
        content = content_dict.get(sec_key, "[Content not generated]")
        content_lines = content.split('\n')
        
        for line in content_lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            
            # Handle different content types
            if 'CHECK YOUR PROGRESS' in line.upper():
                story.append(Paragraph("<b>CHECK YOUR PROGRESS</b>", subsection_style))
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('## '):
                clean_line = clean_text_for_pdf(line[3:])
                story.append(Paragraph(clean_line, subsection_style))
            elif line.startswith(('*', '-', '•', '1.', '2.', '3.')):
                clean_line = clean_text_for_pdf(re.sub(r'^[\*\-•\d\.]\s*', '', line))
                story.append(Paragraph(f"• {clean_line}", body_style))
            else:
                clean_line = clean_text_for_pdf(line)
                if len(clean_line) > 3:
                    try:
                        story.append(Paragraph(clean_line, body_style))
                    except Exception as e:
                        # Fallback for problematic content
                        story.append(Paragraph(line[:500], body_style))
        
        story.append(Spacer(1, 0.5*inch))
        story.append(PageBreak())
    
    try:
        doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ PDF compilation error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

def compile_complete_pdf(outline, course_info, content_dict):
    """
    Compile complete course PDF with all units
    
    Args:
        outline: Complete course outline
        course_info: Course information
        content_dict: All generated content
        
    Returns:
        BytesIO: Complete PDF buffer or None
    """
    if not REPORTLAB_AVAILABLE:
        st.error("ReportLab not available")
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=1.2*inch,
        bottomMargin=1*inch
    )
    
    def add_page_elements(canvas, doc):
        add_header_footer(canvas, doc, course_info, st.session_state.get('logo'))
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=28,
        alignment=TA_CENTER,
        spaceAfter=40,
        fontName='Helvetica-Bold'
    )
    
    # Title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(course_info['course_title'], title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        f"Course Code: {course_info['course_code']} | Credits: {course_info['credits']}",
        styles['Normal']
    ))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Complete Curriculum", styles['Heading1']))
    story.append(PageBreak())
    
    # All units content
    for unit in outline:
        # Process each unit similarly to compile_unit_pdf
        story.append(Paragraph(
            f"UNIT {unit['unit_number']}: {unit['unit_title']}",
            styles['Heading1']
        ))
        story.append(PageBreak())
        
        for section in unit.get('sections', []):
            sec_key = f"{section['section_number']} {section['section_title']}"
            story.append(Paragraph(sec_key, styles['Heading2']))
            
            # Add image if available
            image_data = st.session_state.images.get(sec_key)
            if image_data:
                try:
                    image_data.seek(0)
                    img_bytes = image_data.read()
                    img_buffer = BytesIO(img_bytes)
                    story.append(Image(img_buffer, width=4*inch, height=2.5*inch))
                    story.append(Spacer(1, 0.2*inch))
                except:
                    pass
            
            content = content_dict.get(sec_key, "[Not generated]")
            clean_content = clean_text_for_pdf(content)
            
            # Add content paragraphs
            for para in clean_content.split('\n'):
                if para.strip():
                    try:
                        story.append(Paragraph(para, styles['Normal']))
                    except:
                        pass
            
            story.append(PageBreak())
    
    try:
        doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ Complete PDF error: {str(e)}")
        return None

# ============================================================================
# DOCX COMPILATION WITH IMAGES
# ============================================================================

def compile_unit_docx(unit_data, course_info, content_dict):
    """
    Compile unit as editable DOCX with images
    
    Args:
        unit_data: Unit information
        course_info: Course information
        content_dict: Generated content
        
    Returns:
        BytesIO: DOCX buffer or None
    """
    if not DOCX_AVAILABLE:
        st.error("python-docx not available")
        return None
    
    buffer = BytesIO()
    doc = Document()
    
    # Title
    title = doc.add_heading(f"UNIT {unit_data['unit_number']}: {unit_data['unit_title']}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Course info
    doc.add_paragraph(
        f"Course: {course_info['course_title']} | "
        f"Code: {course_info['course_code']} | "
        f"Credits: {course_info['credits']}"
    )
    doc.add_page_break()
    
    # Content sections
    for section in unit_data.get('sections', []):
        sec_key = f"{section['section_number']} {section['section_title']}"
        
        # Section heading
        doc.add_heading(sec_key, level=1)
        
        # Add image if available
        image_data = st.session_state.images.get(sec_key)
        if image_data:
            try:
                image_data.seek(0)
                img_bytes = image_data.read()
                doc.add_picture(BytesIO(img_bytes), width=Inches(4.5))
                doc.add_paragraph()  # Space after image
            except Exception as e:
                st.warning(f"⚠️ Could not add image to DOCX: {str(e)}")
        
        # Add content
        content = content_dict.get(sec_key, "[Not generated]")
        
        for line in content.split('\n'):
            line = line.strip()
            if line:
                # Simple formatting
                if '**' in line:
                    # Handle bold text
                    p = doc.add_paragraph()
                    parts = re.split(r'\*\*(.+?)\*\*', line)
                    for i, part in enumerate(parts):
                        if i % 2 == 1:  # Odd indices are bold
                            run = p.add_run(part)
                            run.bold = True
                        else:
                            p.add_run(part)
                else:
                    doc.add_paragraph(line)
        
        doc.add_page_break()
    
    try:
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ DOCX error: {str(e)}")
        return None

def compile_complete_docx(outline, course_info, content_dict):
    """
    Compile complete course as DOCX
    
    Args:
        outline: Course outline
        course_info: Course information
        content_dict: All content
        
    Returns:
        BytesIO: DOCX buffer or None
    """
    if not DOCX_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = Document()
    
    # Title page
    title = doc.add_heading(course_info['course_title'], 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        f"Code: {course_info['course_code']} | Credits: {course_info['credits']}"
    )
    doc.add_page_break()
    
    # All units
    for unit in outline:
        doc.add_heading(f"UNIT {unit['unit_number']}: {unit['unit_title']}", level=1)
        
        for section in unit.get('sections', []):
            sec_key = f"{section['section_number']} {section['section_title']}"
            doc.add_heading(sec_key, level=2)
            
            # Add image
            image_data = st.session_state.images.get(sec_key)
            if image_data:
                try:
                    image_data.seek(0)
                    doc.add_picture(BytesIO(image_data.read()), width=Inches(4.5))
                except:
                    pass
            
            # Add content
            content = content_dict.get(sec_key, "[Not generated]")
            doc.add_paragraph(content)
            doc.add_page_break()
    
    try:
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ Complete DOCX error: {str(e)}")
        return None

# ============================================================================
# Phase 3 Complete
# ============================================================================
print("Phase 3: Content Generation and Compilation loaded successfully")"""
PHASE 4: USER INTERFACE PAGES (PART 1)
========================================
- Syllabus upload page
- Configuration page with PEO/PO/CO/PSO
- Outline generation page
- Navigation system
"""

# ============================================================================
# NAVIGATION
# ============================================================================

def show_navigation():
    """Display step navigation bar"""
    steps = {
        'syllabus_upload': '1️⃣ Syllabus',
        'configuration': '2️⃣ Config',
        'outline_generation': '3️⃣ Outline',
        'content_generation': '4️⃣ Content',
        'compilation': '5️⃣ Output'
    }
    
    current = st.session_state.step
    
    cols = st.columns(len(steps))
    for i, (key, name) in enumerate(steps.items()):
        with cols[i]:
            if key == current:
                st.markdown(f"**🔵 {name}**")
            else:
                st.markdown(f"⚪ {name}")
    
    st.divider()

# ============================================================================
# PAGE 1: SYLLABUS UPLOAD
# ============================================================================

def show_syllabus_upload_page():
    """Syllabus upload page - optional PDF upload"""
    st.header("📄 Step 1: Syllabus Upload (Optional)")
    
    st.info("💡 You can upload a syllabus PDF to auto-extract structure, or skip this step to create a custom outline with AI.")
    
    choice = st.radio(
        "Choose an option:",
        ["Upload Syllabus PDF", "Skip and Create Custom Outline"],
        key="upload_choice"
    )
    
    if choice == "Upload Syllabus PDF":
        if PYPDF2_AVAILABLE:
            uploaded = st.file_uploader(
                "Upload PDF Syllabus",
                type=['pdf'],
                key="syllabus_file",
                help="Upload your course syllabus PDF to automatically extract the structure"
            )
            
            if uploaded:
                with st.spinner("📖 Extracting text from PDF..."):
                    text = extract_pdf_text(uploaded)
                    
                    if text:
                        st.success("✅ Text extracted successfully!")
                        
                        with st.expander("📝 Preview Extracted Text", expanded=False):
                            st.text_area("Extracted Content", text[:1000] + "...", height=200)
                        
                        with st.spinner("🔍 Parsing syllabus structure..."):
                            structure = parse_syllabus_structure(text)
                            st.session_state.extracted_structure = structure
                            
                            if structure['course_info']:
                                st.success("✅ Course information extracted!")
                                with st.expander("📋 Course Information", expanded=True):
                                    for key, value in structure['course_info'].items():
                                        st.write(f"**{key.title()}:** {value}")
                            
                            if structure['units']:
                                st.success(f"✅ Found {len(structure['units'])} units")
                                
                                for unit in structure['units']:
                                    with st.expander(f"Unit {unit['unit_number']}: {unit['unit_title']}", expanded=False):
                                        st.write(f"**Topics ({len(unit['topics'])}):**")
                                        for i, topic in enumerate(unit['topics'], 1):
                                            st.write(f"{i}. {topic}")
                                
                                st.divider()
                                
                                if st.checkbox("✅ Structure looks good, use this", key="confirm_structure"):
                                    if st.button("Continue to Configuration →", type="primary", key="continue_with_structure"):
                                        st.session_state.step = 'configuration'
                                        st.rerun()
                            else:
                                st.warning("⚠️ No units found in syllabus. You can still continue and create a custom outline.")
                                if st.button("Continue Anyway →", type="primary"):
                                    st.session_state.step = 'configuration'
                                    st.rerun()
        else:
            st.error("❌ PyPDF2 not installed. Cannot extract PDF content.")
            st.info("Install with: pip install PyPDF2")
            if st.button("Continue Without Upload →", type="primary"):
                st.session_state.step = 'configuration'
                st.rerun()
    else:
        st.info("✅ You'll create a custom outline in the next steps using AI")
        if st.button("Continue to Configuration →", type="primary", key="skip_upload"):
            st.session_state.step = 'configuration'
            st.rerun()

# ============================================================================
# PAGE 2: CONFIGURATION
# ============================================================================

def show_configuration_page():
    """Configuration page with API, course details, and academic mappings"""
    st.header("⚙️ Step 2: Configuration")
    
    # ========== API Configuration ==========
    st.subheader("🔑 API Configuration")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            "Grok API Key",
            value=st.session_state.api_key,
            type="password",
            key="api_key_input",
            help="Your Grok API key from x.ai - starts with 'xai-'"
        )
        st.session_state.api_key = api_key
        
        if api_key and api_key.startswith('xai-'):
            st.success("✅ Valid API key format")
        else:
            st.warning("⚠️ API key should start with 'xai-'")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🧪 Test API", use_container_width=True, key="test_api_btn"):
            with st.expander("🔍 API Test Results", expanded=True):
                st.info("Testing API connection and response quality...")
                
                test_messages = [
                    {"role": "system", "content": "You are a helpful academic content generator."},
                    {"role": "user", "content": "Write a 200-word introduction about Organizational Behaviour. Include: definition, importance, and key concepts. Use academic tone."}
                ]
                
                test_response = make_api_call(test_messages, max_tokens=500)
                
                if test_response:
                    st.success("✅ API is working!")
                    st.write("**Response Preview:**")
                    st.write(test_response[:300] + "...")
                    
                    word_count = len(test_response.split())
                    if word_count >= 150:
                        st.success(f"✅ Good response length: {word_count} words")
                    else:
                        st.warning(f"⚠️ Response seems short: {word_count} words")
                    
                    if len(test_response) > 100:
                        st.success("✅ API returning substantial content")
                        st.info("💡 Your API is ready for curriculum generation!")
                    else:
                        st.error("❌ API response too short - check configuration")
                else:
                    st.error("❌ API test failed - check logs above")
    
    st.divider()
    
    # ========== Course Details ==========
    st.subheader("📚 Course Details")
    
    extracted = st.session_state.get('extracted_structure', {})
    course_info = extracted.get('course_info', {})
    
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input(
            "Course Title",
            value=course_info.get('title', st.session_state.course_title),
            key="title_input",
            help="Full name of the course"
        )
        st.session_state.course_title = title
        
        code = st.text_input(
            "Course Code",
            value=course_info.get('code', st.session_state.course_code),
            key="code_input",
            help="Course code (e.g., MBA101, CS202)"
        )
        st.session_state.course_code = code
    
    with col2:
        credits = st.number_input(
            "Credits",
            min_value=1,
            max_value=10,
            value=int(course_info.get('credits', st.session_state.credits)) if course_info.get('credits') else st.session_state.credits,
            key="credits_input",
            help="Number of credit hours"
        )
        st.session_state.credits = credits
        
        audience = st.selectbox(
            "Target Audience",
            ["Postgraduate (MBA)", "Undergraduate", "Diploma", "Certificate"],
            index=0,
            key="audience_select",
            help="Target student level"
        )
        st.session_state.target_audience = audience
    
    st.divider()
    
    # ========== Document Customization ==========
    st.subheader("📄 Document Customization")
    
    col1, col2 = st.columns(2)
    with col1:
        document_heading = st.text_input(
            "Document Header Text (Optional)",
            value=st.session_state.document_heading,
            key="doc_heading",
            help="Text to appear in the header of each page",
            placeholder="e.g., XYZ University - MBA Program"
        )
        st.session_state.document_heading = document_heading
    
    with col2:
        logo = st.file_uploader(
            "Upload Logo for Header (Optional)",
            type=['png', 'jpg', 'jpeg'],
            key="logo_uploader",
            help="Logo will appear in the top-right corner of each page"
        )
        if logo:
            st.session_state.logo = logo
            st.success("✅ Logo uploaded")
            # Show preview
            st.image(logo, width=150, caption="Logo Preview")
        elif st.session_state.logo:
            st.info("✅ Logo from previous session")
    
    st.divider()
    
    # ========== Content Structure ==========
    if not st.session_state.get('extracted_structure'):
        st.subheader("📚 Content Structure")
        st.info("💡 Define how many units and sections you want. AI will generate relevant content for each.")
        
        col1, col2 = st.columns(2)
        with col1:
            num_units = st.number_input(
                "Number of Units",
                min_value=1,
                max_value=10,
                value=st.session_state.get('num_units', 4),
                help="How many major units/modules for this course",
                key="num_units_config"
            )
            st.session_state.num_units = num_units
        
        with col2:
            sections_per_unit = st.number_input(
                "Sections per Unit",
                min_value=3,
                max_value=15,
                value=st.session_state.get('sections_per_unit', 8),
                help="How many topics/sections in each unit",
                key="sections_per_unit_config"
            )
            st.session_state.sections_per_unit = sections_per_unit
        
        total_sections = num_units * sections_per_unit
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Units", num_units)
        with col2:
            st.metric("Total Sections", total_sections)
        with col3:
            st.metric("Est. Pages", f"~{total_sections * 5}")
        
        st.caption(f"💡 AI will generate {num_units} units with {sections_per_unit} topics each = {total_sections} total sections")
    else:
        st.info("✅ Using structure from uploaded syllabus")
    
    st.divider()
    
    # ========== Academic Mappings ==========
    st.subheader("🎯 Academic Mappings (Optional but Recommended)")
    
    with st.expander("ℹ️ What are PEO, PO, CO, PSO?", expanded=False):
        st.markdown("""
        **Program Educational Objectives (PEO):**
        - What students can accomplish after completing the entire program
        - Long-term career and professional achievements
        
        **Program Outcomes (PO):**
        - Skills and knowledge students gain from the program
        - Example: PO1: Critical thinking, PO2: Communication skills, PO3: Ethical awareness
        
        **Course Learning Outcomes (CO):**
        - What students learn in THIS specific course
        - Example: CO1: Understand OB concepts [Bloom: Understand], CO2: Apply leadership theories [Bloom: Apply]
        
        **Program Specific Outcomes (PSO):**
        - Specialized skills specific to the program (e.g., MBA-specific)
        - Example: PSO1: Strategic management, PSO2: Business analytics
        
        These mappings help create better-aligned content and demonstrate learning outcomes.
        """)
    
    st.info("💡 These mappings enhance content quality and alignment. Leave blank if not needed.")
    
    peo = st.text_area(
        "Program Educational Objectives (PEO)",
        value=st.session_state.program_objectives,
        placeholder="Example:\n- Develop strategic leadership capabilities\n- Foster analytical decision-making skills\n- Build effective communication abilities",
        help="What students should achieve after completing the program",
        key="peo_input",
        height=120
    )
    st.session_state.program_objectives = peo
    
    col1, col2 = st.columns(2)
    with col1:
        po = st.text_area(
            "Program Outcomes (PO)",
            value=st.session_state.program_outcomes,
            placeholder="Example:\nPO1: Critical thinking and problem-solving\nPO2: Effective communication\nPO3: Ethical decision-making\nPO4: Teamwork and collaboration",
            help="Skills and knowledge from the program",
            key="po_input",
            height=150
        )
        st.session_state.program_outcomes = po
    
    with col2:
        pso = st.text_area(
            "Program Specific Outcomes (PSO)",
            value=st.session_state.specialized_outcomes,
            placeholder="Example:\nPSO1: Advanced managerial skills\nPSO2: Strategic HR management\nPSO3: Organizational leadership\nPSO4: Change management expertise",
            help="Specialized skills for this specific program",
            key="pso_input",
            height=150
        )
        st.session_state.specialized_outcomes = pso
    
    co = st.text_area(
        "Course Learning Outcomes (CO)",
        value=st.session_state.course_outcomes,
        placeholder="Example:\nCO1: Understand key organizational behaviour concepts [Bloom: Understand]\nCO2: Apply OB theories to real-world scenarios [Bloom: Apply]\nCO3: Analyze organizational dynamics and culture [Bloom: Analyze]\nCO4: Evaluate organizational strategies [Bloom: Evaluate]",
        help="What students will learn in THIS specific course",
        key="co_input",
        height=150
    )
    st.session_state.course_outcomes = co
    
    if peo or po or co or pso:
        st.success("✅ Academic mappings will be integrated into content generation")
    else:
        st.info("ℹ️ Content will be generated with general academic outcomes")
    
    st.divider()
    
    # ========== Google Drive Configuration ==========
    st.subheader("☁️ Google Drive Upload (Optional)")
    
    if GDRIVE_AVAILABLE:
        st.info("💡 Files can be automatically uploaded to your Google Drive with timestamped subfolders")
        
        folder_url = st.text_input(
            "Google Drive Folder URL or ID",
            value=st.session_state.gdrive_folder_url,
            key="folder_input",
            placeholder="https://drive.google.com/drive/folders/...",
            help="Paste the Google Drive folder URL where files should be uploaded"
        )
        st.session_state.gdrive_folder_url = folder_url
        
        if folder_url:
            folder_id = extract_folder_id_from_url(folder_url)
            if folder_id:
                st.session_state.gdrive_folder_id = folder_id
                st.success(f"✅ Folder ID extracted: {folder_id}")
                
                st.warning("⚠️ **Important:** Share this folder with the service account!")
                st.code("curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com")
                
                with st.expander("📋 How to share the folder", expanded=False):
                    st.markdown("""
                    1. Open your Google Drive folder
                    2. Click the **Share** button
                    3. Add this email: `curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com`
                    4. Give **Editor** permissions
                    5. Click **Send**
                    6. Come back here and continue
                    """)
            else:
                st.error("❌ Could not extract folder ID. Please check the URL.")
    else:
        st.warning("⚠️ Google Drive libraries not installed. Upload feature disabled.")
        st.info("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    
    st.divider()
    
    # ========== Navigation Buttons ==========
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back", use_container_width=True, key="back_to_upload"):
            st.session_state.step = 'syllabus_upload'
            st.rerun()
    
    with col3:
        if st.button("Next: Generate Outline →", type="primary", use_container_width=True, key="next_to_outline"):
            # Validation
            if not st.session_state.course_title:
                st.error("❌ Please enter a course title")
            elif not st.session_state.course_code:
                st.error("❌ Please enter a course code")
            else:
                st.session_state.step = 'outline_generation'
                st.rerun()

# ============================================================================
# PAGE 3: OUTLINE GENERATION
# ============================================================================

def show_outline_page():
    """Outline generation and editing page"""
    st.header("📋 Step 3: Course Outline")
    
    # Check if outline needs to be generated
    if 'outline' not in st.session_state or st.session_state.outline is None:
        
        # Check if extracted from syllabus
        extracted = st.session_state.get('extracted_structure')
        
        if extracted and extracted.get('units'):
            st.info("✅ Using syllabus structure from uploaded PDF")
            
            # Convert extracted structure to outline format
            outline = []
            for unit in extracted['units']:
                sections = []
                for i, topic in enumerate(unit['topics'], 1):
                    sections.append({
                        "section_number": f"{unit['unit_number']}.{i}",
                        "section_title": topic,
                        "description": topic
                    })
                
                outline.append({
                    "unit_number": unit['unit_number'],
                    "unit_title": unit['unit_title'],
                    "sections": sections
                })
            
            st.session_state.outline = outline
            st.success(f"✅ Created outline with {len(outline)} units")
            st.rerun()
            
        else:
            # MUST generate with AI - NO DEFAULTS
            st.warning("⚠️ No outline generated yet")
            st.info("💡 Click 'Generate with AI' to create a custom course outline based on your configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 Generate Outline with AI", type="primary", use_container_width=True, key="generate_ai_outline"):
                    with st.spinner("🤖 AI is creating your course outline... This may take 30-60 seconds"):
                        generated_outline = generate_outline_with_ai()
                        
                        if generated_outline:
                            st.session_state.outline = generated_outline
                            st.success("✅ Outline generated successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ AI generation failed. Please try again or check your API key.")
                            return
            
            with col2:
                if st.button("← Back to Configuration", use_container_width=True, key="back_no_outline"):
                    st.session_state.step = 'configuration'
                    st.rerun()
            
            return
    
    # Display and edit outline
    outline = st.session_state.outline
    total_sections = sum(len(u.get('sections', [])) for u in outline)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Units", len(outline))
    with col2:
        st.metric("📝 Sections", total_sections)
    with col3:
        st.metric("📄 Est. Pages", f"~{total_sections * 5}")
    
    st.divider()
    
    # Convert outline to editable table format
    st.subheader("✏️ Review and Edit Outline")
    st.caption("Click any cell to edit directly. You can modify titles and descriptions.")
    
    rows = []
    for unit in outline:
        for section in unit.get('sections', []):
            rows.append({
                'Unit': unit['unit_number'],
                'Unit Title': unit['unit_title'],
                'Section': section['section_number'],
                'Section Title': section['section_title'],
                'Description': section['description']
            })
    
    edited = st.data_editor(
        rows,
        num_rows="dynamic",
        use_container_width=True,
        height=400,
        key="outline_editor",
        column_config={
            "Unit": st.column_config.NumberColumn("Unit #", width="small"),
            "Unit Title": st.column_config.TextColumn("Unit Title", width="medium"),
            "Section": st.column_config.TextColumn("Section #", width="small"),
            "Section Title": st.column_config.TextColumn("Section Title", width="medium"),
            "Description": st.column_config.TextColumn("Description", width="large"),
        }
    )
    
    st.divider()
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back", use_container_width=True, key="back_from_outline"):
            st.session_state.step = 'configuration'
            st.rerun()
    
    with col2:
        if st.button("🔄 Regenerate with AI", use_container_width=True, key="regen_outline_btn"):
            st.session_state.outline = None
            st.rerun()
    
    with col3:
        if st.button("✅ Approve & Generate Content →", type="primary", use_container_width=True, key="approve_outline_btn"):
            # Convert edited data back to outline format
            approved = []
            current = None
            
            for row in edited:
                unit_num = int(row['Unit'])
                unit_title = row['Unit Title']
                section_num = row['Section']
                section_title = row['Section Title']
                description = row['Description']
                
                if current is None or current['unit_number'] != unit_num:
                    if current:
                        approved.append(current)
                    current = {
                        'unit_number': unit_num,
                        'unit_title': unit_title,
                        'sections': []
                    }
                
                current['sections'].append({
                    'section_number': section_num,
                    'section_title': section_title,
                    'description': description
                })
            
            if current:
                approved.append(current)
            
            st.session_state.approved_outline = approved
            st.session_state.images = {}  # Reset images
            st.session_state.image_prompts = {}  # Reset image prompts
            st.session_state.step = 'content_generation'
            st.success("✅ Outline approved! Moving to content generation...")
            time.sleep(1)
            st.rerun()

# ============================================================================
# Phase 4 Part 1 Complete
# ============================================================================
print("Phase 4 Part 1: UI Pages (Syllabus, Config, Outline) loaded successfully")"""
PHASE 4: USER INTERFACE PAGES (PART 2)
========================================
- Content generation page with image uploads
- Compilation page with Google Drive upload
- Sidebar status display
"""

# ============================================================================
# PAGE 4: CONTENT GENERATION WITH IMAGE UPLOADS
# ============================================================================

def show_content_generation_page():
    """Content generation page with image upload and prompt generation"""
    st.header("✍️ Step 4: Content Generation")
    
    if 'approved_outline' not in st.session_state:
        st.error("❌ No approved outline found")
        if st.button("← Back to Outline", key="back_no_outline_gen"):
            st.session_state.step = 'outline_generation'
            st.rerun()
        return
    
    # Initialize generation
    if 'content' not in st.session_state or not st.session_state.content:
        st.session_state.content = {}
        st.session_state.sections_to_process = []
        st.session_state.generation_start_time = time.time()
        
        # Build list of sections to process
        for unit in st.session_state.approved_outline:
            for section in unit.get('sections', []):
                st.session_state.sections_to_process.append({
                    'unit_number': unit['unit_number'],
                    'unit_title': unit['unit_title'],
                    'section_number': section['section_number'],
                    'section_title': section['section_title'],
                    'description': section.get('description', '')
                })
    
    total = len(st.session_state.sections_to_process)
    completed = len(st.session_state.content)
    
    # Progress metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Completed", f"{completed}/{total}")
    with col2:
        progress_pct = (completed / total * 100) if total > 0 else 0
        st.metric("📊 Progress", f"{progress_pct:.0f}%")
    with col3:
        st.metric("⏳ Remaining", total - completed)
    with col4:
        if completed > 0:
            elapsed = time.time() - st.session_state.generation_start_time
            avg_time = elapsed / completed
            eta_seconds = int(avg_time * (total - completed))
            eta_minutes = eta_seconds // 60
            st.metric("⏱️ ETA", f"~{eta_minutes}min")
    
    # Progress bar
    st.progress(completed / total if total > 0 else 0)
    
    st.divider()
    
    # Generate content section by section
    if completed < total:
        current = st.session_state.sections_to_process[completed]
        section_key = f"{current['section_number']} {current['section_title']}"
        
        st.subheader(f"🤖 Generating: {section_key}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**Unit {current['unit_number']}:** {current['unit_title']}")
            st.write(f"**Description:** {current['description']}")
        
        with col2:
            if st.button("⏸️ Pause Generation", key="pause_gen", use_container_width=True):
                st.session_state.paused = True
                st.rerun()
        
        # Generate content if not paused
        if not st.session_state.paused:
            with st.spinner(f"✍️ Writing content for section {completed + 1} of {total}... This may take 30-60 seconds"):
                
                # Build context
                context = {
                    'course_title': st.session_state.course_title,
                    'course_code': st.session_state.course_code,
                    'credits': st.session_state.credits,
                    'target_audience': st.session_state.target_audience,
                    'program_objectives': st.session_state.program_objectives,
                    'program_outcomes': st.session_state.program_outcomes,
                    'course_outcomes': st.session_state.course_outcomes,
                    'specialized_outcomes': st.session_state.specialized_outcomes
                }
                
                # Generate content
                with st.expander("🔍 Content Generation Details", expanded=True):
                    content = generate_content(current, context)
                
                if content and len(content.strip()) > 100:
                    st.session_state.content[section_key] = content
                    st.success(f"✅ Content generated for {section_key}")
                    
                    # Show preview
                    with st.expander("📄 Content Preview", expanded=False):
                        st.write(content[:500] + "...")
                    
                    st.divider()
                    
                    # ===== IMAGE SECTION =====
                    st.subheader("🖼️ Add Image for This Section (Optional)")
                    
                    tab1, tab2 = st.tabs(["📤 Upload Image", "🤖 Generate Image Prompt"])
                    
                    with tab1:
                        st.info("💡 Upload a relevant image for this section")
                        uploaded_image = st.file_uploader(
                            f"Upload image for {section_key}",
                            type=['png', 'jpg', 'jpeg'],
                            key=f"image_upload_{completed}"
                        )
                        
                        if uploaded_image:
                            st.session_state.images[section_key] = uploaded_image
                            st.success("✅ Image uploaded successfully!")
                            st.image(uploaded_image, caption=section_key, width=300)
                    
                    with tab2:
                        st.info("💡 Generate an AI prompt to create an image for this section")
                        
                        if st.button("🤖 Generate Image Prompt", key=f"gen_img_prompt_{completed}"):
                            with st.spinner("Generating image prompt..."):
                                img_prompt = generate_image_prompt_for_section(current, context)
                                st.session_state.image_prompts[section_key] = img_prompt
                        
                        if section_key in st.session_state.image_prompts:
                            st.success("✅ Image prompt generated!")
                            prompt_text = st.text_area(
                                "Image Generation Prompt (edit if needed):",
                                value=st.session_state.image_prompts[section_key],
                                height=150,
                                key=f"img_prompt_text_{completed}"
                            )
                            st.session_state.image_prompts[section_key] = prompt_text
                            
                            st.info("💡 Copy this prompt and use it with DALL-E, Midjourney, or Stable Diffusion to generate an image, then upload it in the 'Upload Image' tab")
                            
                            if st.button("📋 Copy Prompt", key=f"copy_prompt_{completed}"):
                                st.code(prompt_text)
                    
                    st.divider()
                    
                    # Continue or skip buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("⏭️ Skip Image & Continue", type="primary", use_container_width=True, key=f"skip_img_{completed}"):
                            time.sleep(0.5)
                            st.rerun()
                    
                    with col2:
                        if st.button("✅ Save & Continue", type="primary", use_container_width=True, key=f"continue_{completed}"):
                            time.sleep(0.5)
                            st.rerun()
                    
                else:
                    st.error("❌ Content generation failed or returned insufficient content")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Retry", type="primary", use_container_width=True, key="retry_gen"):
                            st.rerun()
                    with col2:
                        if st.button("⏭️ Skip This Section", use_container_width=True, key="skip_section"):
                            st.session_state.content[section_key] = "[Content generation skipped]"
                            st.rerun()
        else:
            # Paused state
            st.warning("⏸️ Content generation paused")
            st.info(f"Currently at section {completed + 1} of {total}")
            
            if st.button("▶️ Resume Generation", type="primary", key="resume_gen"):
                st.session_state.paused = False
                st.rerun()
    
    else:
        # All content generated
        st.success("🎉 All Content Generated Successfully!")
        
        total_words = sum(len(c.split()) for c in st.session_state.content.values())
        est_pages = total_words // 300 + 1 if total_words > 0 else 0
        images_added = len(st.session_state.images)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Total Words", f"{total_words:,}")
        with col2:
            st.metric("📄 Est. Pages", f"~{est_pages}")
        with col3:
            st.metric("📚 Sections", total)
        with col4:
            st.metric("🖼️ Images", images_added)
        
        # Show content summary
        with st.expander("📊 Content Summary", expanded=False):
            for unit in st.session_state.approved_outline:
                st.write(f"**Unit {unit['unit_number']}: {unit['unit_title']}**")
                for section in unit.get('sections', []):
                    sec_key = f"{section['section_number']} {section['section_title']}"
                    content_words = len(st.session_state.content.get(sec_key, '').split())
                    has_image = "🖼️" if sec_key in st.session_state.images else ""
                    st.write(f"  - {sec_key}: {content_words:,} words {has_image}")
        
        st.divider()
        
        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back to Outline", use_container_width=True, key="back_from_gen"):
                st.session_state.step = 'outline_generation'
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate All", use_container_width=True, key="regen_all"):
                if st.checkbox("⚠️ Confirm: This will delete all generated content", key="confirm_regen"):
                    st.session_state.content = {}
                    st.session_state.images = {}
                    st.session_state.image_prompts = {}
                    st.rerun()
        
        with col3:
            if st.button("📄 Compile Documents →", type="primary", use_container_width=True, key="go_compile"):
                st.session_state.step = 'compilation'
                st.rerun()

# ============================================================================
# PAGE 5: COMPILATION AND GOOGLE DRIVE UPLOAD
# ============================================================================

def show_compilation_page():
    """Compilation page with PDF/DOCX generation and Google Drive upload"""
    st.header("📄 Step 5: Compile & Download")
    
    # Validation
    if 'content' not in st.session_state or not st.session_state.content:
        st.error("❌ No content to compile")
        if st.button("← Back to Content Generation", key="back_no_content"):
            st.session_state.step = 'content_generation'
            st.rerun()
        return
    
    if 'approved_outline' not in st.session_state:
        st.error("❌ No outline found")
        if st.button("← Back to Outline", key="back_no_outline_comp"):
            st.session_state.step = 'outline_generation'
            st.rerun()
        return
    
    # ========== Summary ==========
    st.subheader("📊 Content Summary")
    
    total_sections = len(st.session_state.content)
    total_words = sum(len(c.split()) for c in st.session_state.content.values())
    est_pages = total_words // 300 + 1 if total_words > 0 else 0
    images_count = len(st.session_state.images)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Units", len(st.session_state.approved_outline))
    with col2:
        st.metric("📝 Sections", total_sections)
    with col3:
        st.metric("📄 Words", f"{total_words:,}")
    with col4:
        st.metric("🖼️ Images", images_count)
    
    st.info(f"📄 Estimated pages: ~{est_pages}")
    
    st.divider()
    
    # ========== Compilation Options ==========
    st.subheader("⚙️ Compilation Options")
    
    col1, col2 = st.columns(2)
    with col1:
        compile_type = st.radio(
            "What to compile:",
            ["Separate Unit Files", "Complete Course File", "Both (Separate + Complete)"],
            index=2,
            key="compile_type",
            help="Choose whether to compile each unit separately, one complete file, or both"
        )
    
    with col2:
        output_format = st.radio(
            "Output Format:",
            ["PDF", "DOCX (Editable)"],
            index=0,
            key="output_format",
            help="PDF for final documents, DOCX for editable files in Google Docs"
        )
    
    # Google Drive upload option
    upload_drive = False
    if GDRIVE_AVAILABLE and st.session_state.gdrive_folder_id:
        st.divider()
        upload_drive = st.checkbox(
            "☁️ Upload to Google Drive (Auto-creates timestamped subfolder)",
            value=True,
            key="upload_drive",
            help="Automatically upload all files to Google Drive in a timestamped subfolder"
        )
        
        if upload_drive:
            st.success(f"✅ Will upload to: {st.session_state.gdrive_folder_url}")
            st.info("💡 A subfolder with timestamp will be created automatically")
            if output_format == "DOCX":
                st.info("💡 DOCX files will be editable directly in Google Docs")
    
    st.divider()
    
    # ========== Compilation Button ==========
    if st.button("🔨 Start Compilation & Upload", type="primary", use_container_width=True, key="start_compile"):
        
        course_info = {
            'course_title': st.session_state.course_title,
            'course_code': st.session_state.course_code,
            'credits': st.session_state.credits,
            'target_audience': st.session_state.target_audience
        }
        
        # ===== Setup Google Drive =====
        gdrive_service = None
        gdrive_folder_id = None
        drive_links = {}
        
        if upload_drive:
            gdrive_service, gdrive_folder_id = setup_gdrive_for_compilation()
            
            if not gdrive_service or not gdrive_folder_id:
                st.error("❌ Google Drive setup failed - continuing without upload")
                upload_drive = False
        
        # ===== Compilation =====
        compiled_files = {}
        mime_type = 'application/pdf' if output_format == "PDF" else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ext = '.pdf' if output_format == "PDF" else '.docx'
        
        # Compile individual units
        if compile_type in ["Separate Unit Files", "Both (Separate + Complete)"]:
            st.subheader("🔨 Compiling Individual Units")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, unit in enumerate(st.session_state.approved_outline):
                status_text.text(f"Compiling Unit {unit['unit_number']}: {unit['unit_title'][:40]}...")
                
                with st.spinner(f"Compiling Unit {unit['unit_number']}..."):
                    if output_format == "PDF":
                        file_buffer = compile_unit_pdf(unit, course_info, st.session_state.content)
                    else:
                        file_buffer = compile_unit_docx(unit, course_info, st.session_state.content)
                    
                    if file_buffer:
                        # Safe filename
                        safe_title = re.sub(r'[^\w\s-]', '', unit['unit_title'])[:30]
                        filename = f"Unit_{unit['unit_number']}_{safe_title}{ext}"
                        
                        compiled_files[f"Unit_{unit['unit_number']}"] = {
                            'buffer': file_buffer,
                            'filename': filename
                        }
                        
                        st.success(f"✅ {output_format} compiled for Unit {unit['unit_number']}")
                        
                        # Upload to Google Drive
                        if upload_drive and gdrive_service and gdrive_folder_id:
                            file_buffer.seek(0)
                            with st.spinner(f"Uploading Unit {unit['unit_number']} to Drive..."):
                                link = upload_to_gdrive(gdrive_service, file_buffer, filename, gdrive_folder_id, mime_type)
                                if link:
                                    drive_links[f"Unit_{unit['unit_number']}"] = link
                                    st.success(f"📤 Uploaded to Google Drive")
                                else:
                                    st.warning("⚠️ Upload failed for this file")
                    else:
                        st.error(f"❌ Failed to compile Unit {unit['unit_number']}")
                
                progress_bar.progress((i + 1) / len(st.session_state.approved_outline))
            
            status_text.text("✅ All units compiled!")
        
        # Compile complete file
        if compile_type in ["Complete Course File", "Both (Separate + Complete)"]:
            st.subheader("🔨 Compiling Complete Course File")
            
            with st.spinner("Compiling complete course file... This may take a minute..."):
                if output_format == "PDF":
                    file_buffer = compile_complete_pdf(
                        st.session_state.approved_outline,
                        course_info,
                        st.session_state.content
                    )
                else:
                    file_buffer = compile_complete_docx(
                        st.session_state.approved_outline,
                        course_info,
                        st.session_state.content
                    )
                
                if file_buffer:
                    filename = f"{st.session_state.course_code}_Complete_Curriculum{ext}"
                    compiled_files['Complete'] = {
                        'buffer': file_buffer,
                        'filename': filename
                    }
                    st.success(f"✅ Complete {output_format} file compiled")
                    
                    # Upload to Google Drive
                    if upload_drive and gdrive_service and gdrive_folder_id:
                        file_buffer.seek(0)
                        with st.spinner("Uploading complete file to Drive..."):
                            link = upload_to_gdrive(gdrive_service, file_buffer, filename, gdrive_folder_id, mime_type)
                            if link:
                                drive_links['Complete'] = link
                                st.success("📤 Complete file uploaded to Google Drive")
                            else:
                                st.warning("⚠️ Upload failed for complete file")
                else:
                    st.error("❌ Failed to compile complete file")
        
        st.success("🎉 Compilation Complete!")
        
        st.divider()
        
        # ===== Download Links =====
        st.subheader("📥 Download Files & Google Drive Links")
        
        if not compiled_files:
            st.error("❌ No files were compiled successfully")
        else:
            for key, data in compiled_files.items():
                st.write("---")
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**📄 {data['filename']}**")
                    file_size = len(data['buffer'].getvalue()) / 1024  # KB
                    st.caption(f"Size: {file_size:.1f} KB")
                
                with col2:
                    if key in drive_links:
                        st.markdown(f"[🔗 Open in Google Drive]({drive_links[key]})")
                    else:
                        st.write("No Drive link")
                
                with col3:
                    data['buffer'].seek(0)
                    st.download_button(
                        "⬇️ Download",
                        data=data['buffer'].getvalue(),
                        file_name=data['filename'],
                        mime=mime_type,
                        key=f"dl_{key}",
                        use_container_width=True
                    )
        
        st.divider()
        
        # ===== Navigation Buttons =====
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Recompile", use_container_width=True, key="recompile"):
                st.rerun()
        
        with col2:
            if st.button("← Back to Content", use_container_width=True, key="back_final"):
                st.session_state.step = 'content_generation'
                st.rerun()
        
        with col3:
            if st.button("🏠 New Project", use_container_width=True, key="new_proj"):
                # Save important data
                api_key = st.session_state.api_key
                folder_url = st.session_state.gdrive_folder_url
                
                # Clear everything
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # Reinitialize
                initialize_session_state()
                st.session_state.api_key = api_key
                st.session_state.gdrive_folder_url = folder_url
                
                st.success("✅ Ready for new project!")
                time.sleep(1)
                st.rerun()

# ============================================================================
# SIDEBAR STATUS DISPLAY
# ============================================================================

def show_sidebar_status():
    """Display current status in sidebar"""
    with st.sidebar:
        st.header("📊 Project Status")
        
        # Course info
        if st.session_state.course_title:
            st.write(f"**Course:** {st.session_state.course_title[:40]}")
            st.write(f"**Code:** {st.session_state.course_code}")
            st.write(f"**Credits:** {st.session_state.credits}")
        
        st.divider()
        
        # Outline status
        if st.session_state.get('approved_outline'):
            units = len(st.session_state.approved_outline)
            sections = sum(len(u.get('sections', [])) for u in st.session_state.approved_outline)
            st.metric("📚 Units", units)
            st.metric("📝 Sections", sections)
        
        # Content status
        if st.session_state.content:
            total_words = sum(len(c.split()) for c in st.session_state.content.values())
            st.metric("✍️ Words Generated", f"{total_words:,}")
            st.metric("🖼️ Images Added", len(st.session_state.images))
        
        st.divider()
        
        # Current step
        step_names = {
            'syllabus_upload': '1️⃣ Syllabus Upload',
            'configuration': '2️⃣ Configuration',
            'outline_generation': '3️⃣ Outline',
            'content_generation': '4️⃣ Content Generation',
            'compilation': '5️⃣ Compilation'
        }
        current_step = step_names.get(st.session_state.step, 'Unknown')
        st.info(f"**Current Step:**\n{current_step}")
        
        st.divider()
        
        # System status
        st.caption("**System Status:**")
        st.caption(f"PDF: {'✅' if REPORTLAB_AVAILABLE else '❌'}")
        st.caption(f"DOCX: {'✅' if DOCX_AVAILABLE else '❌'}")
        st.caption(f"Drive: {'✅' if GDRIVE_AVAILABLE else '❌'}")
        st.caption(f"PyPDF2: {'✅' if PYPDF2_AVAILABLE else '❌'}")

# ============================================================================
# Phase 4 Part 2 Complete
# ============================================================================
print("Phase 4 Part 2: Content Generation, Compilation, and Sidebar loaded successfully")"""
AI CURRICULUM GENERATOR - COMPLETE APPLICATION
================================================
FINAL INTEGRATION - ALL PHASES COMBINED

To use this application, you need to combine all 4 phase files:
1. Phase 1: Imports and Configuration
2. Phase 2: Helper Functions
3. Phase 3: Content Generation and Compilation
4. Phase 4: UI Pages (Part 1 and Part 2)
5. This file: Main Application

Features:
Fixed LaTeX equation rendering
Automatic timestamped Google Drive subfolders
Image upload for each section
AI-powered image prompt generation
Complete PDF/DOCX compilation
Enhanced error handling
"""

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="AI Curriculum Generator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🎓 AI Curriculum Generator")
    st.caption("Professional academic materials with eGyankosh standards | Powered by Grok AI")
    
    # Initialize session state
    initialize_session_state()
    
    # Show navigation
    show_navigation()
    
    # Route to appropriate page based on current step
    step = st.session_state.step
    
    if step == 'syllabus_upload':
        show_syllabus_upload_page()
    
    elif step == 'configuration':
        show_configuration_page()
    
    elif step == 'outline_generation':
        show_outline_page()
    
    elif step == 'content_generation':
        show_content_generation_page()
    
    elif step == 'compilation':
        show_compilation_page()
    
    else:
        st.error(f"❌ Unknown step: {step}")
        st.session_state.step = 'syllabus_upload'
        st.rerun()
    
    # Show sidebar status
    show_sidebar_status()
    
    # Footer
    st.divider()
    with st.expander("ℹ️ About This Application", expanded=False):
        st.markdown("""
        ### AI Curriculum Generator
        
        **Features:**
        - PDF syllabus extraction
        - AI-powered content generation
        - Image upload and prompt generation
        - Professional PDF/DOCX compilation
        - Google Drive auto-upload with timestamped subfolders
        - Academic outcome mapping (PEO/PO/CO/PSO)
        - Fixed LaTeX equation rendering
        
        **Technologies:**
        - Grok AI (grok-2-1212)
        - ReportLab (PDF generation)
        - python-docx (DOCX generation)
        - Google Drive API
        - Streamlit
        """)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()

# ============================================================================
# INSTALLATION REQUIREMENTS
# ============================================================================
"""
Required packages - install with pip:

pip install streamlit
pip install requests
pip install pillow
pip install PyPDF2
pip install reportlab
pip install python-docx
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install google-api-python-client

Or use requirements.txt:

streamlit>=1.29.0
requests>=2.31.0
pillow>=10.0.0
PyPDF2>=3.0.0
reportlab>=4.0.0
python-docx>=1.1.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.108.0
"""

# ============================================================================
# HOW TO RUN
# ============================================================================
"""
1. Save all phases to a single file named 'curriculum_generator.py':
   - Copy Phase 1 content
   - Copy Phase 2 content
   - Copy Phase 3 content
   - Copy Phase 4 Part 1 content
   - Copy Phase 4 Part 2 content
   - Copy this final integration code

2. Install requirements:
   pip install -r requirements.txt

3. Run the application:
   streamlit run curriculum_generator.py

4. Open browser at:
   http://localhost:8501

5. Configure Google Drive:
   - Go to your Google Drive folder
   - Share with: curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com
   - Give Editor permissions
   - Copy folder URL and paste in app
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
Common Issues and Solutions:

1. **LaTeX equations not rendering:**
   - Fixed! Now converts LaTeX to Unicode symbols
   - Example: \leq becomes ≤

2. **Google Drive permission error:**
   - Share folder with service account email
   - Give Editor permissions
   - Wait 1-2 minutes for permissions to propagate

3. **API errors:**
   - Check API key starts with 'xai-'
   - Test API using the test button
   - Check internet connection

4. **PDF compilation fails:**
   - Check ReportLab is installed
   - Try DOCX format instead
   - Check error logs in UI

5. **Images not appearing:**
   - Ensure images are PNG/JPG/JPEG
   - Check file size < 5MB
   - Upload one image at a time

6. **Content too short:**
   - Check API logs in UI
   - Increase max_tokens if needed
   - Check API rate limits
"""

# ============================================================================
# COMPLETE APPLICATION - READY TO USE
# ============================================================================
print("✅ All components loaded successfully!")
print("🎓 AI Curriculum Generator ready!")
print("🚀 Run with: streamlit run curriculum_generator.py")
