"""
COMPLETE AI CURRICULUM GENERATOR - SYNTAX FIXED & ENHANCED
================================================
All features integrated with proper syntax
Enhancements: Fixed page estimation, added image upload per section, better PDF formatting with bold/italics,
document heading/logo (header), fixed Drive uploads, options for separate/combined outputs, DOCX for editable Google Docs
"""

import streamlit as st
import requests
import json
import time
import os
import re
from datetime import datetime
from io import BytesIO
from PIL import Image as PilImage  # For logo handling

# PDF imports
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Google Drive imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

# ReportLab imports
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

# DOCX imports for editable output
try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Configuration
DEFAULT_API_KEY = "xai-6QJwG3u6540lVZyXbFBArvLQ43ZyJsrnq65pyCWhxh5zXqNvtwe6LdTURbTwvE2sA3Uxlb9gn82Vamgu"
API_URL = "https://api.x.ai/v1/chat/completions"

# Google Drive Service Account JSON
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

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'step': 'syllabus_upload',
        'api_key': DEFAULT_API_KEY,
        'course_title': 'Organizational Behaviour',
        'course_code': 'MBA101',
        'credits': 3,
        'target_audience': 'Postgraduate (MBA)',
        'num_units': 4,
        'sections_per_unit': 8,
        'sections_per_unit': 8,
        'program_objectives': '',
        'program_outcomes': '',
        'course_outcomes': '',
        'specialized_outcomes': '',
        'use_egyankosh_style': True,
        'gdrive_folder_url': '',
        'gdrive_folder_id': '',
        'logo': None,
        'document_heading': '',
        'content': {},
        'images': {},  # section_key: uploaded_file
        'paused': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_api_headers():
    """Get API headers"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.api_key}"
    }

def make_api_call(messages, retries=3, timeout=120, max_tokens=2000):
    """Make API call with detailed logging"""
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
            
            # Show response headers
            if response.headers:
                st.write(f"⏱️ Response time: {response.elapsed.total_seconds():.2f}s")
            
            response.raise_for_status()
            result = response.json()
            
            # Detailed response analysis
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                
                # Analyze response
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

def extract_pdf_text(pdf_file):
    """Extract text from PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting PDF: {str(e)}")
        return None

