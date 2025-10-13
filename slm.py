"""
AI CURRICULUM GENERATOR - COMPLETE VERSION WITH FORMULAS & IMAGES
=================================================================
Full-featured with LaTeX formula support and image handling
"""

import streamlit as st
import requests
import json
import time
import os
import re
from datetime import datetime
from io import BytesIO
from PIL import Image as PILImage

# Try importing reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
        Table, TableStyle, Image as RLImage, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
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
                st.write(f"🔄 API Attempt {attempt + 1}/{retries} with {model}...")
                
                response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
                st.write(f"📡 Status: {response.status_code}")
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    st.write(f"✅ Success! Length: {len(content)} chars")
                    return content
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ HTTP {e.response.status_code}")
                if e.response.status_code == 404:
                    break
                elif e.response.status_code == 401:
                    st.error("❌ Invalid API Key")
                    return None
                if attempt < retries - 1:
                    time.sleep(delay)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
    
    st.error("❌ All attempts failed")
    return None

def clean_text_for_pdf(text):
    """Remove markdown formatting but preserve formulas"""
    if not text:
        return ""
    
    # Protect formulas first (anything between $ signs)
    formula_pattern = r'\$([^\$]+)\$'
    formulas = re.findall(formula_pattern, text)
    formula_placeholders = {}
    
    for i, formula in enumerate(formulas):
        placeholder = f"___FORMULA_{i}___"
        formula_placeholders[placeholder] = formula
        text = text.replace(f"${formula}$", placeholder)
    
    # Remove markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)  # Italic
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # Headers
    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)  # HR
    
    # Restore formulas
    for placeholder, formula in formula_placeholders.items():
        text = text.replace(placeholder, f'<i>[{formula}]</i>')
    
    return text

def process_uploaded_image(uploaded_file, max_width=4*inch, max_height=3*inch):
    """Process and resize uploaded image"""
    try:
        image = PILImage.open(uploaded_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Calculate aspect ratio
        aspect = image.width / image.height
        
        if aspect > max_width / max_height:
            # Width is limiting factor
            new_width = max_width
            new_height = max_width / aspect
        else:
            # Height is limiting factor
            new_height = max_height
            new_width = max_height * aspect
        
        # Resize
        image = image.resize((int(new_width * 72 / inch), int(new_height * 72 / inch)), PILImage.LANCZOS)
        
        # Save to BytesIO
        img_buffer = BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer, new_width, new_height
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None, None

def compile_pdf_reportlab(course_title, content_dict, outline, target_audience="Postgraduate", uploaded_images=None):
    """Generate PDF with formula and image support"""
    
    if not REPORTLAB_AVAILABLE:
        st.error("❌ PDF library not available")
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
    
    formula_style = ParagraphStyle(
        'FormulaStyle',
        parent=body_style,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#000080'),
        fontName='Courier',
        fontSize=10,
        backColor=colors.lightgrey,
        borderPadding=5
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
            
            # Process content line by line
            lines = raw_content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # Check for formulas (lines with $ signs)
                if '$' in line and line.count('$') >= 2:
                    # Extract formula
                    formula_match = re.search(r'\$([^\$]+)\$', line)
                    if formula_match:
                        formula = formula_match.group(1)
                        before_formula = line[:formula_match.start()]
                        after_formula = line[formula_match.end():]
                        
                        # Add text before formula
                        if before_formula.strip():
                            story.append(Paragraph(clean_text_for_pdf(before_formula), body_style))
                        
                        # Add formula in styled box
                        try:
                            story.append(Spacer(1, 0.1*inch))
                            formula_para = Paragraph(f"<i>{formula}</i>", formula_style)
                            story.append(formula_para)
                            story.append(Spacer(1, 0.1*inch))
                        except:
                            # Fallback
                            story.append(Paragraph(f"[Formula: {formula}]", body_style))
                        
                        # Add text after formula
                        if after_formula.strip():
                            story.append(Paragraph(clean_text_for_pdf(after_formula), body_style))
                        
                        i += 1
                        continue
                
                # Check for figure references
                fig_match = re.search(r'\[\[FIGURE\s+(\d+):\s*(.*?)\]\]', line, re.IGNORECASE)
                if fig_match:
                    fig_num = int(fig_match.group(1))
                    fig_caption = fig_match.group(2)
                    
                    # Check if image was uploaded
                    if uploaded_images and fig_num in uploaded_images:
                        try:
                            img_buffer, width, height = process_uploaded_image(uploaded_images[fig_num])
                            if img_buffer:
                                story.append(Spacer(1, 0.2*inch))
                                img = RLImage(img_buffer, width=width, height=height)
                                story.append(img)
                                story.append(Paragraph(f"<b>Figure {fig_num}:</b> {fig_caption}", styles['Caption']))
                                story.append(Spacer(1, 0.2*inch))
                            else:
                                # Placeholder if processing failed
                                story.append(Paragraph(f"[Figure {fig_num}: {fig_caption}]", body_style))
                        except Exception as e:
                            st.warning(f"Could not insert Figure {fig_num}: {str(e)}")
                            story.append(Paragraph(f"[Figure {fig_num}: {fig_caption}]", body_style))
                    else:
                        # No image uploaded - show placeholder
                        story.append(Spacer(1, 0.1*inch))
                        fig_table = Table([[Paragraph(f"[Figure {fig_num}: {fig_caption}]", body_style)]], 
                                        colWidths=[6*inch])
                        fig_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                            ('BORDER', (0, 0), (-1, -1), 1, colors.grey),
                            ('PADDING', (0, 0), (-1, -1), 10),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ]))
                        story.append(fig_table)
                        story.append(Spacer(1, 0.1*inch))
                    
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
                    continue
                
                # Bullet points
                if line.startswith(('*', '-', '•')):
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
            
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
    
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ PDF generation error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

