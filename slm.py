"""
AI CURRICULUM GENERATOR - COMPLETE WORKING VERSION
==================================================
Full-featured, cloud-compatible academic curriculum generator
"""

import streamlit as st
import requests
import json
import time
import os
import re
from datetime import datetime
from io import BytesIO

# Try importing reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
        Table, TableStyle, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Configuration
DEFAULT_API_KEY = "xai-6QJwG3u6540lVZyXbFBArvLQ43ZyJsrnq65pyCWhxh5zXqNvtwe6LdTURbTwvE2sA3Uxlb9gn82Vamgu"
API_URL = "https://api.x.ai/v1/chat/completions"

def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'step': 'configuration',
        'api_key': DEFAULT_API_KEY,
        'custom_model': '',
        'course_title': 'Organisational Behaviour: Concept, Nature & Historical Perspectives',
        'target_audience': 'Postgraduate (MBA)',
        'learning_objectives': 'Comprehensive MBA course content covering fundamental concepts and advanced topics',
        'num_units': 4,
        'sections_per_unit': 8
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_api_headers():
    """Get API headers with authentication"""
    api_key = st.session_state.get('api_key', DEFAULT_API_KEY)
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

def make_api_call(messages, retries=3, delay=2, timeout=120, max_tokens=2000):
    """Make API call with retries and error handling"""
    headers = get_api_headers()
    
    # Determine which model to use
    if st.session_state.get('custom_model', '').strip():
        models = [st.session_state.custom_model]
    else:
        models = ["grok-2-1212", "grok-beta"]  # Try multiple models
    
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
                    st.warning(f"Model {model} not found, trying next...")
                    break  # Try next model
                elif e.response.status_code == 401:
                    st.error("❌ Invalid API Key - Please check your API key")
                    return None
                elif e.response.status_code == 429:
                    st.warning("⏳ Rate limited, waiting longer...")
                    time.sleep(delay * 2)
                else:
                    if attempt < retries - 1:
                        st.warning(f"⏳ Retrying in {delay} seconds...")
                        time.sleep(delay)
            except requests.exceptions.Timeout:
                st.error(f"⏰ Request timeout after {timeout} seconds")
                if attempt < retries - 1:
                    time.sleep(delay)
            except requests.exceptions.RequestException as e:
                st.error(f"🔌 Network error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
    
    st.error("❌ All API attempts failed across all models")
    return None

def clean_text_for_pdf(text):
    """Remove markdown formatting for PDF generation"""
    if not text:
        return ""
    
    # Remove bold markers **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic markers *text*
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)
    
    return text

