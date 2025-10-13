"""
AI CURRICULUM GENERATOR - CLOUD-COMPATIBLE VERSION
==================================================
Works on Streamlit Cloud without LaTeX installation
"""

import streamlit as st
import requests
import json
import time
import os
import re
from datetime import datetime
import threading
from io import BytesIO

# Try importing reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configuration
DEFAULT_API_KEY = "xai-6QJwG3u6540lVZyXbFBArvLQ43ZyJsrnq65pyCWhxh5zXqNvtwe6LdTURbTwvE2sA3Uxlb9gn82Vamgu"
API_URL = "https://api.x.ai/v1/chat/completions"

content_lock = threading.Lock()

def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'step': 'configuration',
        'api_key': DEFAULT_API_KEY,
        'custom_model': '',
        'course_title': 'Organisational Behaviour: Concept, Nature & Historical Perspectives',
        'target_audience': 'Postgraduate (MBA)',
        'learning_objectives': 'Comprehensive course content',
        'num_units': 4,
        'sections_per_unit': 8
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_api_headers():
    api_key = st.session_state.get('api_key', DEFAULT_API_KEY)
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def make_api_call(messages, retries=2, delay=3, timeout=180, max_tokens=2000):
    """Optimized API call with configurable max_tokens"""
    headers = get_api_headers()
    
    if st.session_state.get('custom_model', '').strip():
        models = [st.session_state.custom_model]
    else:
        models = ["grok-2-1212"]
    
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
                response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    break
                elif e.response.status_code == 401:
                    st.error("❌ Invalid API Key")
                    return None
                if attempt < retries - 1:
                    time.sleep(delay)
            except Exception:
                if attempt < retries - 1:
                    time.sleep(delay)
    
    return None
