"""
COMPLETE AI CURRICULUM GENERATOR - FULL VERSION
================================================
All features: Images, Beautiful PDFs, Logo, Google Drive/Docs Export
"""

import streamlit as st
import requests
import json
import time
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
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configuration
DEFAULT_API_KEY = "xai-6QJwG3u6540lVZyXbFBArvLQ43ZyJsrnq65pyCWhxh5zXqNvtwe6LdTURbTwvE2sA3Uxlb9gn82Vamgu"
API_URL = "https://api.x.ai/v1/chat/completions"

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
    defaults = {
        'step': 'syllabus_upload', 'api_key': DEFAULT_API_KEY, 'course_title': 'Organizational Behaviour',
        'course_code': 'MBA101', 'credits': 3, 'target_audience': 'Postgraduate (MBA)',
        'num_units': 4, 'sections_per_unit': 8, 'program_objectives': '', 'program_outcomes': '',
        'course_outcomes': '', 'specialized_outcomes': '', 'use_egyankosh_style': True,
        'gdrive_folder_url': '', 'gdrive_folder_id': '', 'content': {}, 'paused': False,
        'image_prompts': {}, 'uploaded_images': {}, 'document_heading': '',
        'institution_logo': None, 'export_to_docs': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def calculate_accurate_pages(content):
    if not content:
        return 0
    words = len(content.split())
    pages = words / 275
    image_count = len(re.findall(r'\[\[FIGURE\s+\d+:', content, re.IGNORECASE))
    pages += (image_count * 0.5)
    box_count = len(re.findall(r'CHECK YOUR PROGRESS', content, re.IGNORECASE))
    pages += (box_count * 0.3)
    return round(pages, 1)

def extract_image_references(content):
    image_refs = {}
    figures = re.findall(r'\[\[FIGURE\s+(\d+):\s*(.*?)\]\]', content, re.IGNORECASE)
    for fig_num, description in figures:
        fig_num = int(fig_num)
        if fig_num not in image_refs:
            prompt = f"Professional educational illustration: {description}. Clean academic diagram, textbook quality."
            image_refs[fig_num] = {'description': description, 'prompt': prompt, 'uploaded': False}
    return image_refs

def show_image_manager():
    st.subheader("🖼️ Image Manager")
    all_image_refs = {}
    if 'content' in st.session_state:
        for content in st.session_state.content.values():
            refs = extract_image_references(content)
            all_image_refs.update(refs)
    
    for fig_num, ref_data in all_image_refs.items():
        if fig_num not in st.session_state.image_prompts:
            st.session_state.image_prompts[fig_num] = ref_data
    
    if not all_image_refs:
        st.info("📝 No images found. Add [[FIGURE X: description]] to content.")
        return
    
    st.info(f"📸 Found {len(all_image_refs)} image(s)")
    for fig_num in sorted(all_image_refs.keys()):
        ref_data = st.session_state.image_prompts[fig_num]
        with st.expander(f"📷 Figure {fig_num}: {ref_data['description'][:50]}..."):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Description:** {ref_data['description']}")
                st.code(ref_data['prompt'])
            with col2:
                uploaded = st.file_uploader(f"Upload {fig_num}", type=['png', 'jpg'], key=f"img_{fig_num}")
                if uploaded:
                    st.session_state.uploaded_images[fig_num] = uploaded
                    st.session_state.image_prompts[fig_num]['uploaded'] = True
                    st.success("✅")
                    st.image(uploaded, width=200)
    
    uploaded_count = sum(1 for ref in st.session_state.image_prompts.values() if ref['uploaded'])
    st.metric("Ready", f"{uploaded_count}/{len(all_image_refs)}")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self.logo = kwargs.pop('logo', None)
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            self.draw_watermark()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(A4[0] - 1*inch, 0.5*inch, f"Page {self._pageNumber} of {page_count}")
    
    def draw_watermark(self):
        if self.logo:
            try:
                self.saveState()
                self.setFillAlpha(0.1)
                x, y = (A4[0] - 4*inch) / 2, (A4[1] - 4*inch) / 2
                self.drawImage(self.logo, x, y, 4*inch, 4*inch, preserveAspectRatio=True, mask='auto')
                self.restoreState()
            except:
                pass

def compile_beautiful_pdf(unit_data, course_info, content_dict, uploaded_images=None, logo_path=None):
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=1*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=28, textColor=colors.HexColor('#1f77b4'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#2c3e50'), spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold', backColor=colors.HexColor('#ecf0f1'))
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=11, alignment=TA_JUSTIFY, spaceAfter=12, leading=16, textColor=colors.HexColor('#2c3e50'))
    
    # Cover
    story.append(Spacer(1, 2*inch))
    if course_info.get('document_heading'):
        story.append(Paragraph(course_info['document_heading'], styles['Heading3']))
        story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"UNIT {unit_data['unit_number']}", styles['Heading2']))
    story.append(Paragraph(unit_data['unit_title'].upper(), title_style))
    story.append(Spacer(1, 0.5*inch))
    
    line = Table([['']], colWidths=[6*inch])
    line.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 3, colors.HexColor('#1f77b4'))]))
    story.append(line)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<b>{course_info.get('course_title', '')}</b>", styles['Heading3']))
    story.append(Paragraph(f"Code: {course_info.get('course_code', 'N/A')} | Credits: {course_info.get('credits', 3)}", styles['Normal']))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(PageBreak())
    
    # Content
    for section in unit_data.get('sections', []):
        sec_key = f"{section['section_number']} {section['section_title']}"
        story.append(Paragraph(f"<b>{sec_key}</b>", section_style))
        story.append(Spacer(1, 0.3*inch))
        
        content = content_dict.get(sec_key, "")
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Images
            if '[[FIGURE' in line.upper():
                fig_match = re.search(r'\[\[FIGURE\s+(\d+):\s*(.*?)\]\]', line, re.IGNORECASE)
                if fig_match:
                    fig_num = int(fig_match.group(1))
                    fig_desc = fig_match.group(2)
                    if uploaded_images and fig_num in uploaded_images:
                        try:
                            img_file = uploaded_images[fig_num]
                            img_file.seek(0)
                            img = RLImage(img_file, width=5*inch, height=3.5*inch)
                            story.append(img)
                            story.append(Paragraph(f"<i>Figure {fig_num}: {fig_desc}</i>", styles['Caption']))
                        except:
                            story.append(Paragraph(f"[Figure {fig_num}: {fig_desc}]", styles['Italic']))
                    else:
                        story.append(Paragraph(f"[Figure {fig_num}: {fig_desc} - To be added]", styles['Italic']))
                i += 1
                continue
            
            # CHECK YOUR PROGRESS
            if 'CHECK YOUR PROGRESS' in line.upper():
                progress_table = Table([[Paragraph("<b>CHECK YOUR PROGRESS</b>", body_style)]], colWidths=[6*inch])
                progress_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e8f4f8')),
                    ('BORDER', (0,0), (-1,-1), 2, colors.HexColor('#3498db')),
                    ('PADDING', (0,0), (-1,-1), 15)
                ]))
                story.append(progress_table)
                i += 1
                while i < len(lines):
                    q = lines[i].strip()
                    if not q or q == '---':
                        break
                    q = re.sub(r'^\d+\.\s*', '', q)
                    if q:
                        story.append(Paragraph(f"• {q}", body_style))
                    i += 1
                continue
            
            # Bold terms
            if '**' in line:
                line = line.replace('**', '<b>').replace('**', '</b>')
            
            # Bullets
            if line.startswith(('*', '-', '•')):
                clean = re.sub(r'^[\*\-•]\s*', '', line)
                story.append(Paragraph(f"• {clean}", body_style))
            else:
                if len(line) > 3:
                    try:
                        story.append(Paragraph(line, body_style))
                    except:
                        pass
            i += 1
        
        story.append(Spacer(1, 0.5*inch))
        story.append(line)
        story.append(PageBreak())
    
    try:
        def create_canvas(*args, **kwargs):
            return NumberedCanvas(*args, logo=logo_path, **kwargs)
        doc.build(story, canvasmaker=create_canvas)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"PDF error: {str(e)}")
        return None