def compile_pdf_reportlab(course_title, content_dict, outline, target_audience="Postgraduate", uploaded_images=None):
    """Generate PDF using ReportLab"""
    
    if not REPORTLAB_AVAILABLE:
        st.error("❌ PDF generation library not available")
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=18
    )
    
    story = []
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
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10
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
            story.append(Paragraph(f"{section_num:.1f} {sec_title}", body_style))
            section_num += 0.1
    
    story.append(PageBreak())
    
    # Main Content
    for unit in outline:
        unit_num = unit.get('unit_number', 1)
        unit_title = unit.get('unit_title', 'Untitled')
        
        story.append(Paragraph(f"UNIT {unit_num}: {unit_title.upper()}", chapter_style))
        story.append(Spacer(1, 0.3*inch))
        
        for section in unit.get('sections', []):
            sec_num = section.get('section_number', '1.1')
            sec_title = section.get('section_title', 'Untitled')
            sec_key = f"{sec_num} {sec_title}"
            
            story.append(Paragraph(f"{sec_key}", section_style))
            story.append(Spacer(1, 0.2*inch))
            
            raw_content = content_dict.get(sec_key, "[Content not generated]")
            content = clean_text_for_pdf(raw_content)
            
            # Process content
            lines = content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # Check Your Progress
                if 'CHECK YOUR PROGRESS' in line.upper():
                    story.append(Spacer(1, 0.2*inch))
                    progress_data = [[Paragraph("<b>CHECK YOUR PROGRESS</b>", body_style)]]
                    progress_table = Table(progress_data, colWidths=[6.5*inch])
                    progress_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('BORDER', (0, 0), (-1, -1), 1, colors.black),
                        ('PADDING', (0, 0), (-1, -1), 10),
                    ]))
                    story.append(progress_table)
                    story.append(Spacer(1, 0.1*inch))
                    
                    i += 1
                    while i < len(lines):
                        q_line = lines[i].strip()
                        if not q_line or q_line == '---':
                            break
                        q_line = re.sub(r'^\d+\.\s*', '', q_line)
                        q_line = clean_text_for_pdf(q_line)
                        if q_line:
                            try:
                                story.append(Paragraph(f"• {q_line}", bullet_style))
                            except:
                                pass
                        i += 1
                    story.append(Spacer(1, 0.2*inch))
                
                # Bullet points
                elif line.startswith(('*', '-', '•')):
                    clean_line = re.sub(r'^[\*\-•]\s*', '', line)
                    clean_line = clean_text_for_pdf(clean_line)
                    if clean_line:
                        try:
                            story.append(Paragraph(f"• {clean_line}", bullet_style))
                        except:
                            escaped = clean_line.replace('<', '&lt;').replace('>', '&gt;')
                            story.append(Paragraph(f"• {escaped}", bullet_style))
                
                # Regular paragraphs
                else:
                    clean_line = clean_text_for_pdf(line)
                    if clean_line and len(clean_line) > 3:
                        try:
                            story.append(Paragraph(clean_line, body_style))
                            story.append(Spacer(1, 0.1*inch))
                        except:
                            try:
                                escaped = clean_line.replace('<', '&lt;').replace('>', '&gt;')
                                story.append(Paragraph(escaped, body_style))
                            except:
                                pass
                
                i += 1
            
            # Handle images
            if uploaded_images:
                fig_refs = re.findall(r'\[\[FIGURE\s+(\d+):', raw_content, re.IGNORECASE)
                for fig_num_str in fig_refs:
                    fig_num = int(fig_num_str)
                    if fig_num in uploaded_images:
                        try:
                            img = Image(uploaded_images[fig_num], width=4*inch, height=3*inch)
                            story.append(Spacer(1, 0.2*inch))
                            story.append(img)
                            story.append(Paragraph(f"Figure {fig_num}", styles['Caption']))
                            story.append(Spacer(1, 0.2*inch))
                        except:
                            pass
            
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
    
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ PDF generation error: {str(e)}")
        return None

def generate_section_content(section_info, course_context):
    """Generate content for a single section"""
    system_prompt = f"""You are an expert academic writer creating content for {course_context['target_audience']} level education.

Write ONLY for this specific section: {section_info['section_number']} {section_info['section_title']}

REQUIREMENTS:
- Write 600-800 words of high-quality academic content
- Use clear, professional language appropriate for {course_context['target_audience']}
- Include relevant examples and explanations
- Use bullet points (*) for lists
- Add a "CHECK YOUR PROGRESS" section at the end with 3-4 review questions

FORMAT EXACTLY LIKE THIS:
[Your content here with paragraphs]

* Bullet point one
* Bullet point two

--- CHECK YOUR PROGRESS ---
1. Question about key concept?
2. Another important question?
3. Application question?
---

DO NOT write content for other sections. Focus ONLY on {section_info['section_title']}."""

    user_prompt = f"""Write complete academic content for:

**Section Number:** {section_info['section_number']}
**Section Title:** {section_info['section_title']}
**Unit:** {section_info['unit_title']}
**Topics to Cover:** {section_info['description']}
**Course:** {course_context['course_title']}
**Audience:** {course_context['target_audience']}

Write comprehensive, well-structured content for THIS SECTION ONLY.
Include definitions, explanations, examples, and practical applications.
Make it engaging and educational."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return make_api_call(messages, max_tokens=2500, retries=3)

def create_comprehensive_outline(num_units=4, sections_per_unit=8):
    """Create a comprehensive default outline"""
    outline = []
    
    base_topics = [
        {
            "title": "Introduction and Foundations",
            "sections": [
                ("Introduction", "Overview of organisational behaviour"),
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

def show_navigation():
    """Show navigation breadcrumb"""
    steps = {
        'configuration': '1️⃣ Configuration',
        'outline_generation': '2️⃣ Outline',
        'content_generation': '3️⃣ Content',
        'compilation': '4️⃣ PDF'
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
        else:
            st.warning("⚠️ API key should start with 'xai-'")
    
    with col2:
        if st.button("🧪 Test API", use_container_width=True, key="test_api_btn"):
            with st.expander("API Test Results", expanded=True):
                st.info("Testing API connection...")
                resp = make_api_call([{"role": "user", "content": "Say 'API test successful' in 5 words or less"}], max_tokens=50)
                if resp:
                    st.success(f"✅ API Working! Response: {resp[:100]}")
                else:
                    st.error("❌ API Test Failed - Check logs above")
    
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
    
    col1, col2 = st.columns(2)
    with col1:
        num_units = st.number_input(
            "Number of Units",
            min_value=1,
            max_value=10,
            value=st.session_state.num_units,
            key="num_units_input"
        )
        st.session_state.num_units = num_units
    
    with col2:
        sections_per_unit = st.number_input(
            "Sections per Unit",
            min_value=3,
            max_value=15,
            value=st.session_state.sections_per_unit,
            key="sections_per_unit_input"
        )
        st.session_state.sections_per_unit = sections_per_unit
    
    st.info(f"📊 Total sections to generate: {num_units * sections_per_unit}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Generate Course Outline", type="primary", use_container_width=True, key="gen_outline_btn"):
            if st.session_state.api_key:
                # Clear old data
                if 'outline' in st.session_state:
                    del st.session_state.outline
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
        num_units = st.session_state.get('num_units', 4)
        sections_per_unit = st.session_state.get('sections_per_unit', 8)
        
        with st.spinner("🤖 Generating course outline with AI..."):
            st.info(f"Requesting {num_units} units with {sections_per_unit} sections each...")
            
            system_prompt = """You are an expert curriculum designer. Create a comprehensive JSON course outline.

