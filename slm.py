"""
COMPLETE AI CURRICULUM GENERATOR - V2.1 (FIXED)
===============================================
All features integrated: LLM-based Syllabus Parsing, Manual Outline Generation,
eGyankosh Style Content, PO/CO/PSO Mapping, Google Drive Upload, and Unit-wise PDF Compilation.
"""

import streamlit as st
import requests
import json
import time
import re
from datetime import datetime
from io import BytesIO
import pandas as pd

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
        Table, TableStyle, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# --- CONFIGURATION ---
DEFAULT_API_KEY = "xai-your-key-here" # Replace with your actual key if desired
API_URL = "https://api.x.ai/v1/chat/completions"
GDRIVE_SERVICE_ACCOUNT_EMAIL = "curriculum-generator@dynamic-wording-475018-e2.iam.gserviceaccount.com"
GDRIVE_CREDENTIALS = {
    "type": "service_account", "project_id": "dynamic-wording-475018-e2",
    "private_key_id": "2e97986797c2f143cc94209e0b0f97922146c958",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCJ/1wVoHvZvFvM\nxXxq1Zzd3XsC5g24nw9/TUdIvAvGsZU+6ZF9fxYScHpQzy2LpEwKYtaHmxsm/Ia8\n4eX33tcysd7K9vEWCPW1RckbNlzuLbCUHm5WU7pxhCB8AEBy2roD82RRkZvGhzgs\nBQFK4AbDEbuglT1BPej5+pSwJti4JaGjkozgum8ecvaZv3FLof5zp2/s0LDICOGB\nUVZCXvXDKetMLoZYJRm/W41T074NUXdmCCFtuyiXszNzzQa/HVy7yqo/5UxXQyRs\nZgAKSmp7EhtXkEozlBoMGhFXQHH6oIs9j4FtFKZ3w7/oLgCg2MqgX+G/1W7znaK6\n4i+vjrWTAgMBAAECggEAIzWh96yqXQxHufAbhiC5tQwpMjyjfJss95SunvrH4Gr4\nAwTSR9xws8S6GLs7yjjh4/aC+TeUjnZ5JGFY7U0QyFEE4PFv4ujnVFiZbtWIkYbb\n2ncHPQSA+iy1ox3nU8bGFnL4Ai3uOpHOvcCLK2EMqKHyJw9dATP8KSgL3wQSYK1t\nbbJQbuBec1W92//i1x2S2Ac0ppWyP379K3BiVcqPUUN83cqvklCeAdUNOfNro4o6\nSVgrAx4NF+EhnO158CNvJ70cKhY1Cyz3+ihPg2Z6UDL8RpcddrCScKYJqHp1Vsz+\nWHngLqR0InLCefcY16Pd90yFDWFlwm7xCUPjdOYAPQKBgQC9F66IHAvrLdGSz9OO\nxUuZQNPDU18/KUjO74/KNF4vSzd2Ye65rY5ai/BNeGNCUxRVyiUwlsdaEplPhEce\n7+3U0sP0NoxrOCYh0r0sBd7QpZWx5YBFsz/s3MVe10BvFaZWUOqUQHHOQRquyeEu\nCHsx2s5D86Zl6wNG9XSESV9A/wKBgQC602fqsWza40zqeqzN0YY/Bb0+LJoGSfwh\nMuWRAyhjJHGV/LomA2uLuwvLAaJ5vOOv+tCGhnQPV4s8P5NlNXDOggq7OTUBxWgG\nZxpJBop0RtV71M2/v6v/iyKpI05cc6prGRWv56oFQ3vdyB79EXBJx3epRBrW+URt\nDXgRq7b3bQKBgGAImvc9Z0A1sO4i5orn4JEgv2u/9+uYCAYw3JIRLpROWwigjCF4\n54dM8uolbiPNFdLMKz8WFIDGWV5tC8HGkL85m5N38LCzf4pGARVOle7ZacFDkXXU\np26gYQzdvTetgyDrT3ejkyjxH6ANn3NFk2uqeH9CSwwP40Yyes6EhP/5AoGAZ2Cj\nl9IlkdlErlrDVAAkcKsUVFsJv4Eg6p3nOZ6tsm5wC7aUqoQp9l/B3stAxGwo8S+w\nQ0AS6IpgmS30uYQgr6R1m7PECP7a2PAkM1RTOJQZfTP7xaah3f13aHAI5E98dVak\nEXn3MoJtAAPEYfRMVgbxx8/PqjS0EEPrtJt32uECgYEAi/8JnI8MAhq+eDcVuO45\nu/itREj4sHS/4dcTtL2mbUz8DKWyDpe6LC7/oMIl4459Ktp7MOanR/yPIvJfU8t6\ni+05OoFDvrDkXraE28wIHO0qIT1NY/htaNByBHNvs9b1Rj99O7o2sH8k8fG2OM0u\nxTEWjBaUn1bG59flELY88zk=\n-----END PRIVATE KEY-----\n",
    "client_email": GDRIVE_SERVICE_ACCOUNT_EMAIL, "client_id": "113202445348377169696",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/curriculum-generator%40dynamic-wording-475018-e2.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}