def export_to_google_docs(content_text, filename, folder_id, service):
    try:
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', content_text)
        clean = re.sub(r'\[\[FIGURE.*?\]\]', '[Image]', clean)
        
        file_metadata = {
            'name': filename.replace('.pdf', ''),
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(BytesIO(clean.encode('utf-8')), mimetype='text/plain', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Docs error: {str(e)}")
        return None

def get_api_headers():
    return {"Content-Type": "application/json", "Authorization": f"Bearer {st.session_state.api_key}"}

def make_api_call(messages, retries=3, timeout=120, max_tokens=3000):
    headers = get_api_headers()
    payload = {"messages": messages, "model": "grok-2-1212", "stream": False, "temperature": 0.3, "max_tokens": max_tokens}
    
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
    return None

def extract_pdf_text(pdf_file):
    try:
        return "\n".join([page.extract_text() for page in PyPDF2.PdfReader(pdf_file).pages])
    except:
        return None

def parse_syllabus_structure(text):
    structure = {'course_info': {}, 'units': []}
    for key, pattern in {'title': r'Course.*?:?\s*(.+)', 'code': r'Code\s*:?\s*([A-Z0-9]+)', 'credits': r'Credits?\s*:?\s*(\d+)'}.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            structure['course_info'][key] = match.group(1).strip()
    
    for unit_match in re.finditer(r'UNIT[\s-]*(\d+)\s*:?\s*(.+?)(?=UNIT|$)', text, re.IGNORECASE | re.DOTALL):
        unit_num = int(unit_match.group(1))
        content = unit_match.group(2)
        title = re.search(r'^(.+?)(?:\n|$)', content).group(1).strip() if re.search(r'^(.+?)(?:\n|$)', content) else f"Unit {unit_num}"
        topics = [m.group(1).strip() for m in re.finditer(r'^\s*[\d.]+\s+(.+?)$', content, re.MULTILINE) if 5 < len(m.group(1).strip()) < 200]
        structure['units'].append({'unit_number': unit_num, 'unit_title': title, 'topics': topics})
    return structure

def setup_google_drive_connection():
    try:
        creds = service_account.Credentials.from_service_account_info(GDRIVE_CREDENTIALS, scopes=['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=creds)
    except:
        return None

def extract_folder_id_from_url(url):
    for p in [r'folders/([a-zA-Z0-9_-]+)', r'id=([a-zA-Z0-9_-]+)']:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return url if re.match(r'^[a-zA-Z0-9_-]+$', url) else None

def create_or_use_folder(service, name, parent=None):
    try:
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent:
            q += f" and '{parent}' in parents"
        folders = service.files().list(q=q, fields="files(id)").execute().get('files', [])
        if folders:
            return folders[0]['id']
        meta = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
        if parent:
            meta['parents'] = [parent]
        return service.files().create(body=meta, fields='id').execute().get('id')
    except:
        return None

def upload_to_gdrive(service, buffer, filename, folder_id):
    try:
        meta = {'name': filename, 'parents': [folder_id]}
        media = MediaIoBaseUpload(buffer, mimetype='application/pdf', resumable=True)
        return service.files().create(body=meta, media_body=media, fields='webViewLink').execute().get('webViewLink')
    except:
        return None

def generate_content(section_info, course_context):
    po_text = ""
    for key, label in [('program_objectives', 'PEO'), ('program_outcomes', 'PO'), ('course_outcomes', 'CO'), ('specialized_outcomes', 'PSO')]:
        if course_context.get(key):
            po_text += f"\n**{label}:** {course_context[key]}\n"
    
    sys_prompt = f"""Expert academic writer for {course_context['target_audience']}.
Generate 8,000+ words (30-35 pages) in eGyankosh style.
Structure: Overview, Objectives (Bloom's), Intro, Definitions, Types, Characteristics, Explanation, Examples, Cases (2020-2025), Applications, CHECK YOUR PROGRESS, Summary, Terms, Reading, PO/CO/PSO mapping.
Use **bold**, [[FIGURE X: desc]], bullets.
{po_text}"""
    
    user_prompt = f"""Write for: {section_info['section_number']} {section_info['section_title']}
Course: {course_context['course_title']}
Description: {section_info['description']}
Minimum 8,000 words."""
    
    return make_api_call([{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}], max_tokens=4000)

def generate_outline_with_ai():
    num_units = st.session_state.get('num_units', 4)
    spu = st.session_state.get('sections_per_unit', 8)
    
    sys = """Curriculum designer. JSON: [{"unit_number":1,"unit_title":"Title","sections":[{"section_number":"1.1","section_title":"Title","description":"Desc"}]}]"""
    usr = f"""Course: {st.session_state.course_title}, Code: {st.session_state.course_code}
Generate {num_units} units, {spu} sections each. JSON only."""
    
    with st.expander("AI Generation", expanded=True):
        outline_str = make_api_call([{"role": "system", "content": sys}, {"role": "user", "content": usr}], max_tokens=3000)
    
    if outline_str:
        try:
            m = re.search(r'```(?:json)?\s*\n(.*?)\n```', outline_str, re.DOTALL)
            if m:
                outline_str = m.group(1)
            parsed = json.loads(outline_str.strip())
            if isinstance(parsed, list) and len(parsed) > 0:
                st.success(f"✅ {len(parsed)} units!")
                return parsed
        except:
            st.error("❌ Parse error")
    return None

# UI Pages

def show_syllabus_upload_page():
    st.header("📄 Step 1: Syllabus")
    choice = st.radio("Choose:", ["Upload", "Skip"], key="choice")
    if choice == "Upload" and PYPDF2_AVAILABLE:
        up = st.file_uploader("PDF", type=['pdf'], key="syl")
        if up:
            text = extract_pdf_text(up)
            if text:
                st.success("✅")
                struct = parse_syllabus_structure(text)
                st.session_state.extracted_structure = struct
                if struct['units']:
                    for u in struct['units']:
                        with st.expander(f"Unit {u['unit_number']}: {u['unit_title']}"):
                            for i, t in enumerate(u['topics'], 1):
                                st.write(f"{i}. {t}")
                    if st.checkbox("✅ OK"):
                        if st.button("Continue", type="primary"):
                            st.session_state.step = 'configuration'
                            st.rerun()
    else:
        if st.button("Continue", type="primary"):
            st.session_state.step = 'configuration'
            st.rerun()

def show_configuration_page():
    st.header("⚙️ Step 2: Config")
    st.session_state.api_key = st.text_input("API", st.session_state.api_key, type="password")
    
    st.subheader("Course")
    ex = st.session_state.get('extracted_structure', {}).get('course_info', {})
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.course_title = st.text_input("Title", ex.get('title', st.session_state.course_title))
        st.session_state.course_code = st.text_input("Code", ex.get('code', st.session_state.course_code))
    with col2:
        st.session_state.credits = st.number_input("Credits", 1, 10, st.session_state.credits)
        st.session_state