CRITICAL: Create EXACTLY the number of units and sections requested.

OUTPUT FORMAT (JSON only, no other text):
[
  {
    "unit_number": 1,
    "unit_title": "Descriptive Title",
    "sections": [
      {
        "section_number": "1.1",
        "section_title": "Section Title",
        "description": "What this covers"
      }
    ]
  }
]

Make titles specific, relevant, and academic."""

            user_prompt = f"""Create a course outline for:

Course: {st.session_state.course_title}
Audience: {st.session_state.target_audience}
Objectives: {st.session_state.learning_objectives}

REQUIREMENTS:
- Create EXACTLY {num_units} units
- Each unit must have EXACTLY {sections_per_unit} sections
- Section numbers: 1.1-1.{sections_per_unit}, 2.1-2.{sections_per_unit}, etc.
- Total sections: {num_units * sections_per_unit}

Return ONLY the JSON array. Be comprehensive and academic."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            with st.expander("🔍 API Call Details", expanded=False):
                outline_str = make_api_call(messages, max_tokens=4000, retries=3)
            
            if outline_str:
                try:
                    # Extract JSON
                    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', outline_str, re.DOTALL)
                    if json_match:
                        outline_str = json_match.group(1)
                    
                    parsed_outline = json.loads(outline_str.strip())
                    
                    if isinstance(parsed_outline, list) and len(parsed_outline) > 0:
                        st.session_state.outline = parsed_outline
                        actual_units = len(parsed_outline)
                        actual_sections = sum(len(u.get('sections', [])) for u in parsed_outline)
                        
                        if actual_units < num_units or actual_sections < (num_units * sections_per_unit * 0.8):
                            st.warning(f"⚠️ Generated {actual_units} units with {actual_sections} sections (requested {num_units} units with {num_units * sections_per_unit} sections)")
                            st.info("You can edit and add more in the table below")
                        else:
                            st.success(f"✅ Generated {actual_units} units with {actual_sections} sections!")
                    else:
                        st.error("❌ Invalid outline format. Using default structure.")
                        st.session_state.outline = create_comprehensive_outline(num_units, sections_per_unit)
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Failed to parse JSON: {str(e)}")
                    st.warning("Using comprehensive default outline...")
                    st.session_state.outline = create_comprehensive_outline(num_units, sections_per_unit)
            else:
                st.error("❌ API call returned no data. Using default outline.")
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
        
        st.subheader("✏️ Edit Outline")
        st.caption("Click any cell to edit. Use + button to add rows.")
        
        edited = st.data_editor(
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
            key="outline_editor"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Back", use_container_width=True, key="back_to_config_btn"):
                st.session_state.step = "configuration"
                st.rerun()
        
        with col2:
            if st.button("✅ Approve & Start Generation", type="primary", use_container_width=True, key="approve_outline_btn"):
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
                    current