# --- SESSION STATE & CORE FUNCTIONS ---
def initialize_session_state():
    defaults = {
        'step': 'syllabus_upload', 'api_key': DEFAULT_API_KEY, 'course_title': 'Organizational Behaviour',
        'course_code': 'MBA101', 'credits': 3, 'target_audience': 'Postgraduate (MBA)', 'num_units': 4,
        'sections_per_unit': 8, 'program_objectives': '', 'program_outcomes': '', 'course_outcomes': '',
        'specialized_outcomes': '', 'use_egyankosh_style': True, 'extracted_structure': None,
        'gdrive_folder_url': '', 'gdrive_folder_id': None, 'gdrive_service': None, 'approved_outline': None,
        'content': {}, 'sections_to_process': [], 'failed_sections': [], 'uploaded_pdfs': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def make_api_call(messages, retries=3, delay=5, max_tokens=4000):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {st.session_state.api_key}"}
    payload = {"messages": messages, "model": "grok-1.5-flash-20240517", "temperature": 0.2, "max_tokens": max_tokens}
    
    for attempt in range(retries):
        try:
            with st.spinner(f"Communicating with AI... (Attempt {attempt + 1})"):
                response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content']
            st.warning(f"AI returned an empty response: {result}")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e.response.status_code} - {e.response.text[:200]}")
            if e.response.status_code == 401: return None # Auth error
            time.sleep(delay * (attempt + 1))
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            time.sleep(delay * (attempt + 1))
    st.error("All API attempts failed.")
    return None