def generate_section_content(section_info, course_context):
    """Generate content for a single section"""
    system_prompt = f"""You are an expert academic writer creating content for {course_context['target_audience']} level education.

Write ONLY for this specific section: {section_info['section_number']} {section_info['section_title']}

REQUIREMENTS:
- Write 600-800 words of high-quality academic content
- Use clear, professional language
- Include relevant examples and explanations
- Use bullet points (*) for lists
- For mathematical formulas, use: $formula$ (e.g., $E = mc^2$)
- For figures/diagrams, use: [[FIGURE 1: Description of the figure]]
- Add "CHECK YOUR PROGRESS" section at the end with 3-4 questions

FORMAT EXAMPLE:
[Content with paragraphs]

The famous equation $E = mc^2$ shows the relationship...

* Point one
* Point two

[[FIGURE 1: Diagram showing the organizational structure]]

--- CHECK YOUR PROGRESS ---
1. What is...?
2. Explain...?
---

Focus ONLY on {section_info['section_title']}."""

    user_prompt = f"""Write complete academic content for:

**Section:** {section_info['section_number']} {section_info['section_title']}
**Unit:** {section_info['unit_title']}
**Topics:** {section_info['description']}
**Course:** {course_context['course_title']}
**Audience:** {course_context['target_audience']}

Write comprehensive, well-structured content for THIS SECTION ONLY.
Include formulas where relevant using $formula$ syntax.
Include figure placeholders where diagrams would help: [[FIGURE X: description]]"""

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

# Continue with the rest of the functions (show_outline_page, show_content_generation_page, etc.)
# I'll provide them in the next message due to length...def show_outline_page():
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
                    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', outline_str, re.DOTALL)
                    if json_match:
                        outline_str = json_match.group(1)
                    
                    parsed_outline = json.loads(outline_str.strip())
                    
                    if isinstance(parsed_outline, list) and len(parsed_outline) > 0:
                        st.session_state.outline = parsed_outline
                        actual_units = len(parsed_outline)
                        actual_sections = sum(len(u.get('sections', [])) for u in parsed_outline)
                        
                        if actual_units < num_units or actual_sections < (num_units * sections_per_unit * 0.8):
                            st.warning(f"⚠️ Generated {actual_units} units with {actual_sections} sections")
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
                if st.button("➡️ Continue", use_container_width=True, key="continue_content_btn"):
                    st.session_state.step = "content_generation"
                    st.rerun()

