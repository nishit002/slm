"""
COMPLETE AI CURRICULUM GENERATOR
=================================
All features integrated: Syllabus Upload, Google Drive, eGyankosh Style, PO/CO/PSO Mapping
"""

import streamlit as st
import requests
import json
import time
import os
import re
from datetime import datetime
from io import BytesIO

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

# Configuration
DEFAULT_API_KEY = "xai-6QJwG3u6540lVZyXbFBArvLQ43ZyJsrnq65pyCWhxh5zXqNvtwe6LdTURbTwvE2sA3Uxlb9gn82Vamgu"
API_URL = "https://api.x.ai/v1/chat/completions"

# Google Drive Service Account JSON (embedded)
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
    """Initialize all session state variables"""
    defaults = {
        'step': 'syllabus_upload',
        'api_key': DEFAULT_API_KEY,
        'custom_model': '',
        'course_title': 'Organizational Behaviour',
        'course_code': 'MBA101',
        'credits': 3,
        'target_audience': 'Postgraduate (MBA)',
        'num_units': 4,
        'sections_per_unit': 8,
        'program_objectives': '',
        'program_outcomes': '',
        'course_outcomes': '',
        'specialized_outcomes': '',
        'use_egyankosh_style': True,
        'uploaded_syllabus': None,
        'extracted_structure': None,
        'gdrive_folder_url': '',
        'gdrive_folder_id': '',
        'gdrive_service': None,
        'approved_outline': None,
        'content': {},
        'sections_to_process': [],
        'generation_start_time': None,
        'failed_sections': [],
        'paused': False,
        'uploaded_pdfs': {},
        'show_image_manager': False,
        'image_prompts': {},
        'uploaded_images': {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_api_headers():
    """Get API headers"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.get('api_key', DEFAULT_API_KEY)}"
    }

def make_api_call(messages, retries=3, delay=2, timeout=120, max_tokens=2000):
    """Make API call with retries"""
    headers = get_api_headers()
    
    if st.session_state.get('custom_model', '').strip():
        models = [st.session_state.custom_model]
    else:
        models = ["grok-2-1212", "grok-beta"]
    
    for model in models:
        payload = {
            "messages": messages,
            "model": model,
            "stream": False,
            "temperature": 0.3,
            "max_tokens": max_tokens
        }
        
        for attempt in range(retries):
            try:
                st.write(f"🔄 API Call Attempt {attempt + 1}/{retries} with model {model}...")
                
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                
                st.write(f"📡 Response Status: {response.status_code}")
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    st.write(f"✅ API Success! Response length: {len(content)} characters")
                    return content
                else:
                    st.warning(f"⚠️ Unexpected response format: {result}")
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ HTTP Error {e.response.status_code}: {e.response.text[:200]}")
                if e.response.status_code == 404:
                    break
                elif e.response.status_code == 401:
                    st.error("❌ Invalid API Key")
                    return None
                elif e.response.status_code == 429:
                    st.warning("⏳ Rate limited, waiting longer...")
                    time.sleep(delay * 2)
                else:
                    if attempt < retries - 1:
                        time.sleep(delay)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
    
    st.error("❌ All API attempts failed")
    return None

def extract_pdf_text(pdf_file):
    """Extract text from PDF"""
    if not PYPDF2_AVAILABLE:
        st.error("❌ PyPDF2 not installed. Install with: pip install PyPDF2")
        return None
    
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"❌ Error extracting PDF: {str(e)}")
        return None

def parse_syllabus_structure(text):
    """Parse syllabus text into structured format"""
    structure = {
        'course_info': {},
        'units': []
    }
    
    # Extract course information
    course_patterns = {
        'title': r'(?:Course|Subject)\s*(?:Title|Name)?\s*:?\s*(.+)',
        'code': r'(?:Course|Subject)\s*Code\s*:?\s*([A-Z0-9]+)',
        'credits': r'Credits?\s*:?\s*(\d+)',
    }
    
    for key, pattern in course_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            structure['course_info'][key] = match.group(1).strip()
    
    # Extract units
    unit_pattern = r'UNIT[\s-]*(\d+)\s*:?\s*(.+?)(?=UNIT[\s-]*\d+|$)'
    units = re.finditer(unit_pattern, text, re.IGNORECASE | re.DOTALL)
    
    for unit_match in units:
        unit_num = unit_match.group(1)
        unit_content = unit_match.group(2)
        
        # Extract unit title
        title_match = re.search(r'^(.+?)(?:\n|$)', unit_content)
        unit_title = title_match.group(1).strip() if title_match else f"Unit {unit_num}"
        
        # Extract topics
        topics = []
        topic_patterns = [
            r'^\s*[\d.]+\s+(.+?)$',
            r'^\s*[-•]\s+(.+?)$',
        ]
        
        lines = unit_content.split('\n')
        for line in lines:
            for pattern in topic_patterns:
                match = re.match(pattern, line)
                if match:
                    topic = match.group(1).strip()
                    if len(topic) > 5 and len(topic) < 200:
                        topics.append(topic)
        
        structure['units'].append({
            'unit_number': int(unit_num),
            'unit_title': unit_title,
            'topics': topics
        })
    
    return structure

def setup_google_drive_connection():
    """Setup Google Drive connection"""
    if not GDRIVE_AVAILABLE:
        st.warning("⚠️ Google Drive libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_info(
            GDRIVE_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Drive: {str(e)}")
        return None

def extract_folder_id_from_url(url):
    """Extract folder ID from Google Drive URL"""
    patterns = [
        r'folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume the URL is the folder ID itself
    if re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url
    
    return None

def create_or_use_folder(service, folder_name, parent_folder_id=None):
    """Create a new folder or use existing"""
    try:
        # Check if folder exists
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    
    except Exception as e:
        st.error(f"❌ Error creating folder: {str(e)}")
        return None

def upload_to_gdrive(service, file_buffer, filename, folder_id, mime_type='application/pdf'):
    """Upload file to Google Drive"""
    try:
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(file_buffer, mimetype=mime_type, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    
    except Exception as e:
        st.error(f"❌ Upload error: {str(e)}")
        return None

def clean_text_for_pdf(text):
    """Clean text for PDF rendering"""
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    
    return text

def generate_egyankosh_content(section_info, course_context):
    """Generate content in eGyankosh style with PO/CO/PSO mapping"""
    
    system_prompt = f"""You are an expert academic content developer specializing in {course_context['target_audience']} education.

Generate comprehensive self-learning material following eGyankosh standards and IGNOU guidelines.

CONTENT REQUIREMENTS:
- 30-35 pages worth of content (approximately 8,000-9,000 words)
- Grade 5 Simple English with Academic tonality
- Readability index: 10-12 (Flesch-Kincaid)
- Subject domain: {course_context['target_audience']}
- Each page should have minimum 250 words

MANDATORY STRUCTURE (Follow exactly):
1. **Structure Overview** (1 page)
   - Brief outline of what will be covered
   
2. **Learning Objectives** (1 page)
   - Mapped to Bloom's Taxonomy levels
   - Remember, Understand, Apply, Analyze, Evaluate, Create
   
3. **Introduction** (2-3 pages)
   - Engaging overview of the topic
   - Why it's important
   - Real-world relevance
   
4. **Meaning and Definition** (3-4 pages)
   - Clear, comprehensive definitions
   - Multiple perspectives
   - Academic references
   
5. **Nature/Types/Classification** (4-5 pages)
   - If applicable, categorize the concept
   - Use [[FIGURE X: description]] for diagrams
   
6. **Characteristics/Features** (3-4 pages)
   - Key attributes
   - Distinguishing factors
   
7. **Detailed Explanation** (8-10 pages)
   - In-depth coverage
   - Theories and models
   - Critical analysis
   
8. **Examples and Case Studies** (5-6 pages)
   - Real-world examples
   - Recent case studies (2020-2025)
   - Industry applications
   
9. **Practical Applications** (3-4 pages)
   - How to apply the knowledge
   - Step-by-step guidance
   
10. **CHECK YOUR PROGRESS** (1 page)
    - 5-7 review questions
    - Mix of Remember, Understand, Apply, Analyze levels
    
11. **Summary** (1 page)
    - Key takeaways
    - Concise recap
    
12. **Key Terms** (1 page)
    - Glossary of important terms
    
13. **Further Reading Links** (1 page)
    - Books, articles, websites
    - Academic resources

BLOOM'S TAXONOMY MAPPING:
Map all learning objectives clearly:
- **Remember**: Recall facts and basic concepts
- **Understand**: Explain ideas or concepts
- **Apply**: Use information in new situations
- **Analyze**: Draw connections among ideas
- **Evaluate**: Justify a decision or course of action
- **Create**: Produce new or original work

PROGRAM OUTCOMES MAPPING:
Align content with:
- **PO (Program Outcomes)**: {course_context.get('program_outcomes', 'Critical thinking, Problem-solving, Communication')}
- **CO (Course Outcomes)**: {course_context.get('course_outcomes', 'Understand key concepts, Apply theories')}
- **PSO (Specialized Outcomes)**: {course_context.get('specialized_outcomes', 'Specialized skills in the domain')}

FORMATTING RULES:
- Use **bold** for key terms
- Use [[FIGURE X: detailed description]] for diagrams/images
- Use $$formula$$ for mathematical expressions
- Use bullet points with * for lists
- Use --- for section breaks
- Keep paragraphs 4-6 sentences
- Average sentence length: 15-20 words

WRITING STYLE:
- Simple, clear language (Grade 5 level)
- Academic tone maintained throughout
- Active voice preferred
- Short paragraphs for readability
- Engaging and student-friendly"""

    user_prompt = f"""Generate complete, comprehensive academic content for:

**UNIT**: {section_info['unit_title']}
**TOPIC**: {section_info['section_number']} {section_info['section_title']}
**DESCRIPTION**: {section_info['description']}

**COURSE DETAILS**:
- Title: {course_context['course_title']}
- Code: {course_context.get('course_code', 'N/A')}
- Credits: {course_context.get('credits', 3)}
- Level: {course_context['target_audience']}

**PROGRAM OBJECTIVES**: {course_context.get('program_objectives', 'Not specified')}

Write comprehensive, well-researched content with:
✓ Clear definitions and explanations
✓ Multiple real-world examples from recent years
✓ Case studies from 2020-2025 scenarios
✓ Practical applications for students
✓ Critical thinking questions
✓ Assessment questions aligned with Bloom's taxonomy
✓ PO/CO/PSO mapping at the end

Ensure content is engaging, academically rigorous, and suitable for self-study.
Minimum 8,000 words covering all required sections."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return make_api_call(messages, max_tokens=4000, retries=3)

def compile_unit_pdf_egyankosh(unit_data, course_info, content_dict):
    """Compile unit PDF with eGyankosh formatting"""
    
    if not REPORTLAB_AVAILABLE:
        st.error("❌ PDF generation not available. Install: pip install reportlab")
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles matching the sample
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    unit_title_style = ParagraphStyle(
        'UnitTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10
    )
    
    # Cover page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(f"UNIT {unit_data['unit_number']}", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(unit_data['unit_title'].upper(), title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Horizontal line
    line_table = Table([['']], colWidths=[6.5*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1f77b4')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(line_table)
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(course_info.get('course_title', 'Course Material'), styles['Heading3']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"<b>Course Code:</b> {course_info.get('course_code', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Credits:</b> {course_info.get('credits', 3)}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"For {course_info.get('target_audience', 'Students')}", styles['Normal']))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>", styles['Normal']))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("<b>STRUCTURE</b>", section_style))
    story.append(line_table)
    story.append(Spacer(1, 0.3*inch))
    
    for section in unit_data.get('sections', []):
        sec_title = section.get('section_title', 'Untitled')
        sec_num = section.get('section_number', '')
        story.append(Paragraph(f"{sec_num} {sec_title}", body_style))
    
    story.append(PageBreak())
    
    # Content sections
    for section in unit_data.get('sections', []):
        sec_num = section.get('section_number', '')
        sec_title = section.get('section_title', 'Untitled')
        sec_key = f"{sec_num} {sec_title}"
        
        # Section title with bold and line
        story.append(Paragraph(f"<b>{sec_key}</b>", section_style))
        story.append(line_table)
        story.append(Spacer(1, 0.2*inch))
        
        raw_content = content_dict.get(sec_key, "[Content not generated]")
        
        # Process content line by line
        lines = raw_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Handle subsection headings
            if line.startswith('##'):
                clean_line = line.replace('#', '').strip()
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph(f"<b>{clean_line}</b>", section_style))
                story.append(line_table)
                i += 1
                continue
            
            # Handle CHECK YOUR PROGRESS
            if 'CHECK YOUR PROGRESS' in line.upper():
                story.append(Spacer(1, 0.3*inch))
                progress_table = Table(
                    [[Paragraph("<b>CHECK YOUR PROGRESS</b>", body_style)]],
                    colWidths=[6.5*inch]
                )
                progress_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                    ('BORDER', (0, 0), (-1, -1), 1, colors.black),
                    ('PADDING', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))
                story.append(progress_table)
                story.append(Spacer(1, 0.15*inch))
                
                # Collect questions
                i += 1
                while i < len(lines):
                    q_line = lines[i].strip()
                    if not q_line or q_line == '---':
                        break
                    q_line = re.sub(r'^\d+\.\s*', '', q_line)
                    q_line = clean_text_for_pdf(q_line)
                    if q_line:
                        story.append(Paragraph(f"• {q_line}", bullet_style))
                    i += 1
                story.append(Spacer(1, 0.3*inch))
                continue
            
            # Handle bullet points
            elif line.startswith(('*', '-', '•')):
                clean_line = re.sub(r'^[\*\-•]\s*', '', line)
                clean_line = clean_text_for_pdf(clean_line)
                if clean_line:
                    story.append(Paragraph(f"• {clean_line}", bullet_style))
            
            # Handle regular paragraphs
            else:
                clean_line = clean_text_for_pdf(line)
                if clean_line and len(clean_line) > 3:
                    try:
                        story.append(Paragraph(clean_line, body_style))
                        story.append(Spacer(1, 0.1*inch))
                    except:
                        escaped = clean_line.replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(escaped, body_style))
            
            i += 1
        
        # Add line at end of section
        story.append(Spacer(1, 0.3*inch))
        story.append(line_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ PDF generation error: {str(e)}")
        return None

def show_syllabus_upload_page():
    """Syllabus upload page"""
    st.header("📄 Step 1: Syllabus Upload (Optional)")
    
    st.info("💡 You can either upload your existing syllabus or proceed without one")
    
    upload_choice = st.radio(
        "Choose your approach:",
        ["Upload Existing Syllabus", "Proceed Without Syllabus"],
        key="upload_choice"
    )
    
    if upload_choice == "Upload Existing Syllabus":
        uploaded_file = st.file_uploader(
            "Upload Syllabus PDF",
            type=['pdf'],
            help="Upload your course syllabus in PDF format",
            key="syllabus_uploader"
        )
        
        if uploaded_file:
            st.session_state.uploaded_syllabus = uploaded_file
            
            with st.spinner("📖 Extracting syllabus content..."):
                extracted_text = extract_pdf_text(uploaded_file)
                
                if extracted_text:
                    st.success("✅ Syllabus extracted successfully!")
                    
                    with st.expander("📝 View Extracted Text", expanded=False):
                        st.text_area("Extracted Content", extracted_text, height=300, key="extracted_text_view")
                    
                    with st.spinner("🔍 Parsing syllabus structure..."):
                        structure = parse_syllabus_structure(extracted_text)
                        st.session_state.extracted_structure = structure
                    
                    if structure['units']:
                        st.success(f"✅ Found {len(structure['units'])} units")
                        
                        # Display extracted structure
                        st.subheader("📊 Extracted Course Structure")
                        
                        # Course info
                        if structure['course_info']:
                            st.write("**Course Information:**")
                            for key, value in structure['course_info'].items():
                                st.write(f"- {key.title()}: {value}")
                        
                        # Units
                        for unit in structure['units']:
                            with st.expander(f"Unit {unit['unit_number']}: {unit['unit_title']}", expanded=False):
                                st.write(f"**Topics ({len(unit['topics'])}):**")
                                for i, topic in enumerate(unit['topics'], 1):
                                    st.write(f"{i}. {topic}")
                        
                        # Verification
                        st.divider()
                        verify = st.checkbox("✅ Structure looks correct, proceed with this", key="verify_structure")
                        
                        if verify:
                            if st.button("➡️ Continue to Configuration", type="primary", key="continue_from_syllabus"):
                                st.session_state.step = 'configuration'
                                st.rerun()
                    else:
                        st.warning("⚠️ Could not parse unit structure automatically")
                        if st.button("⚙️ Configure Manually", key="manual_config_from_syllabus"):
                            st.session_state.step = 'configuration'
                            st.rerun()
    else:
        st.info("📝 You'll configure the course structure manually")
        if st.button("➡️ Continue to Configuration", type="primary", key="continue_no_syllabus"):
            st.session_state.step = 'configuration'
            st.rerun()

def show_configuration_page():
    """Configuration page"""
    st.header("⚙️ Step 2: Course Configuration")
    
    # Use extracted info if available
    extracted = st.session_state.get('extracted_structure', {})
    course_info = extracted.get('course_info', {})
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key = st.text_input(
            "Grok API Key",
            value=st.session_state.get('api_key', DEFAULT_API_KEY),
            type="password",
            key="api_key_input"
        )
        st.session_state.api_key = api_key
    
    with col2:
        if st.button("🧪 Test API", use_container_width=True, key="test_api"):
            with st.spinner("Testing..."):
                resp = make_api_call([{"role": "user", "content": "Say 'API test successful'"}], max_tokens=50)
                if resp:
                    st.success("✅ API Working!")
    
    st.divider()
    
    # Course Details
    st.subheader("📚 Course Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        course_title = st.text_input(
            "Course Title",
            value=course_info.get('title', st.session_state.course_title),
            key="course_title_input"
        )
        st.session_state.course_title = course_title
        
        course_code = st.text_input(
            "Course Code",
            value=course_info.get('code', st.session_state.get('course_code', 'MBA101')),
            key="course_code_input"
        )
        st.session_state.course_code = course_code
    
    with col2:
        credits = st.number_input(
            "Credits",
            min_value=1,
            max_value=10,
            value=int(course_info.get('credits', st.session_state.credits)),
            key="credits_input"
        )
        st.session_state.credits = credits
        
        target_audience = st.selectbox(
            "Target Audience",
            ["Postgraduate (MBA)", "Undergraduate", "Professional Development"],
            index=0,
            key="target_audience_select"
        )
        st.session_state.target_audience = target_audience
    
    st.divider()
    
    # Academic Mappings
    st.subheader("🎯 Academic Mappings")
    
    program_objectives = st.text_area(
        "Program Educational Objectives (PEO)",
        value=st.session_state.get('program_objectives', ''),
        height=100,
        help="Define what students should be able to do after completing the program",
        key="peo_input"
    )
    st.session_state.program_objectives = program_objectives
    
    col1, col2 = st.columns(2)
    
    with col1:
        program_outcomes = st.text_area(
            "Program Outcomes (PO)",
            value=st.session_state.get('program_outcomes', ''),
            height=100,
            help="Skills and knowledge students gain from the program",
            key="po_input"
        )
        st.session_state.program_outcomes = program_outcomes
    
    with col2:
        specialized_outcomes = st.text_area(
            "Specialized Program Outcomes (PSO)",
            value=st.session_state.get('specialized_outcomes', ''),
            height=100,
            help="Specialized skills specific to this program",
            key="pso_input"
        )
        st.session_state.specialized_outcomes = specialized_outcomes
    
    course_outcomes = st.text_area(
        "Course Learning Objectives & Outcomes (CLO/CO)",
        value=st.session_state.get('course_outcomes', ''),
        height=100,
        help="What students will learn in this specific course",
        key="co_input"
    )
    st.session_state.course_outcomes = course_outcomes
    
    st.divider()
    
    # Content Configuration
    st.subheader("📝 Content Configuration")
    
    use_egyankosh = st.checkbox(
        "Use eGyankosh Style Content (IGNOU Standards)",
        value=True,
        help="Generate content following eGyankosh standards with 30-35 pages per topic",
        key="use_egyankosh"
    )
    st.session_state.use_egyankosh_style = use_egyankosh
    
    if not st.session_state.get('extracted_structure'):
        col1, col2 = st.columns(2)
        with col1:
            num_units = st.number_input(
                "Number of Units",
                min_value=1,
                max_value=10,
                value=4,
                key="num_units_input"
            )
            st.session_state.num_units = num_units
        
        with col2:
            sections_per_unit = st.number_input(
                "Topics per Unit",
                min_value=3,
                max_value=15,
                value=8,
                key="sections_per_unit_input"
            )
            st.session_state.sections_per_unit = sections_per_unit
    
    st.divider()
    
    # Google Drive Configuration
    st.subheader("☁️ Google Drive Configuration")
    
    if GDRIVE_AVAILABLE:
        st.success("✅ Google Drive libraries installed")
        
        gdrive_folder_url = st.text_input(
            "Google Drive Folder URL or ID",
            value=st.session_state.get('gdrive_folder_url', ''),
            placeholder="https://drive.google.com/drive/folders/YOUR_FOLDER_ID or just the folder ID",
            help="Enter the Google Drive folder URL or ID where PDFs will be uploaded",
            key="gdrive_folder_input"
        )
        
        if gdrive_folder_url:
            st.session_state.gdrive_folder_url = gdrive_folder_url
            folder_id = extract_folder_id_from_url(gdrive_folder_url)
            
            if folder_id:
                st.session_state.gdrive_folder_id = folder_id
                st.success(f"✅ Folder ID: {folder_id}")
                st.info(f"📧 Make sure this folder is shared with: curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com")
                
                # Test connection
                if st.button("🔗 Test Google Drive Connection", key="test_gdrive"):
                    with st.spinner("Testing connection..."):
                        service = setup_google_drive_connection()
                        if service:
                            try:
                                # Try to access the folder
                                folder = service.files().get(fileId=folder_id, fields='id,name').execute()
                                st.success(f"✅ Successfully connected to folder: {folder.get('name')}")
                                st.session_state.gdrive_service = service
                            except Exception as e:
                                st.error(f"❌ Cannot access folder. Make sure it's shared with the service account email above.")
                                st.error(f"Error details: {str(e)}")
            else:
                st.error("❌ Invalid folder URL or ID format")
        
        st.markdown("---")
        st.markdown("**How to set up:**")
        st.markdown("1. Create a folder in Google Drive")
        st.markdown("2. Right-click folder → Share")
        st.markdown("3. Add email: `curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com`")
        st.markdown("4. Grant **Editor** permission")
        st.markdown("5. Copy and paste the folder URL above")
    else:
        st.warning("⚠️ Google Drive libraries not installed. PDFs will only be available for download.")
        st.code("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    
    st.divider()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Syllabus", use_container_width=True, key="back_to_syllabus"):
            st.session_state.step = 'syllabus_upload'
            st.rerun()
    
    with col2:
        if st.button("➡️ Generate Outline", type="primary", use_container_width=True, key="generate_outline"):
            st.session_state.step = 'outline_generation'
            st.rerun()

def create_comprehensive_outline(num_units=4, sections_per_unit=8):
    """Create comprehensive default outline"""
    outline = []
    
    base_topics = [
        {
            "title": "Introduction and Foundations",
            "sections": [
                ("Introduction", "Overview of organizational behaviour"),
                ("Objectives", "Learning outcomes and goals"),
                ("Meaning and Definition", "Core concepts and terminology"),
                ("Historical Perspective", "Evolution of the field"),
                ("Different Approaches", "Theoretical frameworks"),
                ("Educational Institutions", "Application in educational settings"),
                ("Need to Study", "Importance and relevance"),
                ("Goals", "Objectives of studying OB")
            ]
        },
        {
            "title": "Individual Behaviour and Personality",
            "sections": [
                ("Individual Behaviour", "Understanding individual differences"),
                ("Personality", "Personality traits and determinants"),
                ("Personality Theories", "Major theoretical approaches"),
                ("Perception", "Perceptual processes"),
                ("Values and Attitudes", "Belief systems"),
                ("Learning", "Learning theories and applications"),
                ("Motivation", "Motivational theories"),
                ("Job Satisfaction", "Performance and satisfaction")
            ]
        },
        {
            "title": "Group Dynamics and Teams",
            "sections": [
                ("Group Behaviour", "Foundations of group dynamics"),
                ("Group Development", "Stages of team formation"),
                ("Group Decision Making", "Collective decision processes"),
                ("Communication", "Communication in organizations"),
                ("Leadership", "Leadership theories and styles"),
                ("Power and Politics", "Organizational power structures"),
                ("Conflict", "Conflict management"),
                ("Team Building", "Creating effective teams")
            ]
        },
        {
            "title": "Organizational Structure and Culture",
            "sections": [
                ("Structure", "Organizational design principles"),
                ("Design", "Structural configurations"),
                ("Culture", "Organizational culture"),
                ("Change Management", "Managing organizational change"),
                ("Development", "Organizational development"),
                ("Stress Management", "Workplace stress"),
                ("Work-Life Balance", "Balancing work and life"),
                ("Future Trends", "Emerging trends in OB")
            ]
        }
    ]
    
    for i in range(num_units):
        unit_num = i + 1
        
        if i < len(base_topics):
            unit_title = base_topics[i]["title"]
            section_data = base_topics[i]["sections"]
        else:
            unit_title = f"Advanced Topics Part {i - len(base_topics) + 1}"
            section_data = [(f"Topic {j+1}", f"Advanced topic {j+1}") for j in range(sections_per_unit)]
        
        sections = []
        for j in range(min(sections_per_unit, len(section_data))):
            sec_title, sec_desc = section_data[j] if j < len(section_data) else (f"Topic {j+1}", f"Description {j+1}")
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

def show_outline_page():
    """Outline generation and editing page"""
    st.header("📋 Step 3: Course Outline")
    
    if 'approved_outline' not in st.session_state or st.session_state.approved_outline is None:
        # Use extracted structure if available
        if st.session_state.get('extracted_structure') and st.session_state.extracted_structure.get('units'):
            extracted = st.session_state.extracted_structure
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
            st.success("✅ Using extracted syllabus structure")
        else:
            # Generate outline using AI or default
            num_units = st.session_state.get('num_units', 4)
            sections_per_unit = st.session_state.get('sections_per_unit', 8)
            
            st.info(f"Generating outline for {num_units} units with {sections_per_unit} sections each...")
            st.session_state.outline = create_comprehensive_outline(num_units, sections_per_unit)
    
    if 'outline' in st.session_state:
        outline = st.session_state.outline
        total_sections = sum(len(unit.get('sections', [])) for unit in outline)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Units", len(outline))
        with col2:
            st.metric("📄 Total Sections", total_sections)
        with col3:
            estimated_pages = (total_sections * 35) if st.session_state.use_egyankosh_style else (total_sections * 2)
            st.metric("📖 Est. Pages", f"~{estimated_pages}")
        
        st.divider()
        
        # Convert outline to editable format
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
        st.caption("Edit any cell directly. Add rows with + button at the bottom.")
        
        edited_df = st.data_editor(
            rows,
            num_rows="dynamic",
            use_container_width=True,
            height=400,
            column_config={
                "Unit": st.column_config.NumberColumn("Unit #", width="small"),
                "Unit Title": st.column_config.TextColumn("Unit Title", width="medium"),
                "Section": st.column_config.TextColumn("Section #", width="small"),
                "Section Title": st.column_config.TextColumn("Section Title", width="medium"),
                "Description": st.column_config.TextColumn("Description", width="large")
            },
            key="outline_editor_main"
        )
        
        st.divider()
        
        # Navigation
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back", use_container_width=True, key="back_to_config"):
                st.session_state.step = 'configuration'
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True, key="regenerate_outline"):
                if 'outline' in st.session_state:
                    del st.session_state.outline
                st.rerun()
        
        with col3:
            if st.button("✅ Approve & Generate Content", type="primary", use_container_width=True, key="approve_outline"):
                # Convert edited dataframe back to outline format
                approved = []
                current = None
                
                for _, row in edited_df.iterrows():
                    if current is None or current['unit_number'] != row['Unit']:
                        if current:
                            approved.append(current)
                        current = {
                            'unit_number': row['Unit'],
                            'unit_title': row['Unit Title'],
                            'sections': []
                        }
                    current['sections'].append({
                        'section_number': row['Section'],
                        'section_title': row['Section Title'],
                        'description': row['Description']
                    })
                
                if current:
                    approved.append(current)
                
                st.session_state.approved_outline = approved
                st.session_state.step = 'content_generation'
                st.rerun()

def show_content_generation_page():
    """Content generation page"""
    st.header("✍️ Step 4: AI Content Generation")
    
    if 'approved_outline' not in st.session_state or st.session_state.approved_outline is None:
        st.error("❌ No approved outline found")
        if st.button("← Go Back", key="back_no_outline"):
            st.session_state.step = 'outline_generation'
            st.rerun()
        return
    
    # Initialize content generation
    if 'content' not in st.session_state or not st.session_state.content:
        st.session_state.content = {}
        st.session_state.sections_to_process = []
        st.session_state.generation_start_time = time.time()
        st.session_state.failed_sections = []
        
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
        remaining = total - completed
        st.metric("⏳ Remaining", remaining)
    with col4:
        if completed > 0 and st.session_state.generation_start_time:
            elapsed = time.time() - st.session_state.generation_start_time
            avg_time = elapsed / completed
            eta_seconds = avg_time * remaining
            eta_minutes = int(eta_seconds / 60)
            st.metric("⏱️ ETA", f"~{eta_minutes}min")
    
    st.progress(completed / total if total > 0 else 0)
    
    # Content generation loop
    if completed < total:
        current = st.session_state.sections_to_process[completed]
        section_key = f"{current['section_number']} {current['section_title']}"
        
        st.info(f"🤖 Now Generating: **{section_key}**")
        st.caption(f"Unit {current['unit_number']}: {current['unit_title']}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Description:** {current['description']}")
        with col2:
            if st.button("⏸️ Pause", use_container_width=True, key="pause_generation"):
                st.session_state.paused = True
                st.rerun()
        
        if not st.session_state.get('paused', False):
            with st.spinner(f"✍️ Writing section {completed + 1} of {total}..."):
                course_context = {
                    'course_title': st.session_state.course_title,
                    'course_code': st.session_state.course_code,
                    'credits': st.session_state.credits,
                    'target_audience': st.session_state.target_audience,
                    'program_objectives': st.session_state.program_objectives,
                    'program_outcomes': st.session_state.program_outcomes,
                    'course_outcomes': st.session_state.course_outcomes,
                    'specialized_outcomes': st.session_state.specialized_outcomes
                }
                
                with st.expander("🔍 Generation Details", expanded=False):
                    content = generate_egyankosh_content(current, course_context)
                
                if content and len(content.strip()) > 100:
                    st.session_state.content[section_key] = content
                    st.success(f"✅ Completed: {section_key}")
                    
                    with st.expander("📄 Generated Content Preview", expanded=False):
                        st.markdown(content[:500] + "...")
                        st.caption(f"📊 {len(content.split())} words")
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to generate: {section_key}")
                    st.session_state.failed_sections.append(section_key)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔄 Retry", use_container_width=True, key="retry_failed"):
                            st.rerun()
                    with col2:
                        if st.button("⏭️ Skip", use_container_width=True, key="skip_failed"):
                            st.session_state.content[section_key] = f"[Content skipped for {section_key}]"
                            st.rerun()
                    with col3:
                        if st.button("🛑 Stop All", use_container_width=True, key="stop_all"):
                            st.session_state.step = 'compilation'
                            st.rerun()
        else:
            st.warning("⏸️ Generation Paused")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Resume", type="primary", use_container_width=True, key="resume_generation"):
                    st.session_state.paused = False
                    st.rerun()
            with col2:
                if st.button("⏭️ Skip This Section", use_container_width=True, key="skip_paused"):
                    st.session_state.content[section_key] = f"[Skipped: {section_key}]"
                    st.session_state.paused = False
                    st.rerun()
    
    else:
        # All content generated
        st.success("🎉 All Content Generated Successfully!")
        
        total_words = sum(len(c.split()) for c in st.session_state.content.values())
        total_chars = sum(len(c) for c in st.session_state.content.values())
        estimated_pages = total_chars / 3000
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Total Words", f"{total_words:,}")
        with col2:
            st.metric("📄 Sections", total)
        with col3:
            st.metric("📖 Pages", f"~{estimated_pages:.0f}")
        
        if st.session_state.failed_sections:
            st.warning(f"⚠️ {len(st.session_state.failed_sections)} sections failed")
            with st.expander("View Failed Sections"):
                for failed in st.session_state.failed_sections:
                    st.write(f"- {failed}")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back", use_container_width=True, key="back_from_generation"):
                st.session_state.step = 'outline_generation'
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate All", use_container_width=True, key="regenerate_all_content"):
                if st.checkbox("⚠️ Confirm delete all?", key="confirm_regen"):
                    del st.session_state.content
                    del st.session_state.sections_to_process
                    st.rerun()
        
        with col3:
            if st.button("📄 Compile PDFs", type="primary", use_container_width=True, key="go_to_compilation"):
                st.session_state.step = 'compilation'
                st.rerun()

def show_compilation_page():
    """PDF compilation and Google Drive upload page"""
    st.header("📄 Step 5: Compile & Upload PDFs")
    
    if 'content' not in st.session_state or not st.session_state.content:
        st.error("❌ No content found")
        if st.button("← Back", key="back_no_content"):
            st.session_state.step = 'content_generation'
            st.rerun()
        return
    
    if 'approved_outline'