def compile_pdf_reportlab(course_title, content_dict, outline, target_audience="Postgraduate"):
    """Generate PDF using ReportLab (cloud-compatible)"""
    
    if not REPORTLAB_AVAILABLE:
        st.error("❌ PDF generation library not available. Installing dependencies...")
        st.code("pip install reportlab", language="bash")
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    chapter_style = ParagraphStyle(
        'CustomChapter',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'CustomSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=16
    )
    
    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("UNIT 1", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(course_title, title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Academic Study Material", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"For {target_audience}", styles['Normal']))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(PageBreak())
    
    # Structure Page
    story.append(Paragraph("Structure", chapter_style))
    story.append(Spacer(1, 0.3*inch))
    
    section_num = 1.1
    for unit in outline:
        for section in unit.get('sections', []):
            sec_title = section.get('section_title', 'Untitled')
            story.append(Paragraph(f"{section_num} {sec_title}", body_style))
            section_num = round(section_num + 0.1, 1)
    
    story.append(PageBreak())
    
    # Main Content
    for unit in outline:
        unit_num = unit.get('unit_number', 1)
        unit_title = unit.get('unit_title', 'Untitled')
        
        # Unit title
        story.append(Paragraph(f"UNIT {unit_num}: {unit_title.upper()}", chapter_style))
        story.append(Spacer(1, 0.3*inch))
        
        for section in unit.get('sections', []):
            sec_num = section.get('section_number', '1.1')
            sec_title = section.get('section_title', 'Untitled')
            sec_key = f"{sec_num} {sec_title}"
            
            # Section title
            story.append(Paragraph(f"{sec_key}", section_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Section content
            content = content_dict.get(sec_key, "[Content not generated]")
            
            # Process content - convert markdown-like formatting
            paragraphs = content.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    # Handle Check Your Progress sections
                    if 'CHECK YOUR PROGRESS' in para.upper():
                        # Create a box for check your progress
                        story.append(Spacer(1, 0.2*inch))
                        progress_style = ParagraphStyle(
                            'Progress',
                            parent=body_style,
                            backColor=colors.lightgrey,
                            borderColor=colors.black,
                            borderWidth=1,
                            borderPadding=10
                        )
                        story.append(Paragraph("<b>CHECK YOUR PROGRESS</b>", progress_style))
                        
                        # Extract questions
                        questions = re.findall(r'\d+\.\s*(.+?)(?=\d+\.|$)', para, re.DOTALL)
                        for q in questions:
                            if q.strip():
                                story.append(Paragraph(f"• {q.strip()}", body_style))
                        story.append(Spacer(1, 0.2*inch))
                    
                    # Handle bullet points
                    elif para.strip().startswith('*') or para.strip().startswith('-'):
                        items = para.split('\n')
                        for item in items:
                            if item.strip():
                                clean_item = re.sub(r'^[\*\-]\s*', '', item.strip())
                                story.append(Paragraph(f"• {clean_item}", body_style))
                    
                    # Handle bold text
                    else:
                        # Convert **text** to <b>text</b>
                        para = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', para)
                        # Convert *text* to <i>text</i>
                        para = re.sub(r'\*(.+?)\*', r'<i>\1</i>', para)
                        
                        try:
                            story.append(Paragraph(para, body_style))
                            story.append(Spacer(1, 0.1*inch))
                        except:
                            # If paragraph parsing fails, add as plain text
                            story.append(Paragraph(para.replace('<', '&lt;').replace('>', '&gt;'), body_style))
                            story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
    
    # Build PDF
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ PDF generation error: {str(e)}")
        return None

def generate_section_content(section_info, course_context):
    """Generate content for a single section"""
    system_prompt = f"""You are an expert academic writer for {course_context['target_audience']} level courses.

CRITICAL INSTRUCTIONS:
- Write ONLY for section: {section_info['section_number']} {section_info['section_title']}
- Write 500-700 words
- Use clear academic language
- Include relevant examples
- Format with bullet points where appropriate
- Add one "CHECK YOUR PROGRESS" section at the end with 3-4 questions

FORMAT:
- Use * for bullet points
- Use ** for bold text
- Add: --- CHECK YOUR PROGRESS ---
  1. Question one?
  2. Question two?
  ---

DO NOT write about other sections."""

    user_prompt = f"""Write complete academic content for this section ONLY:

**Section:** {section_info['section_number']} {section_info['section_title']}
**Unit:** {section_info['unit_title']}
**Topics to cover:** {section_info['description']}
**Course:** {course_context['course_title']}
**Audience:** {course_context['target_audience']}

Write clear, comprehensive content for THIS SECTION ONLY."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return make_api_call(messages)

def show_navigation():
    """Show navigation breadcrumb"""
    steps = {
        'configuration': '1️⃣ Configuration',
        'outline_generation': '2️⃣ Outline',
        'content_generation': '3️⃣ Content Generation',
        'compilation': '4️⃣ Compilation'
    }
    
    current_step = st.session_state.get('step', 'configuration')
    
    cols = st.columns(len(steps))
    for idx, (step_key, step_name) in enumerate(steps.items()):
        with cols[idx]:
            if step_key == current_step:
                st.markdown(f"**🔵 {step_name}**")
            else:
                st.markdown(f"⚪ {step_name}")
    
    st.divider()

def show_configuration_page():
    st.header("⚙️ Step 1: Configure Your Course")
    
    st.subheader("🔑 API Configuration")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        use_custom = st.checkbox("Use Custom Model Name", key="use_custom_model")
    with col2:
        if use_custom:
            custom_model = st.text_input(
                "Model Name",
                value=st.session_state.get('custom_model', 'grok-2-1212'),
                key="custom_model_input"
            )
            st.session_state.custom_model = custom_model
    
    col1, col2 = st.columns([3, 1])
    with col1:
        api_key = st.text_input(
            "Grok API Key",
            value=st.session_state.get('api_key', DEFAULT_API_KEY),
            type="password",
            key="api_key_input"
        )
        st.session_state.api_key = api_key
        
        if api_key and api_key.startswith('xai-'):
            st.success("✅ Valid API key format")
    
    with col2:
        if st.button("🧪 Test API", use_container_width=True, key="test_api_btn"):
            with st.spinner("Testing connection..."):
                resp = make_api_call([{"role": "user", "content": "Hi"}])
                if resp:
                    st.success("✅ API Working!")
                else:
                    st.error("❌ API Test Failed")
    
    st.divider()
    st.subheader("📚 Course Details")
    
    course_title = st.text_input(
        "Course Title",
        value=st.session_state.course_title,
        key="course_title_input"
    )
    st.session_state.course_title = course_title
    
    target_audience = st.selectbox(
        "Target Audience",
        ["Postgraduate (MBA)", "Undergraduate", "Professional Development"],
        index=0,
        key="target_audience_select"
    )
    st.session_state.target_audience = target_audience
    
    learning_objectives = st.text_area(
        "Learning Objectives (Optional)",
        value=st.session_state.learning_objectives,
        key="learning_objectives_input",
        height=100
    )
    st.session_state.learning_objectives = learning_objectives
    
    num_units = st.number_input(
        "Number of Units",
        min_value=1,
        max_value=10,
        value=st.session_state.num_units,
        key="num_units_input"
    )
    st.session_state.num_units = num_units
    
    sections_per_unit = st.number_input(
        "Sections per Unit",
        min_value=3,
        max_value=15,
        value=st.session_state.sections_per_unit,
        key="sections_per_unit_input"
    )
    st.session_state.sections_per_unit = sections_per_unit
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Generate Course Outline", type="primary", use_container_width=True, key="gen_outline_btn"):
            if st.session_state.api_key:
                st.session_state.step = "outline_generation"
                st.rerun()
            else:
                st.error("⚠️ Please enter an API key first!")
    
    with col2:
        if 'outline' in st.session_state or 'approved_outline' in st.session_state:
            if st.button("➡️ Continue to Outline", use_container_width=True, key="continue_outline_btn"):
                st.session_state.step = "outline_generation"
                st.rerun()

def show_outline_page():
    st.header("📋 Step 2: Review Course Outline")
    
    if 'outline' not in st.session_state:
        with st.spinner("🤖 Generating course outline..."):
            num_units = st.session_state.get('num_units', 4)
            sections_per_unit = st.session_state.get('sections_per_unit', 8)
            
            system_prompt = """Create a comprehensive JSON array of course units with sections.

YOU MUST CREATE THE EXACT NUMBER OF UNITS AND SECTIONS REQUESTED.

STRICT JSON FORMAT:
[
  {
    "unit_number": 1,
    "unit_title": "Descriptive Unit Title",
    "sections": [
      {
        "section_number": "1.1",
        "section_title": "Descriptive Section Title",
        "description": "Brief description of what this section covers"
      },
      {
        "section_number": "1.2",
        "section_title": "Another Section Title",
        "description": "What topics are covered here"
      }
    ]
  },
  {
    "unit_number": 2,
    "unit_title": "Second Unit Title",
    "sections": [...]
  }
]

CRITICAL REQUIREMENTS:
1. Create EXACTLY the number of units requested
2. Each unit must have EXACTLY the number of sections requested
3. Section numbers follow the pattern: 1.1, 1.2, 1.3... for unit 1, then 2.1, 2.2, 2.3... for unit 2
4. Each section must have a unique, descriptive title relevant to the course
5. Return ONLY valid JSON, no explanations or additional text"""

            user_prompt = f"""Course Title: {st.session_state.course_title}
Target Audience: {st.session_state.target_audience}
Learning Objectives: {st.session_state.learning_objectives}

REQUIREMENTS:
- Create EXACTLY {num_units} units
- Each unit must have EXACTLY {sections_per_unit} sections
- Total sections will be: {num_units * sections_per_unit}

Create a comprehensive course outline with:
- Unit 1, Unit 2, Unit 3, etc. (up to {num_units})
- Each unit should have sections numbered appropriately (1.1-1.{sections_per_unit}, 2.1-2.{sections_per_unit}, etc.)
- Make titles specific and relevant to "{st.session_state.course_title}"
- Include varied topics across all units

Return ONLY the JSON array, nothing else."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            outline_str = make_api_call(messages)
            
            if outline_str:
                try:
                    # Extract JSON from response
                    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', outline_str, re.DOTALL)
                    if json_match:
                        outline_str = json_match.group(1)
                    
                    # Clean up the string
                    outline_str = outline_str.strip()
                    
                    # Parse JSON
                    parsed_outline = json.loads(outline_str)
                    
                    # Validate the outline has correct structure
                    if isinstance(parsed_outline, list) and len(parsed_outline) > 0:
                        st.session_state.outline = parsed_outline
                        
                        # Check if we got the right number
                        actual_units = len(parsed_outline)
                        if actual_units < num_units:
                            st.warning(f"⚠️ Generated {actual_units} units instead of {num_units}. You can add more in the editor.")
                        
                        st.success(f"✅ Outline generated with {actual_units} units!")
                    else:
                        st.error("❌ Invalid outline structure. Using default.")
                        st.session_state.outline = create_comprehensive_outline(num_units, sections_per_unit)
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Failed to parse outline: {str(e)}")
                    st.warning("Using default comprehensive outline...")
                    st.session_state.outline = create_comprehensive_outline(num_units, sections_per_unit)
            else:
                st.error("❌ API call failed. Using default comprehensive outline.")
                st.session_state.outline = create_comprehensive_outline(num_units, sections_per_unit)
    
    if 'outline' in st.session_state:
        total_sections = sum(len(unit.get('sections', [])) for unit in st.session_state.outline)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Units", len(st.session_state.outline))
        with col2:
            st.metric("📄 Total Sections", total_sections)
        with col3:
            estimated_pages = (total_sections * 2) + 10
            st.metric("📖 Est. Pages", f"~{estimated_pages}")
        
        st.divider()
        
        rows = []
        for unit in st.session_state.outline:
            for section in unit.get('sections', []):
                rows.append({
                    'Unit': unit['unit_number'],
                    'Unit Title': unit['unit_title'],
                    'Section': section['section_number'],
                    'Section Title': section['section_title'],
                    'Description': section['description']
                })
        
        st.subheader("✏️ Edit Outline (Click cells to edit)")
        edited = st.data_editor(
            rows,
            num_rows="dynamic",
            use_container_width=True,
            height=500,
            column_config={
                "Unit": st.column_config.NumberColumn("Unit #", width="small"),
                "Unit Title": st.column_config.TextColumn("Unit Title", width="medium"),
                "Section": st.column_config.TextColumn("Section #", width="small"),
                "Section Title": st.column_config.TextColumn("Section Title", width="medium"),
                "Description": st.column_config.TextColumn("Description", width="large")
            },
            key="outline_editor"
        )
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back to Configuration", use_container_width=True, key="back_to_config_btn"):
                st.session_state.step = "configuration"
                st.rerun()
        
        with col2:
            if st.button("✅ Approve & Start", type="primary", use_container_width=True, key="approve_outline_btn"):
                approved = []
                current = None
                
                for row in edited:
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
                st.session_state.step = "content_generation"
                st.rerun()
        
        with col3:
            if 'content' in st.session_state and st.session_state.content:
                if st.button("➡️ Continue to Content", use_container_width=True, key="continue_content_btn"):
                    st.session_state.step = "content_generation"
                    st.rerun()


def create_comprehensive_outline(num_units=4, sections_per_unit=8):
    """Create a comprehensive default outline based on the course"""
    outline = []
    
    # Base topics for Organizational Behaviour course
    base_topics = [
        {
            "title": "Introduction and Foundations",
            "sections": [
                "Introduction to Organisational Behaviour",
                "Objectives and Learning Outcomes",
                "Meaning and Definition",
                "Historical Perspective",
                "Different Approaches and Theories",
                "Organisational Behaviour in Educational Institutions",
                "Need to Study Organisational Behaviour",
                "Goals of Organisational Behaviour"
            ]
        },
        {
            "title": "Individual Behaviour and Personality",
            "sections": [
                "Understanding Individual Behaviour",
                "Personality and Its Determinants",
                "Personality Theories",
                "Perception and Individual Decision Making",
                "Values and Attitudes",
                "Learning and Behaviour Modification",
                "Motivation Theories",
                "Job Satisfaction and Performance"
            ]
        },
        {
            "title": "Group Dynamics and Teams",
            "sections": [
                "Foundations of Group Behaviour",
                "Stages of Group Development",
                "Group Decision Making",
                "Communication in Organizations",
                "Leadership Concepts and Theories",
                "Power and Politics",
                "Conflict and Negotiation",
                "Team Building and Effectiveness"
            ]
        },
        {
            "title": "Organizational Structure and Culture",
            "sections": [
                "Organizational Structure Fundamentals",
                "Organizational Design",
                "Organizational Culture",
                "Change Management",
                "Organizational Development",
                "Stress Management",
                "Work-Life Balance",
                "Future of Organizational Behaviour"
            ]
        }
    ]
    
    for i in range(num_units):
        unit_num = i + 1
        
        # Use predefined topics or generate generic ones
        if i < len(base_topics):
            unit_title = base_topics[i]["title"]
            section_titles = base_topics[i]["sections"]
        else:
            unit_title = f"Advanced Topics in Organisational Behaviour - Part {i - len(base_topics) + 1}"
            section_titles = [
                f"Topic {j+1}" for j in range(sections_per_unit)
            ]
        
        sections = []
        for j in range(sections_per_unit):
            section_num = f"{unit_num}.{j+1}"
            
            if j < len(section_titles):
                section_title = section_titles[j]
            else:
                section_title = f"Additional Topic {j+1}"
            
            sections.append({
                "section_number": section_num,
                "section_title": section_title,
                "description": f"Comprehensive coverage of {section_title.lower()}"
            })
        
        outline.append({
            "unit_number": unit_num,
            "unit_title": unit_title,
            "sections": sections
        })
    
    return outline


def create_default_outline():
    """Create a minimal default outline if generation completely fails"""
    return create_comprehensive_outline(2, 4)
def create_default_outline():
    """Create a default outline if generation fails"""
    return [
        {
            "unit_number": 1,
            "unit_title": "Introduction",
            "sections": [
                {
                    "section_number": "1.1",
                    "section_title": "Overview",
                    "description": "Introduction to the subject"
                },
                {
                    "section_number": "1.2",
                    "section_title": "Objectives",
                    "description": "Learning objectives"
                }
            ]
        }
    ]

def show_content_generation_page():
    st.header("✍️ Step 3: Automated Content Generation")
    
    if 'approved_outline' not in st.session_state:
        st.error("❌ No approved outline found")
        if st.button("← Go Back to Outline", key="back_outline_err_btn"):
            st.session_state.step = "outline_generation"
            st.rerun()
        return
    
    if 'content' not in st.session_state:
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
        if completed > 0:
            elapsed = time.time() - st.session_state.generation_start_time
            avg_time = elapsed / completed
            eta_seconds = avg_time * remaining
            eta_minutes = int(eta_seconds / 60)
            st.metric("⏱️ ETA", f"~{eta_minutes}min")
    
    st.progress(completed / total if total > 0 else 0)
    
    if completed < total:
        current = st.session_state.sections_to_process[completed]
        section_key = f"{current['section_number']} {current['section_title']}"
        
        st.info(f"🤖 Currently generating: **{section_key}**")
        
        with st.spinner(f"Writing section {completed + 1} of {total}..."):
            course_context = {
                'course_title': st.session_state.course_title,
                'target_audience': st.session_state.target_audience
            }
            
            content = generate_section_content(current, course_context)
            
            if content:
                with content_lock:
                    st.session_state.content[section_key] = content
                st.success(f"✅ Completed: {section_key}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(f"❌ Failed to generate: {section_key}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Retry", use_container_width=True, key="retry_gen_btn"):
                        st.rerun()
                with col2:
                    if st.button("⏭️ Skip", use_container_width=True, key="skip_gen_btn"):
                        with content_lock:
                            st.session_state.content[section_key] = f"[Content for {section_key} - To be added]"
                        st.rerun()
    else:
        st.success("🎉 All content generated successfully!")
        
        total_words = sum(len(c.split()) for c in st.session_state.content.values())
        total_chars = sum(len(c) for c in st.session_state.content.values())
        estimated_pages = total_chars / 3000
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Total Words", f"{total_words:,}")
        with col2:
            st.metric("📄 Total Sections", total)
        with col3:
            st.metric("📖 Estimated Pages", f"~{estimated_pages:.0f}")
        
        st.divider()
        
        if st.checkbox("👁️ Preview Generated Content", key="preview_content_check"):
            for unit in st.session_state.approved_outline:
                with st.expander(f"📚 Unit {unit['unit_number']}: {unit['unit_title']}", expanded=False):
                    for section in unit.get('sections', []):
                        sec_key = f"{section['section_number']} {section['section_title']}"
                        if sec_key in st.session_state.content:
                            st.markdown(f"### {sec_key}")
                            st.markdown(st.session_state.content[sec_key][:500] + "...")
                            st.caption(f"📊 {len(st.session_state.content[sec_key].split())} words")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back to Outline", use_container_width=True, key="back_outline_content_btn"):
                st.session_state.step = "outline_generation"
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate All", use_container_width=True, key="regen_all_btn"):
                if st.checkbox("⚠️ Delete all content and regenerate?", key="regen_confirm"):
                    del st.session_state.content
                    del st.session_state.sections_to_process
                    st.rerun()
        
        with col3:
            if st.button("📄 Compile PDF", type="primary", use_container_width=True, key="compile_pdf_btn"):
                st.session_state.step = "compilation"
                st.rerun()

def show_compilation_page():
    st.header("📄 Step 4: Compile PDF")
    
    # Verify all required data exists
    if 'content' not in st.session_state or not st.session_state.content:
        st.error("❌ No content found to compile")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Content Generation", use_container_width=True, key="back_content_comp_err_btn"):
                st.session_state.step = "content_generation"
                st.rerun()
        with col2:
            if st.button("🏠 Start Over", use_container_width=True, key="start_over_comp_err_btn"):
                for key in list(st.session_state.keys()):
                    if key not in ['api_key', 'custom_model']:
                        del st.session_state[key]
                st.session_state.step = "configuration"
                st.rerun()
        return
    
    if 'approved_outline' not in st.session_state:
        st.error("❌ No outline found")
        if st.button("← Back to Outline", use_container_width=True, key="back_outline_comp_err_btn"):
            st.session_state.step = "outline_generation"
            st.rerun()
        return
    
    # Show summary before compilation
    st.subheader("📊 Document Summary")
    
    total_sections = len(st.session_state.content)
    total_words = sum(len(c.split()) for c in st.session_state.content.values())
    total_chars = sum(len(c) for c in st.session_state.content.values())
    estimated_pages = total_chars / 3000
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Units", len(st.session_state.approved_outline))
    with col2:
        st.metric("📄 Sections", total_sections)
    with col3:
        st.metric("📝 Words", f"{total_words:,}")
    with col4:
        st.metric("📖 Est. Pages", f"~{estimated_pages:.0f}")
    
    st.divider()
    
    # Library check
    if not REPORTLAB_AVAILABLE:
        st.error("❌ PDF generation library not installed")
        st.info("📦 Installing required library: reportlab")
        st.code("pip install reportlab")
        st.warning("Please install the required library and restart the app")
        return# Compilation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Content", use_container_width=True, key="back_content_comp_btn"):
            st.session_state.step = "content_generation"
            st.rerun()
    
    with col2:
        if st.button("📝 Edit Content", use_container_width=True, key="edit_content_comp_btn"):
            st.session_state.show_editor = True
            st.rerun()
    
    with col3:
        compile_button = st.button("🔨 Compile PDF", type="primary", use_container_width=True, key="compile_now_btn")
    
    # Show editor if requested
    if st.session_state.get('show_editor', False):
        st.divider()
        st.subheader("✏️ Quick Content Editor")
        
        for unit_idx, unit in enumerate(st.session_state.approved_outline):
            with st.expander(f"UNIT {unit['unit_number']}: {unit['unit_title']}", key=f"unit_exp_{unit_idx}"):
                for sec_idx, section in enumerate(unit.get('sections', [])):
                    sec_key = f"{section['section_number']} {section['section_title']}"
                    if sec_key in st.session_state.content:
                        st.markdown(f"**{sec_key}**")
                        edited_content = st.text_area(
                            "Edit content:",
                            value=st.session_state.content[sec_key],
                            height=200,
                            key=f"edit_{unit_idx}_{sec_idx}"
                        )
                        if st.button(f"💾 Save", key=f"save_{unit_idx}_{sec_idx}"):
                            st.session_state.content[sec_key] = edited_content
                            st.success(f"✅ Saved: {sec_key}")
        
        if st.button("✅ Done Editing", key="done_editing_btn"):
            st.session_state.show_editor = False
            st.rerun()
        
        st.divider()
    
    # Perform compilation
    if compile_button:
        with st.spinner("🔨 Compiling PDF... This may take 30-60 seconds"):
            pdf_buffer = compile_pdf_reportlab(
                st.session_state.course_title,
                st.session_state.content,
                st.session_state.approved_outline,
                st.session_state.target_audience
            )
        
        if pdf_buffer:
            st.success("✅ PDF Compiled Successfully!")
            
            pdf_bytes = pdf_buffer.getvalue()
            
            st.divider()
            
            # Download section
            st.subheader("📥 Download Your Document")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                download_filename = f"{st.session_state.course_title.replace(' ', '_')[:50]}.pdf"
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=download_filename,
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="download_pdf_btn"
                )
            
            with col2:
                if st.button("🔄 Recompile", use_container_width=True, key="recompile_btn"):
                    st.rerun()
            
            with col3:
                if st.button("🏠 New Project", use_container_width=True, key="new_project_btn"):
                    api_key = st.session_state.get('api_key')
                    custom_model = st.session_state.get('custom_model')
                    st.session_state.clear()
                    st.session_state.api_key = api_key
                    st.session_state.custom_model = custom_model
                    st.session_state.step = "configuration"
                    st.rerun()
            
            # Show file info
            st.info(f"📊 PDF Size: {len(pdf_bytes) / 1024:.2f} KB")
            
        else:
            st.error("❌ PDF compilation failed")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True, key="try_again_comp_btn"):
                    st.rerun()
            with col2:
                if st.button("← Back to Content", use_container_width=True, key="back_content_fail_btn"):
                    st.session_state.step = "content_generation"
                    st.rerun()

def main():
    st.set_page_config(
        page_title="AI Curriculum Generator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stButton button {
        border-radius: 5px;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🎓 AI Curriculum Generator")
    st.caption("Generate professional academic course materials with AI")
    
    # Initialize session state
    initialize_session_state()
    
    # Show navigation breadcrumb
    show_navigation()
    
    # Show current step
    current_step = st.session_state.get('step', 'configuration')
    
    if current_step == "configuration":
        show_configuration_page()
    elif current_step == "outline_generation":
        show_outline_page()
    elif current_step == "content_generation":
        show_content_generation_page()
    elif current_step == "compilation":
        show_compilation_page()
    else:
        st.error("❌ Unknown step. Resetting...")
        st.session_state.step = "configuration"
        st.rerun()
    
    # Sidebar with progress info
    with st.sidebar:
        st.header("📊 Project Status")
        
        if 'course_title' in st.session_state:
            st.markdown(f"**Course:** {st.session_state.course_title[:50]}...")
        
        if 'approved_outline' in st.session_state:
            units = len(st.session_state.approved_outline)
            sections = sum(len(u.get('sections', [])) for u in st.session_state.approved_outline)
            st.metric("Units", units)
            st.metric("Sections", sections)
        
        if 'content' in st.session_state:
            completed = len(st.session_state.content)
            st.metric("Content Generated", completed)
            
            if 'sections_to_process' in st.session_state:
                total = len(st.session_state.sections_to_process)
                progress = (completed / total * 100) if total > 0 else 0
                st.progress(progress / 100)
                st.caption(f"{progress:.0f}% Complete")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🏠 Start Over", use_container_width=True, key="sidebar_start_over"):
            if st.checkbox("⚠️ Clear all data?", key="sidebar_reset"):
                api_key = st.session_state.get('api_key')
                custom_model = st.session_state.get('custom_model')
                st.session_state.clear()
                st.session_state.api_key = api_key
                st.session_state.custom_model = custom_model
                st.session_state.step = "configuration"
                st.rerun()
        
        if 'content' in st.session_state and st.session_state.content:
            if st.button("💾 Save Progress", use_container_width=True, key="sidebar_save"):
                save_data = {
                    'course_title': st.session_state.course_title,
                    'target_audience': st.session_state.target_audience,
                    'outline': st.session_state.get('approved_outline', []),
                    'content': st.session_state.content,
                    'timestamp': datetime.now().isoformat()
                }
                
                json_str = json.dumps(save_data, indent=2)
                st.download_button(
                    label="📥 Download Backup",
                    data=json_str,
                    file_name=f"curriculum_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_backup_btn"
                )
        
        st.divider()
        
        # System info
        st.subheader("ℹ️ System Info")
        st.caption(f"PDF Library: {'✅ Installed' if REPORTLAB_AVAILABLE else '❌ Not installed'}")
        st.caption("💡 Tip: Your progress is saved in this session")
        st.caption("⚠️ Don't refresh the page")

if __name__ == "__main__":
    main()