def show_content_generation_page():
    st.header("✍️ Step 3: AI Content Generation")
    
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
        
        st.info(f"🤖 Now Generating: **{section_key}**")
        st.caption(f"Unit {current['unit_number']}: {current['unit_title']}")
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Topics:** {current['description']}")
            with col2:
                if st.button("⏸️ Pause", use_container_width=True, key="pause_gen_btn"):
                    st.session_state.paused = True
                    st.rerun()
        
        if not st.session_state.get('paused', False):
            with st.spinner(f"✍️ Writing section {completed + 1} of {total}... (30-90 seconds)"):
                course_context = {
                    'course_title': st.session_state.course_title,
                    'target_audience': st.session_state.target_audience
                }
                
                with st.expander("🔍 Generation Details", expanded=True):
                    content = generate_section_content(current, course_context)
                
                if content and len(content.strip()) > 100:
                    st.session_state.content[section_key] = content
                    st.success(f"✅ Completed: {section_key}")
                    
                    with st.expander("📄 Generated Content Preview", expanded=False):
                        st.markdown(content[:500] + "...")
                        st.caption(f"📊 {len(content.split())} words")
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to generate content for: {section_key}")
                    st.session_state.failed_sections.append(section_key)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔄 Retry", use_container_width=True, key="retry_gen_btn"):
                            st.rerun()
                    with col2:
                        if st.button("✏️ Write Manually", use_container_width=True, key="manual_gen_btn"):
                            manual_content = st.text_area(
                                "Write content manually:",
                                height=300,
                                key="manual_content_input"
                            )
                            if st.button("💾 Save", key="save_manual_btn"):
                                if manual_content.strip():
                                    st.session_state.content[section_key] = manual_content
                                    st.success("Saved!")
                                    time.sleep(1)
                                    st.rerun()
                    with col3:
                        if st.button("⏭️ Skip", use_container_width=True, key="skip_gen_btn"):
                            st.session_state.content[section_key] = f"[Content for {section_key} - To be added manually]\n\nPlease add content for this section."
                            st.rerun()
        else:
            st.warning("⏸️ Generation Paused")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Resume", type="primary", use_container_width=True, key="resume_gen_btn"):
                    st.session_state.paused = False
                    st.rerun()
            with col2:
                if st.button("⏭️ Skip This Section", use_container_width=True, key="skip_paused_btn"):
                    st.session_state.content[section_key] = f"[Skipped: {section_key}]"
                    st.session_state.paused = False
                    st.rerun()
    
    else:
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
        
        if st.session_state.get('failed_sections'):
            st.warning(f"⚠️ {len(st.session_state.failed_sections)} sections had issues")
        
        st.divider()
        
        if st.checkbox("👁️ Preview Content", key="preview_content_check"):
            for unit in st.session_state.approved_outline:
                with st.expander(f"📚 Unit {unit['unit_number']}: {unit['unit_title']}", expanded=False):
                    for section in unit.get('sections', []):
                        sec_key = f"{section['section_number']} {section['section_title']}"
                        if sec_key in st.session_state.content:
                            st.markdown(f"### {sec_key}")
                            content = st.session_state.content[sec_key]
                            st.markdown(content[:400] + "...")
                            st.caption(f"📊 {len(content.split())} words")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("← Back to Outline", use_container_width=True, key="back_outline_content_btn"):
                st.session_state.step = "outline_generation"
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate All", use_container_width=True, key="regen_all_btn"):
                if st.checkbox("⚠️ Delete all and start over?", key="regen_confirm"):
                    del st.session_state.content
                    del st.session_state.sections_to_process
                    st.rerun()
        
        with col3:
            if st.button("📄 Compile PDF", type="primary", use_container_width=True, key="compile_pdf_btn"):
                st.session_state.step = "compilation"
                st.rerun()