# --- SYLLABUS PARSING & OUTLINE GENERATION ---
def extract_pdf_text(pdf_file):
    if not PYPDF2_AVAILABLE:
        st.error("PyPDF2 is not installed. Cannot read PDFs.")
        return None
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def parse_syllabus_with_llm(pdf_text):
    system_prompt = """
    You are an expert academic curriculum parser. Your task is to analyze the provided syllabus text and convert it into a structured JSON object.
    
    RULES:
    1.  Extract the course title, course code, and credits if available.
    2.  Identify all the main units or modules.
    3.  For each unit, list all the topics or section titles.
    4.  If you cannot find specific data, use `null`.
    5.  Your response MUST be ONLY the JSON object, with no introductory text, explanations, or markdown fences.
    
    JSON SCHEMA:
    {
      "course_info": {
        "title": "Course Title",
        "code": "COURSE101",
        "credits": 3
      },
      "units": [
        {
          "unit_number": 1,
          "unit_title": "Title of Unit 1",
          "topics": ["Topic 1.1", "Topic 1.2", "Topic 1.3"]
        }
      ]
    }
    """
    user_prompt = f"Here is the syllabus text. Please parse it into the specified JSON format:\n\n---\n\n{pdf_text}"
    response = make_api_call([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    if not response:
        return None
    try:
        # Clean up potential markdown fences
        json_str = re.search(r'\{.*\}', response, re.DOTALL).group(0)
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        st.error("AI failed to return valid JSON. The response will be displayed for debugging.")
        st.code(response)
        return None

def generate_outline_with_llm():
    system_prompt = """
    You are an expert curriculum designer for university-level courses. Generate a detailed course outline in a structured JSON format based on the user's request.
    
    RULES:
    1.  Create exactly the number of units and sections per unit requested.
    2.  Unit and section titles should be academic, clear, and logically sequenced.
    3.  Your response MUST be ONLY the JSON object, without any surrounding text or markdown.
    
    JSON SCHEMA:
    [
      {
        "unit_number": 1,
        "unit_title": "Descriptive Unit Title",
        "sections": [
          {"section_number": "1.1", "section_title": "Specific Section Title", "description": "A brief, one-sentence summary of the section's content."}
        ]
      }
    ]
    """
    user_prompt = f"""
    Please generate a course outline for:
    - Course Title: {st.session_state.course_title}
    - Target Audience: {st.session_state.target_audience}
    - Number of Units: {st.session_state.num_units}
    - Sections per Unit: {st.session_state.sections_per_unit}
    """
    response = make_api_call([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])
    if not response:
        return None
    try:
        json_str = re.search(r'\[.*\]', response, re.DOTALL).group(0)
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        st.error("AI failed to generate a valid JSON outline.")
        st.code(response)
        return None


# --- CONTENT GENERATION ---
def generate_egyankosh_content(section_info, course_context):
    system_prompt = f"""
    You are an expert academic content developer specializing in {course_context['target_audience']} education, writing in the eGyankosh/IGNOU self-learning material style.
    
    MANDATORY STRUCTURE (Follow this sequence exactly for each topic):
    1.  **Structure Overview**: A brief bulleted list of the sections to follow.
    2.  **Learning Objectives**: 3-4 specific objectives starting with action verbs (e.g., "After studying this section, you will be able to: - Define X, - Analyze Y").
    3.  **Introduction**: An engaging overview of the topic's relevance and what will be covered.
    4.  **Main Content Sections**: At least 3-4 detailed sections with clear headings (e.g., **Meaning and Definition**, **Key Theories**, **Practical Applications**). Use bold for headings.
    5.  **Examples and Case Studies**: Include at least one real-world example or a mini case study (from 2023-2025 where possible).
    6.  **CHECK YOUR PROGRESS**: A box with 3-5 questions to test understanding.
    7.  **Summary**: A concise recap of the key takeaways.
    8.  **Key Terms**: A glossary of 3-5 important terms defined in this section.
    
    WRITING STYLE & RULES:
    - Total length: 6,000-8,000 words. This is critical. Be comprehensive.
    - Language: Simple, clear, and academic. Grade 5 readability. Short sentences and paragraphs.
    - Formatting: Use **bold** for headings and key terms. Use bullet points (*) for lists.
    - PO/CO Mapping: At the very end, include a section mapping the content to the provided outcomes.
    - Do NOT invent section numbers; use the structure described above.
    """
    user_prompt = f"""
    Generate a complete, comprehensive, and lengthy self-learning module for the following topic:

    **COURSE**: {course_context['course_title']}
    **UNIT**: {section_info['unit_title']}
    **TOPIC**: {section_info['section_number']} - {section_info['section_title']}
    **DESCRIPTION**: {section_info['description']}

    Align the content with these academic outcomes:
    - **Program Outcomes (PO)**: {course_context['program_outcomes']}
    - **Course Outcomes (CO)**: {course_context['course_outcomes']}
    - **Specialized Outcomes (PSO)**: {course_context['specialized_outcomes']}
    
    Ensure the final output is a single, continuous block of text of at least 6,000 words.
    """
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    return make_api_call(messages, max_tokens=8000)


# --- PDF COMPILATION & GDRIVE ---
def setup_google_drive_connection():
    if not GDRIVE_AVAILABLE: return None
    try:
        creds = service_account.Credentials.from_service_account_info(GDRIVE_CREDENTIALS, scopes=['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Failed to connect to Google Drive: {e}")
        return None

def upload_to_gdrive(service, file_buffer, filename, folder_id):
    try:
        media = MediaIoBaseUpload(file_buffer, mimetype='application/pdf', resumable=True)
        file_metadata = {'name': filename, 'parents': [folder_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Upload to Google Drive failed: {e}")
        return None

def clean_and_format_text(text):
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    text = text.replace('\n', '<br/>')
    return text

def compile_unit_pdf(unit_data, course_info, content_dict):
    if not REPORTLAB_AVAILABLE:
        st.error("ReportLab not installed. Cannot generate PDFs.")
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('Title', parent=styles['h1'], fontSize=24, spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold')
    section_style = ParagraphStyle('Section', parent=styles['h2'], fontSize=14, spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], alignment=TA_JUSTIFY, leading=16)
    
    story = []
    
    # Cover Page
    story.append(Paragraph(f"UNIT {unit_data['unit_number']}", styles['h2']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(unit_data['unit_title'].upper(), title_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(course_info['course_title'], styles['h3']))
    story.append(Paragraph(f"Course Code: {course_info.get('course_code', 'N/A')} | Credits: {course_info.get('credits', 'N/A')}", styles['Normal']))
    story.append(PageBreak())
    
    # Content
    for section in unit_data.get('sections', []):
        sec_key = f"{section['section_number']} {section['section_title']}"
        raw_content = content_dict.get(sec_key, "[Content generation failed or is pending]")
        
        story.append(KeepTogether([
            Paragraph(f"<b>{sec_key}</b>", section_style),
            Table([['']], colWidths=[6.5 * inch], style=[('LINEBELOW', (0,0), (-1,0), 1, colors.black)])
        ]))
        
        paragraphs = re.split(r'\n{2,}', raw_content)
        for para in paragraphs:
            para = para.strip()
            if not para: continue
            
            if para.startswith(('* ', '- ')):
                items = para.split('\n')
                for item in items:
                    story.append(Paragraph(f"• {clean_and_format_text(item.strip('*- '))}", body_style, bulletText='•'))
            else:
                story.append(Paragraph(clean_and_format_text(para), body_style))
            story.append(Spacer(1, 0.1 * inch))
        story.append(PageBreak())

    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"PDF generation failed for Unit {unit_data['unit_number']}: {e}")
        return None


# --- STREAMLIT UI PAGES ---
def show_syllabus_upload_page():
    st.header("📄 Step 1: Provide Syllabus")
    st.info("You can upload an existing syllabus PDF for the AI to parse, or proceed manually.")

    choice = st.radio("How would you like to start?", ["Upload Syllabus PDF", "Configure Manually"], key="start_choice")

    if choice == "Upload Syllabus PDF":
        uploaded_file = st.file_uploader("Upload your syllabus", type=['pdf'])
        if uploaded_file:
            with st.spinner("Reading PDF..."):
                pdf_text = extract_pdf_text(uploaded_file)
            if pdf_text:
                with st.spinner("🤖 Asking AI to parse syllabus... This may take a moment."):
                    parsed_data = parse_syllabus_with_llm(pdf_text[:20000]) # Limit context size
                if parsed_data:
                    st.success("✅ AI successfully parsed the syllabus!")
                    st.session_state.extracted_structure = parsed_data
                    if st.button("➡️ Use this structure and continue", type="primary"):
                        st.session_state.step = 'configuration'
                        st.rerun()
    else:
        if st.button("➡️ Continue to Manual Configuration", type="primary"):
            st.session_state.extracted_structure = None # Ensure it's cleared
            st.session_state.step = 'configuration'
            st.rerun()

def show_configuration_page():
    st.header("⚙️ Step 2: Configure Course Details")
    
    # FIX: Safely get nested dictionary to prevent AttributeError
    extracted_structure = st.session_state.get('extracted_structure') or {}
    extracted_info = extracted_structure.get('course_info', {})
    
    st.session_state.course_title = st.text_input("Course Title", value=extracted_info.get('title') or st.session_state.course_title)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.course_code = st.text_input("Course Code", value=extracted_info.get('code') or st.session_state.course_code)
    with col2:
        st.session_state.credits = st.number_input("Credits", min_value=1, max_value=10, value=extracted_info.get('credits') or st.session_state.credits)

    st.session_state.target_audience = st.selectbox("Target Audience", ["Postgraduate (MBA)", "Undergraduate", "Professional Development"], index=0)

    with st.expander("🎯 Academic Mappings (PO/CO/PSO)"):
        st.session_state.program_outcomes = st.text_area("Program Outcomes (PO)", help="General skills from the entire program.")
        st.session_state.course_outcomes = st.text_area("Course Outcomes (CO)", help="Specific outcomes for this course.")
        st.session_state.specialized_outcomes = st.text_area("Program Specific Outcomes (PSO)", help="Specialized skills for this track.")
    
    if not st.session_state.get('extracted_structure'):
        with st.expander("📝 Manual Outline Structure"):
            col1, col2 = st.columns(2)
            st.session_state.num_units = col1.number_input("Number of Units", 1, 10, st.session_state.num_units)
            st.session_state.sections_per_unit = col2.number_input("Topics per Unit", 3, 15, st.session_state.sections_per_unit)

    with st.expander("☁️ Google Drive & API Settings"):
        st.session_state.api_key = st.text_input("Grok API Key", value=st.session_state.api_key, type="password")
        st.session_state.gdrive_folder_url = st.text_input("Google Drive Folder URL (Optional)")
        if st.session_state.gdrive_folder_url:
            folder_id = re.search(r'folders/([a-zA-Z0-9_-]+)', st.session_state.gdrive_folder_url)
            st.session_state.gdrive_folder_id = folder_id.group(1) if folder_id else None
            if st.session_state.gdrive_folder_id:
                st.success(f"Folder ID found: ...{st.session_state.gdrive_folder_id[-10:]}")
                st.info(f"Remember to share the folder with `{GDRIVE_SERVICE_ACCOUNT_EMAIL}`")
            else:
                st.warning("Could not extract Folder ID from URL.")

    col1, col2 = st.columns(2)
    col1.button("← Back to Syllabus", on_click=lambda: st.session_state.update(step='syllabus_upload'), use_container_width=True)
    col2.button("➡️ Review Outline", on_click=lambda: st.session_state.update(step='outline_generation'), use_container_width=True, type="primary")

def show_outline_page():
    st.header("📋 Step 3: Review and Edit Course Outline")

    if 'approved_outline' not in st.session_state:
        # Determine the source of the outline
        if st.session_state.get('extracted_structure'):
            st.info("Using the outline parsed from your syllabus.")
            parsed_outline = st.session_state.extracted_structure
            # Convert parsed data to the standard outline format
            outline_data = []
            for unit in parsed_outline.get('units', []):
                sections = [{'section_number': f"{unit['unit_number']}.{i+1}", 'section_title': topic, 'description': topic} for i, topic in enumerate(unit.get('topics', []))]
                outline_data.append({'unit_number': unit['unit_number'], 'unit_title': unit['unit_title'], 'sections': sections})
            st.session_state.outline_cache = outline_data
        else:
            st.info("No syllabus uploaded. Asking AI to generate a new outline...")
            with st.spinner("🤖 Generating a new course outline..."):
                st.session_state.outline_cache = generate_outline_with_llm()

    if not st.session_state.get('outline_cache'):
        st.error("Failed to generate an outline. Please go back and try again.")
        return

    # Prepare data for the editor
    rows = []
    for unit in st.session_state.outline_cache:
        for section in unit.get('sections', []):
            rows.append({'Unit': unit['unit_number'], 'Unit Title': unit['unit_title'], 'Section': section['section_number'], 'Section Title': section['section_title'], 'Description': section.get('description', '')})
    
    st.info("You can edit the unit/section titles and descriptions directly in the table.")
    edited_df = st.data_editor(pd.DataFrame(rows), num_rows="dynamic", use_container_width=True, height=500)

    def approve_outline():
        approved = []
        df = pd.DataFrame(edited_df)
        for unit_num, group in df.groupby('Unit'):
            unit_info = group.iloc[0]
            sections = [{'section_number': row['Section'], 'section_title': row['Section Title'], 'description': row['Description']} for _, row in group.iterrows()]
            approved.append({'unit_number': int(unit_num), 'unit_title': unit_info['Unit Title'], 'sections': sections})
        st.session_state.approved_outline = approved
        st.session_state.step = 'content_generation'

    col1, col2 = st.columns(2)
    col1.button("← Back to Configuration", on_click=lambda: st.session_state.update(step='configuration'), use_container_width=True)
    col2.button("✅ Approve & Generate Content", on_click=approve_outline, use_container_width=True, type="primary")

def show_content_generation_page():
    st.header("✍️ Step 4: AI Content Generation")

    if not st.session_state.get('approved_outline'):
        st.error("No outline approved. Please go back to the outline step.")
        return

    # Initialize processing queue
    if not st.session_state.get('sections_to_process'):
        st.session_state.content = {}
        st.session_state.failed_sections = []
        queue = []
        for unit in st.session_state.approved_outline:
            for section in unit.get('sections', []):
                queue.append({**section, 'unit_title': unit['unit_title']})
        st.session_state.sections_to_process = queue
    
    queue = st.session_state.sections_to_process
    completed_count = len(st.session_state.content)
    total_count = len(queue)

    st.progress(completed_count / total_count if total_count > 0 else 0)
    st.metric("Progress", f"{completed_count} / {total_count} Topics Generated")

    if completed_count < total_count:
        current_section = queue[completed_count]
        sec_key = f"{current_section['section_number']} {current_section['section_title']}"
        st.info(f"Currently generating: **{sec_key}**")

        course_context = {
            'course_title': st.session_state.course_title,
            'target_audience': st.session_state.target_audience,
            'program_outcomes': st.session_state.program_outcomes,
            'course_outcomes': st.session_state.course_outcomes,
            'specialized_outcomes': st.session_state.specialized_outcomes,
        }
        
        content = generate_egyankosh_content(current_section, course_context)
        
        if content and len(content) > 500: # Basic quality check
            st.session_state.content[sec_key] = content
            st.success(f"Successfully generated content for {sec_key}")
        else:
            st.session_state.content[sec_key] = "[CONTENT GENERATION FAILED]"
            st.session_state.failed_sections.append(sec_key)
            st.warning(f"Failed to generate adequate content for {sec_key}. It will be marked in the PDF.")
        
        time.sleep(1) # Small delay to allow UI to update
        st.rerun()
    else:
        st.success("🎉 All content has been generated!")
        if st.session_state.failed_sections:
            st.warning(f"The following {len(st.session_state.failed_sections)} sections failed to generate and will have placeholder text:")
            st.json(st.session_state.failed_sections)
        st.button("➡️ Proceed to PDF Compilation", on_click=lambda: st.session_state.update(step='compilation'), use_container_width=True, type="primary")

def show_compilation_page():
    st.header("📦 Step 5: Compile & Download")
    st.info("Your course content is ready. You can now compile each unit into a separate PDF document.")

    course_info = {k: st.session_state[k] for k in ['course_title', 'course_code', 'credits']}
    
    for unit_data in st.session_state.get('approved_outline', []):
        unit_num = unit_data['unit_number']
        with st.container(border=True):
            st.subheader(f"Unit {unit_num}: {unit_data['unit_title']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📄 Compile PDF for Unit {unit_num}", key=f"compile_{unit_num}", use_container_width=True):
                    with st.spinner(f"Generating PDF for Unit {unit_num}..."):
                        pdf_buffer = compile_unit_pdf(unit_data, course_info, st.session_state.content)
                        if pdf_buffer:
                            st.session_state.uploaded_pdfs[f"Unit_{unit_num}.pdf"] = pdf_buffer.getvalue()
                            st.success("Compilation successful!")
            
            pdf_key = f"Unit_{unit_num}.pdf"
            if pdf_key in st.session_state.uploaded_pdfs:
                with col2:
                    st.download_button(
                        label=f"⬇️ Download Unit {unit_num} PDF",
                        data=st.session_state.uploaded_pdfs[pdf_key],
                        file_name=f"{course_info['course_code']}_Unit_{unit_num}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                if st.session_state.gdrive_folder_id:
                    if st.button(f"☁️ Upload Unit {unit_num} to Drive", key=f"upload_{unit_num}", use_container_width=True):
                        service = setup_google_drive_connection()
                        if service:
                            with st.spinner("Uploading..."):
                                pdf_buffer = BytesIO(st.session_state.uploaded_pdfs[pdf_key])
                                link = upload_to_gdrive(service, pdf_buffer, f"{course_info['course_code']}_Unit_{unit_num}.pdf", st.session_state.gdrive_folder_id)
                                if link:
                                    st.link_button("View on Google Drive", link)


# --- MAIN APP LOGIC ---
st.set_page_config(layout="wide", page_title="AI Curriculum Generator")
st.title("🎓 AI Curriculum Generator V2.1")

# Check for required libraries
if not all([PYPDF2_AVAILABLE, GDRIVE_AVAILABLE, REPORTLAB_AVAILABLE]):
    st.warning("Some features may be disabled as required libraries are not installed. Please run: `pip install PyPDF2 google-api-python-client google-auth-httplib2 google-auth-oauthlib reportlab`")

initialize_session_state()

# Navigation & Page Routing
steps = ["Syllabus", "Configure", "Outline", "Generate", "Compile"]
step_map = {
    "Syllabus": "syllabus_upload", "Configure": "configuration", "Outline": "outline_generation",
    "Generate": "content_generation", "Compile": "compilation"
}
current_step_index = list(step_map.values()).index(st.session_state.step)
st.select_slider("Workflow Step", options=steps, value=steps[current_step_index], disabled=True)
st.markdown("---")

# Page router
if st.session_state.step == 'syllabus_upload': show_syllabus_upload_page()
elif st.session_state.step == 'configuration': show_configuration_page()
elif st.session_state.step == 'outline_generation': show_outline_page()
elif st.session_state.step == 'content_generation': show_content_generation_page()
elif st.session_state.step == 'compilation': show_compilation_page()