def parse_syllabus_structure(text):
    """Parse syllabus structure"""
    structure = {'course_info': {}, 'units': []}
    
    # Extract course info
    patterns = {
        'title': r'(?:Course|Subject)\s*(?:Title|Name)?\s*:?\s*(.+)',
        'code': r'(?:Course|Subject)\s*Code\s*:?\s*([A-Z0-9]+)',
        'credits': r'Credits?\s*:?\s*(\d+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            structure['course_info'][key] = match.group(1).strip()
    
    # Extract units
    unit_pattern = r'UNIT[\s-]*(\d+)\s*:?\s*(.+?)(?=UNIT[\s-]*\d+|$)'
    units = re.finditer(unit_pattern, text, re.IGNORECASE | re.DOTALL)
    
    for unit_match in units:
        unit_num = unit_match.group(1)
        unit_content = unit_match.group(2)
        
        title_match = re.search(r'^(.+?)(?:\n|$)', unit_content)
        unit_title = title_match.group(1).strip() if title_match else f"Unit {unit_num}"
        
        topics = []
        lines = unit_content.split('\n')
        for line in lines:
            if re.match(r'^\s*[\d.]+\s+(.+?)$', line):
                topic = re.match(r'^\s*[\d.]+\s+(.+?)$', line).group(1).strip()
                if 5 < len(topic) < 200:
                    topics.append(topic)
        
        structure['units'].append({
            'unit_number': int(unit_num),
            'unit_title': unit_title,
            'topics': topics
        })
    
    return structure

def setup_google_drive_connection():
    """Setup Google Drive"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            GDRIVE_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Google Drive connection failed: {str(e)}")
        return None

def extract_folder_id_from_url(url):
    """Extract folder ID from URL"""
    patterns = [r'folders/([a-zA-Z0-9_-]+)', r'id=([a-zA-Z0-9_-]+)']
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    if re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url
    
    return None

def create_or_use_folder(service, folder_name, parent_id=None):
    """Create or use existing folder"""
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        st.error(f"Error creating folder: {str(e)}")
        return None

def upload_to_gdrive(service, file_buffer, filename, folder_id, mime_type='application/pdf'):
    """Upload file to Google Drive"""
    try:
        file_metadata = {'name': filename, 'parents': [folder_id]}
        media = MediaIoBaseUpload(file_buffer, mimetype=mime_type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def clean_text_for_pdf(text):
    """Clean text for PDF with HTML tags for bold/italic"""
    if not text:
        return ""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    return text

def generate_content(section_info, course_context):
    """Generate content"""
    system_prompt = f"""You are an expert academic content developer for {course_context['target_audience']}.

Generate comprehensive content following eGyankosh standards:
- 4-5 pages (1,000-1,500 words)
- Grade 5 English, Academic tone
- Readability: 10-12
- Suggest 1-2 relevant image placements with descriptions (e.g., "Image: Diagram of organizational structure")

STRUCTURE:
1. Introduction
2. Learning Objectives (Bloom's Taxonomy mapped)
3. Detailed Content
4. Examples & Case Studies
5. CHECK YOUR PROGRESS (5-7 questions)
6. Summary
7. Key Terms

Map to:
- PO: {course_context.get('program_outcomes', 'N/A')}
- CO: {course_context.get('course_outcomes', 'N/A')}
- PSO: {course_context.get('specialized_outcomes', 'N/A')}"""

    user_prompt = f"""Write content for:
Topic: {section_info['section_number']} {section_info['section_title']}
Course: {course_context['course_title']}
Description: {section_info['description']}

Include definitions, examples, case studies, practical applications, and **bold key terms**. Use *italics* for emphasis."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return make_api_call(messages, max_tokens=2000)

def add_header_footer(doc, canvas, course_info, logo=None):
    """Add header and footer to PDF"""
    canvas.saveState()
    
    # Document heading
    heading = st.session_state.get('document_heading', course_info['course_title'])
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(72, doc.height - 72, heading)
    
    # Logo in header (top right)
    if logo:
        try:
            logo_bytes = logo.read()
            logo_buffer = BytesIO(logo_bytes)
            canvas.drawImage(logo_buffer, doc.width - 2*inch, doc.height - 1*inch, width=1*inch, height=0.5*inch, preserveAspectRatio=True)
        except:
            pass  # Ignore logo error
    
    # Footer
    canvas.setFont("Helvetica", 10)
    canvas.drawString(doc.width / 2 - 100, 72, f"Page {doc.page}")
    canvas.drawString(72, 72, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    
    canvas.restoreState()

def compile_unit_pdf(unit_data, course_info, content_dict):
    """Compile unit PDF with enhanced formatting"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
        topMargin=1.2*inch, bottomMargin=1*inch,
        onFirstPage=lambda canvas, doc: add_header_footer(doc, canvas, course_info, st.session_state.logo),
        onLaterPages=lambda canvas, doc: add_header_footer(doc, canvas, course_info, st.session_state.logo)
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Enhanced styles
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=24,
        textColor=colors.HexColor('#1f77b4'), alignment=TA_CENTER, fontName='Helvetica-Bold',
        spaceAfter=30, spaceBefore=20
    )
    
    section_style = ParagraphStyle(
        'Section', parent=styles['Heading2'], fontSize=16,
        textColor=colors.HexColor('#2c3e50'), fontName='Helvetica-Bold',
        spaceAfter=12, spaceBefore=12, leftIndent=0
    )
    
    subsection_style = ParagraphStyle(
        'Subsection', parent=styles['Heading3'], fontSize=14,
        textColor=colors.HexColor('#34495e'), fontName='Helvetica-Bold',
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'Body', parent=styles['BodyText'], fontSize=11, alignment=TA_JUSTIFY, 
        spaceAfter=8, leading=14, fontName='Helvetica'
    )
    
    # Cover page
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph(f"UNIT {unit_data['unit_number']}", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(unit_data['unit_title'].upper(), title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Decorative line
    line_table = Table([['']], colWidths=[6.5*inch])
    line_table.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1f77b4'))]))
    story.append(line_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(course_info.get('course_title', ''), styles['Heading3']))
    story.append(Paragraph(f"Course Code: {course_info.get('course_code', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"Credits: {course_info.get('credits', 3)}", styles['Normal']))
    story.append(PageBreak())
    
    # Content sections
    for section in unit_data.get('sections', []):
        sec_key = f"{section['section_number']} {section['section_title']}"
        story.append(Paragraph(f"<b>{sec_key}</b>", section_style))
        story.append(line_table.copy())  # Line under section
        story.append(Spacer(1, 0.2*inch))
        
        content = content_dict.get(sec_key, "[Not generated]")
        image = st.session_state.images.get(sec_key)
        
        # Add image if available
        if image:
            try:
                img_buffer = BytesIO(image.read())
                story.append(Image(img_buffer, width=4*inch, height=2*inch))
                story.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        lines = content.split('\n')
        in_subsection = False
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            
            if 'CHECK YOUR PROGRESS' in line.upper():
                progress_para = Paragraph("<b>CHECK YOUR PROGRESS</b>", subsection_style)
                story.append(progress_para)
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('## '):  # Subsection
                clean_line = clean_text_for_pdf(line[3:])
                story.append(Paragraph(clean_line, subsection_style))
                in_subsection = True
            elif line.startswith(('*', '-', '•')):
                clean_line = clean_text_for_pdf(re.sub(r'^[\*\-•]\s*', '', line))
                story.append(Paragraph(f"• {clean_line}", body_style))
            else:
                clean_line = clean_text_for_pdf(line)
                if len(clean_line) > 3:
                    try:
                        story.append(Paragraph(clean_line, body_style))
                    except:
                        pass
        
        story.append(Spacer(1, 0.5*inch))
        story.append(PageBreak())
    
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"PDF error: {str(e)}")
        return None

def compile_complete_pdf(outline, course_info, content_dict):
    """Compile complete course PDF"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
        topMargin=1.2*inch, bottomMargin=1*inch,
        onFirstPage=lambda canvas, doc: add_header_footer(doc, canvas, course_info, st.session_state.logo),
        onLaterPages=lambda canvas, doc: add_header_footer(doc, canvas, course_info, st.session_state.logo)
    )
    
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=28, alignment=TA_CENTER, spaceAfter=40)
    
    # Title page
    story.append(Paragraph(course_info['course_title'], title_style))
    story.append(Paragraph(f"Course Code: {course_info['course_code']} | Credits: {course_info['credits']}", styles['Normal']))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Complete Curriculum", styles['Heading1']))
    story.append(PageBreak())
    
    # Units
    for unit in outline:
        story.append(Paragraph(f"UNIT {unit['unit_number']}: {unit['unit_title']}", styles['Heading1']))
        story.append(PageBreak())
        
        for section in unit.get('sections', []):
            sec_key = f"{section['section_number']} {section['section_title']}"
            story.append(Paragraph(sec_key, styles['Heading2']))
            
            content = content_dict.get(sec_key, "[Not generated]")
            image = st.session_state.images.get(sec_key)
            
            if image:
                try:
                    img_buffer = BytesIO(image.read())
                    story.append(Image(img_buffer, width=4*inch, height=2*inch))
                except:
                    pass
            
            clean_content = clean_text_for_pdf(content)
            story.append(Paragraph(clean_content, styles['Normal']))
            story.append(PageBreak())
    
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Complete PDF error: {str(e)}")
        return None

def compile_unit_docx(unit_data, course_info, content_dict):
    """Compile unit as editable DOCX"""
    if not DOCX_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = Document()
    
    # Styles
    styles = doc.styles
    try:
        title_style = styles.add_style('CustomTitle', WD_STYLE_TYPE.PARAGRAPH)
        title_style.font.name = 'Calibri'
        title_style.font.size = Pt(24)
        title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    except:
        pass
    
    # Title
    title = doc.add_heading(f"UNIT {unit_data['unit_number']}: {unit_data['unit_title']}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph(f"Course: {course_info['course_title']} | Code: {course_info['course_code']} | Credits: {course_info['credits']}")
    doc.add_page_break()
    
    # Content
    for section in unit_data.get('sections', []):
        sec_key = f"{section['section_number']} {section['section_title']}"
        sec_heading = doc.add_heading(sec_key, level=1)
        
        content = content_dict.get(sec_key, "[Not generated]")
        
        # Add image if available
        image = st.session_state.images.get(sec_key)
        if image:
            try:
                img_bytes = image.read()
                doc.add_picture(BytesIO(img_bytes), width=Inches(4))
            except:
                pass
        
        # Add text, simple bold/italic parsing
        for line in content.split('\n'):
            line = line.strip()
            if line:
                p = doc.add_paragraph(line)
                # Basic bold: if **text**, but for simplicity, assume clean_text_for_pdf output
                if '**' in line:
                    # Run bold
                    for match in re.finditer(r'\*\*(.+?)\*\*', line):
                        inline = p.add_run(match.group(1))
                        inline.bold = True
        
        doc.add_page_break()
    
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def compile_complete_docx(outline, course_info, content_dict):
    """Compile complete as DOCX"""
    if not DOCX_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = Document()
    
    title = doc.add_heading(course_info['course_title'], 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Code: {course_info['course_code']} | Credits: {course_info['credits']}")
    doc.add_page_break()
    
    for unit in outline:
        unit_heading = doc.add_heading(f"UNIT {unit['unit_number']}: {unit['unit_title']}", level=1)
        
        for section in unit.get('sections', []):
            sec_key = f"{section['section_number']} {section['section_title']}"
            doc.add_heading(sec_key, level=2)
            
            content = content_dict.get(sec_key, "[Not generated]")
            image = st.session_state.images.get(sec_key)
            
            if image:
                try:
                    img_bytes = image.read()
                    doc.add_picture(BytesIO(img_bytes), width=Inches(4))
                except:
                    pass
            
            doc.add_paragraph(content)
            doc.add_page_break()
    
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def create_default_outline(num_units, sections_per_unit):
    """Create default outline"""
    outline = []
    
    base_topics = [
        {"title": "Introduction and Foundations", "sections": [
            ("Introduction", "Overview"), ("Objectives", "Goals"),
            ("Meaning", "Definitions"), ("History", "Evolution"),
            ("Approaches", "Theories"), ("Applications", "Uses"),
            ("Importance", "Relevance"), ("Goals", "Objectives")
        ]},
        {"title": "Core Concepts", "sections": [
            ("Concept 1", "First topic"), ("Concept 2", "Second topic"),
            ("Concept 3", "Third topic"), ("Concept 4", "Fourth topic"),
            ("Concept 5", "Fifth topic"), ("Concept 6", "Sixth topic"),
            ("Concept 7", "Seventh topic"), ("Concept 8", "Eighth topic")
        ]}
    ]
    
    for i in range(num_units):
        unit_num = i + 1
        unit_title = base_topics[i % len(base_topics)]["title"]
        section_data = base_topics[i % len(base_topics)]["sections"]
        
        sections = []
        for j in range(min(sections_per_unit, len(section_data))):
            sec_title, sec_desc = section_data[j]
            sections.append({
                "section_number": f"{unit_num}.{j+1}",
                "section_title": sec_title,
                "description": sec_desc
            })
        
        outline.append({
            "unit_number": unit_num,
            "unit_title": unit_title,
            "sections": sections
        })
    
    return outline

def show_syllabus_upload_page():
    """Syllabus upload page"""
    st.header("📄 Step 1: Syllabus Upload")
    
    choice = st.radio("Choose:", ["Upload Syllabus", "Skip"], key="upload_choice")
    
    if choice == "Upload Syllabus":
        if PYPDF2_AVAILABLE:
            uploaded = st.file_uploader("Upload PDF", type=['pdf'], key="syllabus_file")
            
            if uploaded:
                with st.spinner("Extracting..."):
                    text = extract_pdf_text(uploaded)
                    
                    if text:
                        st.success("✅ Extracted!")
                        structure = parse_syllabus_structure(text)
                        st.session_state.extracted_structure = structure
                        
                        if structure['units']:
                            st.success(f"Found {len(structure['units'])} units")
                            
                            for unit in structure['units']:
                                with st.expander(f"Unit {unit['unit_number']}: {unit['unit_title']}"):
                                    for i, topic in enumerate(unit['topics'], 1):
                                        st.write(f"{i}. {topic}")
                            
                            if st.checkbox("✅ Looks good"):
                                if st.button("Continue", type="primary"):
                                    st.session_state.step = 'configuration'
                                    st.rerun()
        else:
            st.error("PyPDF2 not installed")
            if st.button("Continue Anyway"):
                st.session_state.step = 'configuration'
                st.rerun()
    else:
        if st.button("Continue", type="primary"):
            st.session_state.step = 'configuration'
            st.rerun()

def show_configuration_page():
    """Configuration page"""
    st.header("⚙️ Step 2: Configuration")
    
    # API
    st.subheader("🔑 API Configuration")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            "Grok API Key",
            value=st.session_state.api_key,
            type="password",
            key="api_key_input",
            help="Your Grok API key from x.ai"
        )
        st.session_state.api_key = api_key
        
        if api_key and api_key.startswith('xai-'):
            st.success("✅ Valid API key format")
        else:
            st.warning("⚠️ API key should start with 'xai-'")
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
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
                    
                    # Quality checks
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
                    st.error("❌ API test failed - check logs above for details")
                    st.error("🔍 Common issues:")
                    st.error("   - Invalid API key")
                    st.error("   - Rate limiting")
                    st.error("   - Network connection")
                    st.error("   - API service down")
    
    # Course details
    st.subheader("Course Details")
    
    extracted = st.session_state.get('extracted_structure', {})
    course_info = extracted.get('course_info', {})
    
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", value=course_info.get('title', st.session_state.course_title), key="title_input")
        st.session_state.course_title = title
        
        code = st.text_input("Code", value=course_info.get('code', st.session_state.course_code), key="code_input")
        st.session_state.course_code = code
    
    with col2:
        credits = st.number_input("Credits", min_value=1, max_value=10, value=st.session_state.credits, key="credits_input")
        st.session_state.credits = credits
        
        audience = st.selectbox("Audience", ["Postgraduate (MBA)", "Undergraduate"], key="audience_select")
        st.session_state.target_audience = audience
    
    # Document heading and logo
    st.subheader("📄 Document Customization")
    document_heading = st.text_input("Document Header (Optional)", value=st.session_state.document_heading, key="doc_heading")
    st.session_state.document_heading = document_heading
    
    logo = st.file_uploader("Upload Logo (for header)", type=['png', 'jpg', 'jpeg'], key="logo_uploader")
    if logo:
        st.session_state.logo = logo
        st.success("✅ Logo uploaded")
    elif st.session_state.logo:
        st.info("✅ Logo from previous session")
    
    # Academic mappings
    st.subheader("🎯 Academic Mappings (Optional)")
    st.info("💡 These mappings enhance content quality and alignment. Leave blank if not needed.")
    
    with st.expander("ℹ️ What are PEO, PO, CO, PSO?", expanded=False):
        st.markdown("""
        **Program Educational Objectives (PEO):** What students can do after completing the entire program
        
        **Program Outcomes (PO):** Skills and knowledge students gain from the program
        - Example: PO1: Critical thinking, PO2: Communication skills, PO3: Ethical awareness
        
        **Course Learning Objectives/Outcomes (CLO/CO):** What students learn in THIS specific course
        - Example: CO1: Understand OB concepts [Bloom: Understand], CO2: Apply leadership theories [Bloom: Apply]
        
        **Specialized Program Outcomes (PSO):** Specialized skills specific to the program (e.g., MBA-specific)
        - Example: PSO1: Strategic management, PSO2: Business analytics
        """)
    
    peo = st.text_area(
        "Program Educational Objectives (PEO)",
        value=st.session_state.program_objectives,
        placeholder="Example:\n- Develop strategic leadership capabilities\n- Foster analytical decision-making skills\n- Build effective communication abilities\n\n(Leave blank if not required)",
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
            placeholder="Example:\nPO1: Critical thinking and problem-solving\nPO2: Effective communication\nPO3: Ethical decision-making\nPO4: Teamwork and collaboration\n\n(Leave blank if not required)",
            help="Skills and knowledge from the program",
            key="po_input",
            height=150
        )
        st.session_state.program_outcomes = po
    
    with col2:
        pso = st.text_area(
            "Specialized Program Outcomes (PSO)",
            value=st.session_state.specialized_outcomes,
            placeholder="Example:\nPSO1: Advanced managerial skills\nPSO2: Strategic HR management\nPSO3: Organizational leadership\nPSO4: Change management expertise\n\n(Leave blank if not required)",
            help="Specialized skills for this specific program",
            key="pso_input",
            height=150
        )
        st.session_state.specialized_outcomes = pso
    
    co = st.text_area(
        "Course Learning Objectives & Outcomes (CLO/CO)",
        value=st.session_state.course_outcomes,
        placeholder="Example:\nCO1: Understand key organizational behaviour concepts [Bloom: Understand]\nCO2: Apply OB theories to real-world scenarios [Bloom: Apply]\nCO3: Analyze organizational dynamics and culture [Bloom: Analyze]\nCO4: Evaluate organizational strategies and interventions [Bloom: Evaluate]\n\n(Leave blank if not required)",
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
    
    # Content Structure (only if no syllabus uploaded)
    if not st.session_state.get('extracted_structure'):
        st.subheader("📚 Content Structure")
        st.info("💡 Define how many units and topics you want. AI will generate relevant content for each.")
        
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
                "Topics per Unit",
                min_value=3,
                max_value=15,
                value=st.session_state.get('sections_per_unit', 8),
                help="How many topics/sections in each unit",
                key="sections_per_unit_config"
            )
            st.session_state.sections_per_unit = sections_per_unit
        
        total_sections = num_units * sections_per_unit
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sections", total_sections)
        with col2:
            st.metric("Est. Pages", f"~{total_sections * 5}")  # 5 pages per section estimate
        
        st.caption(f"💡 AI will generate {num_units} units with {sections_per_unit} topics each")
    else:
        st.info("✅ Using structure from uploaded syllabus")
    
    # Google Drive
    st.subheader("Google Drive")
    
    if GDRIVE_AVAILABLE:
        folder_url = st.text_input("Folder URL/ID", value=st.session_state.gdrive_folder_url, key="folder_input")
        st.session_state.gdrive_folder_url = folder_url
        
        if folder_url:
            folder_id = extract_folder_id_from_url(folder_url)
            if folder_id:
                st.session_state.gdrive_folder_id = folder_id
                st.success(f"✅ ID: {folder_id}")
                st.info("Share with: curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.step = 'syllabus_upload'
            st.rerun()
    with col2:
        if st.button("Next →", type="primary"):
            st.session_state.step = 'outline_generation'
            st.rerun()

def show_outline_page():
    """Outline page - AI generated ONLY"""
    st.header("📋 Step 3: Course Outline")
    
    # Check if we need to generate outline
    if 'outline' not in st.session_state or st.session_state.outline is None:
        
        # Check if extracted from syllabus
        extracted = st.session_state.get('extracted_structure')
        
        if extracted and extracted.get('units'):
            st.info("✅ Using syllabus structure")
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
            
        else:
            # MUST generate with AI - NO DEFAULTS
            st.warning("⚠️ No outline generated yet")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 Generate with AI", type="primary", use_container_width=True, key="generate_ai_outline"):
                    with st.spinner("🤖 AI is creating your course outline..."):
                        generated_outline = generate_outline_with_ai()
                        
                        if generated_outline:
                            st.session_state.outline = generated_outline
                            st.success("✅ Outline generated!")
                            st.rerun()
                        else:
                            st.error("❌ AI generation failed. Please try again or check your API key.")
                            return
            
            with col2:
                if st.button("← Back to Configuration", use_container_width=True, key="back_no_outline"):
                    st.session_state.step = 'configuration'
                    st.rerun()
            
            st.info("💡 Click 'Generate with AI' to create a custom outline based on your course details")
            return
    
    # Display outline
    outline = st.session_state.outline
    total_sections = sum(len(u.get('sections', [])) for u in outline)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Units", len(outline))
    with col2:
        st.metric("Sections", total_sections)
    with col3:
        st.metric("Est. Pages", f"~{total_sections * 5}")
    
    st.divider()
    
    # Edit outline
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
    
    st.subheader("✏️ Edit Outline")
    st.caption("Click any cell to edit directly")
    edited = st.data_editor(rows, num_rows="dynamic", use_container_width=True, height=400, key="outline_editor_unique")
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back", use_container_width=True, key="back_from_outline"):
            st.session_state.step = 'configuration'
            st.rerun()
    
    with col2:
        if st.button("🔄 Regenerate", use_container_width=True, key="regen_outline_btn"):
            # Clear outline and regenerate with AI
            st.session_state.outline = None
            st.rerun()
    
    with col3:
        if st.button("✅ Approve & Generate Content", type="primary", use_container_width=True, key="approve_outline_btn"):
            # Convert edited data back to outline format
            approved = []
            current = None
            
            # Handle both list and dict formats
            if isinstance(edited, dict):
                edited = edited.get('data', edited)
            
            for row in edited:
                unit_num = row.get('Unit') if isinstance(row, dict) else row['Unit']
                unit_title = row.get('Unit Title') if isinstance(row, dict) else row['Unit Title']
                section_num = row.get('Section') if isinstance(row, dict) else row['Section']
                section_title = row.get('Section Title') if isinstance(row, dict) else row['Section Title']
                description = row.get('Description') if isinstance(row, dict) else row['Description']
                
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
            st.session_state.step = 'content_generation'
            st.rerun()

def generate_outline_with_ai():
    """Generate outline using AI - NO DEFAULTS"""
    
    num_units = st.session_state.get('num_units', 4)
    sections_per_unit = st.session_state.get('sections_per_unit', 8)
    
    st.write(f"🎯 Generating {num_units} units with {sections_per_unit} sections each...")
    
    # Build PO/CO/PSO context
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
            
            # Remove any leading/trailing whitespace
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
                    for unit in parsed_outline[:2]:  # Show first 2 units
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

def show_content_generation_page():
    """Content generation page"""
    st.header("✍️ Step 4: Content Generation")
    
    if 'approved_outline' not in st.session_state:
        st.error("No outline")
        if st.button("← Back", key="back_no_outline_gen"):
            st.session_state.step = 'outline_generation'
            st.rerun()
        return
    
    # Initialize
    if 'content' not in st.session_state or not st.session_state.content:
        st.session_state.content = {}
        st.session_state.sections_to_process = []
        st.session_state.generation_start_time = time.time()
        
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
    
    # Progress
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Completed", f"{completed}/{total}")
    with col2:
        progress = (completed / total * 100) if total > 0 else 0
        st.metric("Progress", f"{progress:.0f}%")
    with col3:
        st.metric("Remaining", total - completed)
    with col4:
        if completed > 0:
            elapsed = time.time() - st.session_state.generation_start_time
            avg = elapsed / completed
            eta = int((avg * (total - completed)) / 60)
            st.metric("ETA", f"~{eta}min")
    
    st.progress(completed / total if total > 0 else 0)
    
    # Generate
    if completed < total:
        current = st.session_state.sections_to_process[completed]
        section_key = f"{current['section_number']} {current['section_title']}"
        
        st.info(f"🤖 Generating: **{section_key}**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Description: {current['description']}")
        with col2:
            if st.button("⏸️ Pause", key="pause_gen"):
                st.session_state.paused = True
                st.rerun()
        
        if not st.session_state.paused:
            with st.spinner(f"Writing {completed + 1} of {total}..."):
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
                
                content = generate_content(current, context)
                
                if content and len(content.strip()) > 100:
                    st.session_state.content[section_key] = content
                    st.success(f"✅ Content generated for {section_key}")
                    
                    # Image upload for this section
                    uploaded_image = st.file_uploader(f"Upload image for {section_key} (optional)", type=['png', 'jpg', 'jpeg'], key=f"image_{completed}")
                    if uploaded_image:
                        st.session_state.images[section_key] = uploaded_image
                        st.success("✅ Image added")
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Generation failed")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Retry", key="retry_gen"):
                            st.rerun()
                    with col2:
                        if st.button("⏭️ Skip", key="skip_gen"):
                            st.session_state.content[section_key] = "[Skipped]"
                            st.rerun()
        else:
            st.warning("⏸️ Paused")
            if st.button("▶️ Resume", type="primary", key="resume_gen"):
                st.session_state.paused = False
                st.rerun()
    else:
        total_words = sum(len(c.split()) for c in st.session_state.content.values())
        est_pages = total_words // 300 + 1 if total_words > 0 else 0
        
        st.success("🎉 All Content Generated!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", f"{total_words:,}")
        with col2:
            st.metric("Sections", total)
        with col3:
            st.metric("Est. Pages", f"~{est_pages}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="back_from_gen"):
                st.session_state.step = 'outline_generation'
                st.rerun()
        with col2:
            if st.button("📄 Compile Outputs", type="primary", key="go_compile"):
                st.session_state.step = 'compilation'
                st.rerun()

def show_compilation_page():
    """Compilation page"""
    st.header("📄 Step 5: Compile Outputs")
    
    if 'content' not in st.session_state or not st.session_state.content:
        st.error("No content")
        if st.button("← Back", key="back_no_content"):
            st.session_state.step = 'content_generation'
            st.rerun()
        return
    
    if 'approved_outline' not in st.session_state:
        st.error("No outline")
        if st.button("← Back", key="back_no_outline_comp"):
            st.session_state.step = 'outline_generation'
            st.rerun()
        return
    
    # Summary
    st.subheader("Summary")
    
    total_sections = len(st.session_state.content)
    total_words = sum(len(c.split()) for c in st.session_state.content.values())
    est_pages = total_words // 300 + 1 if total_words > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Units", len(st.session_state.approved_outline))
    with col2:
        st.metric("Sections", total_sections)
    with col3:
        st.metric("Words", f"{total_words:,}")
    with col4:
        st.metric("Est. Pages", f"~{est_pages}")
    
    st.divider()
    
    # Options
    col1, col2 = st.columns(2)
    with col1:
        compile_type = st.radio("Output Type:", ["Unit Files", "Complete File", "Both"], index=2, key="compile_type")
    with col2:
        output_format = st.radio("Format:", ["PDF", "DOCX (Editable)"], index=0, key="output_format")
    
    upload_drive = False
    if GDRIVE_AVAILABLE and st.session_state.gdrive_folder_id:
        upload_drive = st.checkbox("📤 Upload to Google Drive (One-click for all)", value=True, key="upload_drive")
        if upload_drive:
            st.info("💡 DOCX files will be editable in Google Docs when uploaded")
    
    st.divider()
    
    if st.button("🔨 Start Compilation & Upload", type="primary", key="start_compile"):
        course_info = {
            'course_title': st.session_state.course_title,
            'course_code': st.session_state.course_code,
            'credits': st.session_state.credits,
            'target_audience': st.session_state.target_audience
        }
        
        # Setup Drive
        gdrive_service = None
        gdrive_folder_id = None
        drive_links = {}
        
        if upload_drive:
            with st.spinner("Connecting to Drive..."):
                gdrive_service = setup_google_drive_connection()
                if gdrive_service:
                    st.success("✅ Connected to Drive")
                    folder_name = f"{st.session_state.course_code}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    gdrive_folder_id = create_or_use_folder(
                        gdrive_service,
                        folder_name,
                        st.session_state.gdrive_folder_id
                    )
                    if gdrive_folder_id:
                        st.success(f"✅ Folder: {folder_name}")
                    else:
                        st.error("❌ Folder creation failed")
        
        # Compile
        compiled_files = {}
        mime_type = 'application/pdf' if output_format == "PDF" else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ext = '.pdf' if output_format == "PDF" else '.docx'
        
        if compile_type in ["Unit Files", "Both"]:
            st.subheader("Compiling Units")
            progress_bar = st.progress(0)
            
            for i, unit in enumerate(st.session_state.approved_outline):
                with st.spinner(f"Unit {unit['unit_number']}..."):
                    if output_format == "PDF":
                        file_buffer = compile_unit_pdf(unit, course_info, st.session_state.content)
                    else:
                        file_buffer = compile_unit_docx(unit, course_info, st.session_state.content)
                    
                    if file_buffer:
                        filename = f"Unit_{unit['unit_number']}_{unit['unit_title'].replace(' ', '_')[:30]}{ext}"
                        compiled_files[f"Unit_{unit['unit_number']}"] = {
                            'buffer': file_buffer,
                            'filename': filename
                        }
                        
                        st.success(f"✅ {output_format} for Unit {unit['unit_number']}")
                        
                        # Upload to Drive
                        if upload_drive and gdrive_service and gdrive_folder_id:
                            file_buffer.seek(0)
                            link = upload_to_gdrive(gdrive_service, file_buffer, filename, gdrive_folder_id, mime_type)
                            if link:
                                drive_links[f"Unit_{unit['unit_number']}"] = link
                                st.success(f"📤 Uploaded to Drive")
                
                progress_bar.progress((i + 1) / len(st.session_state.approved_outline))
        
        if compile_type in ["Complete File", "Both"]:
            st.subheader("Compiling Complete File")
            with st.spinner("Complete file..."):
                if output_format == "PDF":
                    file_buffer = compile_complete_pdf(st.session_state.approved_outline, course_info, st.session_state.content)
                else:
                    file_buffer = compile_complete_docx(st.session_state.approved_outline, course_info, st.session_state.content)
                
                if file_buffer:
                    filename = f"{st.session_state.course_code}_Complete_Curriculum{ext}"
                    compiled_files['Complete'] = {
                        'buffer': file_buffer,
                        'filename': filename
                    }
                    st.success(f"✅ {output_format} Complete file ready")
                    
                    # Upload to Drive
                    if upload_drive and gdrive_service and gdrive_folder_id:
                        file_buffer.seek(0)
                        link = upload_to_gdrive(gdrive_service, file_buffer, filename, gdrive_folder_id, mime_type)
                        if link:
                            drive_links['Complete'] = link
                            st.success("📤 Complete file uploaded to Drive")
        
        st.success("🎉 Compilation Complete!")
        st.divider()
        
        # Downloads and Drive links
        st.subheader("📥 Downloads & Drive Links")
        
        for key, data in compiled_files.items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{data['filename']}**")
            with col2:
                if key in drive_links:
                    st.markdown(f"[🔗 Open in Drive]({drive_links[key]})")
                else:
                    st.write("No Drive link")
            with col3:
                data['buffer'].seek(0)
                st.download_button(
                    "📥 Download",
                    data=data['buffer'].getvalue(),
                    file_name=data['filename'],
                    mime=mime_type,
                    key=f"dl_{key}"
                )
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Recompile", key="recompile"):
                st.rerun()
        with col2:
            if st.button("← Back", key="back_final"):
                st.session_state.step = 'content_generation'
                st.rerun()
        with col3:
            if st.button("🏠 New Project", key="new_proj"):
                api_key = st.session_state.api_key
                folder_url = st.session_state.gdrive_folder_url
                st.session_state.clear()
                initialize_session_state()
                st.session_state.api_key = api_key
                st.session_state.gdrive_folder_url = folder_url
                st.rerun()

def show_navigation():
    """Navigation"""
    steps = {
        'syllabus_upload': '1️⃣ Syllabus',
        'configuration': '2️⃣ Config',
        'outline_generation': '3️⃣ Outline',
        'content_generation': '4️⃣ Content',
        'compilation': '5️⃣ PDF'
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

def main():
    st.set_page_config(
        page_title="AI Curriculum Generator",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 AI Curriculum Generator")
    st.caption("Professional academic materials with eGyankosh standards")
    
    initialize_session_state()
    show_navigation()
    
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
        st.error("Unknown step")
        st.session_state.step = 'syllabus_upload'
        st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Status")
        
        if st.session_state.course_title:
            st.write(f"**Course:** {st.session_state.course_title[:40]}")
        
        if st.session_state.get('approved_outline'):
            units = len(st.session_state.approved_outline)
            sections = sum(len(u.get('sections', [])) for u in st.session_state.approved_outline)
            st.metric("Units", units)
            st.metric("Sections", sections)
        
        if st.session_state.content:
            total_words = sum(len(c.split()) for c in st.session_state.content.values())
            st.metric("Generated Words", f"{total_words:,}")
            st.metric("Images Added", len(st.session_state.images))
        
        st.divider()
        st.caption("✅ All features integrated & enhanced")
        st.caption(f"PDF: {'✅' if REPORTLAB_AVAILABLE else '❌'}")
        st.caption(f"DOCX: {'✅' if DOCX_AVAILABLE else '❌'}")
        st.caption(f"Drive: {'✅' if GDRIVE_AVAILABLE else '❌'}")

if __name__ == "__main__":
    main()