def show_compilation_page():
    st.header("📄 Step 4: Compile PDF Document")
    
    if 'content' not in st.session_state or not st.session_state.content:
        st.error("❌ No content found")
        if st.button("← Back to Content", use_container_width=True, key="back_content_comp_err_btn"):
            st.session_state.step = "content_generation"
            st.rerun()
        return
    
    if 'approved_outline' not in st.session_state:
        st.error("❌ No outline found")
        if st.button("← Back to Outline", use_container_width=True, key="back_outline_comp_err_btn"):
            st.session_state.step = "outline_generation"
            st.rerun()
        return
    
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
        st.metric("📖 Pages", f"~{estimated_pages:.0f}")
    
    st.divider()
    
    if not REPORTLAB_AVAILABLE:
        st.error("❌ PDF library not installed")
        st.code("pip install reportlab pillow")
        st.stop()
    
    # Check for figures
    fig_nums = set()
    fig_descs = {}
    for content in st.session_state.content.values():
        figs = re.findall(r'\[\[FIGURE\s+(\d+):\s*(.*?)\]\]', content, re.IGNORECASE)
        for num, desc in figs:
            num = int(num)
            fig_nums.add(num)
            if num not in fig_descs:
                fig_descs[num] = desc
    
    # Check for formulas
    formula_count = 0
    for content in st.session_state.content.values():
        formula_count += len(re.findall(r'\$[^\$]+\$', content))
    
    if formula_count > 0:
        st.info(f"📐 {formula_count} mathematical formulas detected and will be formatted")
    
    # Image upload
    if fig_nums:
        st.subheader("🖼️ Upload Images")
        st.info(f"📸 {len(fig_nums)} figure references detected in your content")
        
        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = {}
        
        with st.expander("📤 Upload Images for Figures", expanded=True):
            st.caption("💡 Upload images to replace figure placeholders in your PDF")
            
            cols = st.columns(2)
            for idx, num in enumerate(sorted(fig_nums)):
                desc = fig_descs.get(num, "")
                with cols[idx % 2]:
                    st.markdown(f"**Figure {num}**")
                    st.caption(desc[:80] + "..." if len(desc) > 80 else desc)
                    
                    uploaded = st.file_uploader(
                        f"Upload image for Figure {num}",
                        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                        key=f"fig_upload_{num}",
                        label_visibility="collapsed"
                    )
                    
                    if uploaded:
                        st.session_state.uploaded_images[num] = uploaded
                        # Show preview
                        image = PILImage.open(uploaded)
                        st.image(image, width=200, caption=f"✅ Figure {num} uploaded")
                    else:
                        if num in st.session_state.uploaded_images:
                            del st.session_state.uploaded_images[num]
            
            uploaded_count = len(st.session_state.uploaded_images)
            if uploaded_count > 0:
                st.success(f"✅ {uploaded_count} of {len(fig_nums)} images uploaded")
            else:
                st.warning("⚠️ No images uploaded - placeholders will be shown in PDF")
        
        st.divider()
    
    # Compilation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back", use_container_width=True, key="back_content_comp_btn"):
            st.session_state.step = "content_generation"
            st.rerun()
    
    with col2:
        if st.button("📝 Edit", use_container_width=True, key="edit_content_comp_btn"):
            st.session_state.show_editor = True
            st.rerun()
    
    with col3:
        compile_button = st.button("🔨 Compile PDF", type="primary", use_container_width=True, key="compile_now_btn")
    
    # Editor
    if st.session_state.get('show_editor', False):
        st.divider()
        st.subheader("✏️ Content Editor")
        st.caption("Edit any section before compiling. Formulas use $formula$ syntax, figures use [[FIGURE X: description]]")
        
        for unit_idx, unit in enumerate(st.session_state.approved_outline):
            with st.expander(f"UNIT {unit['unit_number']}: {unit['unit_title']}", key=f"unit_exp_{unit_idx}"):
                for sec_idx, section in enumerate(unit.get('sections', [])):
                    sec_key = f"{section['section_number']} {section['section_title']}"
                    if sec_key in st.session_state.content:
                        st.markdown(f"**{sec_key}**")
                        edited = st.text_area(
                            "Content:",
                            value=st.session_state.content[sec_key],
                            height=250,
                            key=f"edit_{unit_idx}_{sec_idx}"
                        )
                        if st.button(f"💾 Save", key=f"save_{unit_idx}_{sec_idx}"):
                            st.session_state.content[sec_key] = edited
                            st.success(f"✅ Saved: {sec_key}")
        
        if st.button("✅ Done Editing", key="done_editing_btn"):
            st.session_state.show_editor = False
            st.rerun()
        
        st.divider()
    
    # Compile
    if compile_button:
        with st.spinner("🔨 Compiling PDF with formulas and images... (30-60 seconds)"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("📄 Preparing document structure...")
            progress_bar.progress(20)
            
            status_text.text("✍️ Processing content and formulas...")
            progress_bar.progress(40)
            
            status_text.text("🖼️ Inserting images...")
            progress_bar.progress(60)
            
            pdf_buffer = compile_pdf_reportlab(
                st.session_state.course_title,
                st.session_state.content,
                st.session_state.approved_outline,
                st.session_state.target_audience,
                st.session_state.get('uploaded_images', {})
            )
            
            progress_bar.progress(80)
            status_text.text("📦 Finalizing PDF...")
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
        
        if pdf_buffer:
            st.success("✅ PDF Compiled Successfully!")
            
            pdf_bytes = pdf_buffer.getvalue()
            
            st.divider()
            st.subheader("📥 Download Your PDF")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                filename = f"{st.session_state.course_title.replace(' ', '_')[:50]}.pdf"
                st.download_button(
                    label="📥 Download PDF Document",
                    data=pdf_bytes,
                    file_name=filename,
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
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"📊 Size: {len(pdf_bytes)/1024:.1f} KB")
            with col2:
                st.info(f"📖 Pages: ~{estimated_pages:.0f}")
            with col3:
                if fig_nums:
                    uploaded = len(st.session_state.get('uploaded_images', {}))
                    st.info(f"🖼️ Images: {uploaded}/{len(fig_nums)}")
            with col4:
                if formula_count > 0:
                    st.info(f"📐 Formulas: {formula_count}")
            
            st.success("🎉 Your academic curriculum is ready!")
            
        else:
            st.error("❌ PDF compilation failed")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Again", use_container_width=True, key="try_again_btn"):
                    st.rerun()
            with col2:
                if st.button("← Back", use_container_width=True, key="back_fail_btn"):
                    st.session_state.step = "content_generation"
                    st.rerun()

def main():
    st.set_page_config(
        page_title="AI Curriculum Generator",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown("""
    <style>
    .stButton button {
        border-radius: 5px;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🎓 AI Curriculum Generator")
    st.caption("Generate professional academic course materials with formulas and images")
    
    initialize_session_state()
    show_navigation()
    
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
        st.error("❌ Unknown step")
        st.session_state.step = "configuration"
        st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Project Status")
        
        if 'course_title' in st.session_state:
            st.markdown(f"**Course:** {st.session_state.course_title[:40]}...")
        
        if 'approved_outline' in st.session_state:
            units = len(st.session_state.approved_outline)
            sections = sum(len(u.get('sections', [])) for u in st.session_state.approved_outline)
            st.metric("Units", units)
            st.metric("Sections", sections)
        
        if 'content' in st.session_state:
            completed = len(st.session_state.content)
            st.metric("Generated", completed)
            
            if 'sections_to_process' in st.session_state:
                total = len(st.session_state.sections_to_process)
                progress = (completed / total * 100) if total > 0 else 0
                st.progress(progress / 100)
                st.caption(f"{progress:.0f}% Complete")
        
        st.divider()
        st.subheader("⚡ Features")
        st.caption("✅ AI Content Generation")
        st.caption("✅ Mathematical Formulas")
        st.caption("✅ Image Upload")
        st.caption("✅ Professional PDF")
        
        st.divider()
        
        if st.button("🏠 Start Over", use_container_width=True, key="sidebar_start_over"):
            if st.checkbox("⚠️ Clear all?", key="sidebar_reset"):
                api_key = st.session_state.get('api_key')
                custom_model = st.session_state.get('custom_model')
                st.session_state.clear()
                st.session_state.api_key = api_key
                st.session_state.custom_model = custom_model
                st.session_state.step = "configuration"
                st.rerun()
        
        if 'content' in st.session_state and st.session_state.content:
            if st.button("💾 Backup", use_container_width=True, key="sidebar_save"):
                backup = {
                    'course_title': st.session_state.course_title,
                    'target_audience': st.session_state.target_audience,
                    'outline': st.session_state.get('approved_outline', []),
                    'content': st.session_state.content,
                    'timestamp': datetime.now().isoformat()
                }
                
                json_str = json.dumps(backup, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"curriculum_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_backup_btn"
                )
        
        st.divider()
        st.caption("💡 Progress auto-saved")
        st.caption("⚠️ Don't refresh page")
        st.caption(f"✅ PDF: {'Ready' if REPORTLAB_AVAILABLE else 'Missing'}")

if __name__== "__main__":
    main()
