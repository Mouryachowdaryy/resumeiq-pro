from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import pdfplumber
from docx import Document
import json
import os
import re
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
import traceback

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load skill taxonomy
with open('skills.json', 'r') as f:
    SKILLS_TAXONOMY = json.load(f)

# Initialize Groq LLM
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=groq_api_key
)

# ============================================================================
# RESUME PARSING FUNCTIONS
# ============================================================================

def parse_pdf(file_path):
    """Extract text from PDF using pdfplumber"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF parsing error: {e}")
        return ""

def parse_docx(file_path):
    """Extract text from DOCX"""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"DOCX parsing error: {e}")
        return ""

def extract_contact_info(text):
    """Extract contact information from resume text"""
    contact = {}
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    contact['email'] = emails[0] if emails else ""
    
    # Extract phone
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, text)
    contact['phone'] = phones[0] if phones else ""
    
    # Extract LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    contact['linkedin'] = linkedin[0] if linkedin else ""
    
    # Extract GitHub
    github_pattern = r'github\.com/[\w-]+'
    github = re.findall(github_pattern, text, re.IGNORECASE)
    contact['github'] = github[0] if github else ""
    
    # Extract name (first line typically)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    contact['name'] = lines[0] if lines else "Candidate"
    
    return contact

def extract_skills_from_text(text, skills_db):
    """Extract skills mentioned in resume text"""
    text_lower = text.lower()
    found_skills = {}
    
    for category, skills_list in skills_db.items():
        found_skills[category] = []
        for skill in skills_list:
            # Check for exact match and variations
            skill_lower = skill.lower()
            if skill_lower in text_lower:
                found_skills[category].append(skill)
    
    return found_skills

def parse_resume(file_path):
    """Main resume parsing function"""
    # Determine file type and parse
    if file_path.endswith('.pdf'):
        text = parse_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = parse_docx(file_path)
    else:
        text = ""
    
    # Extract structured information
    contact = extract_contact_info(text)
    skills = extract_skills_from_text(text, SKILLS_TAXONOMY)
    
    return {
        'contact': contact,
        'raw_text': text,
        'skills': skills,
        'text_length': len(text)
    }

# ============================================================================
# JOB DESCRIPTION PARSING
# ============================================================================

def parse_job_description(file_path=None, text=None):
    """Parse job description from file or text"""
    if file_path:
        if file_path.endswith('.pdf'):
            jd_text = parse_pdf(file_path)
        elif file_path.endswith('.docx'):
            jd_text = parse_docx(file_path)
        else:
            with open(file_path, 'r') as f:
                jd_text = f.read()
    else:
        jd_text = text or ""
    
    # Extract required skills from JD
    jd_skills = extract_skills_from_text(jd_text, SKILLS_TAXONOMY)
    
    # Extract job title (simple heuristic)
    lines = [line.strip() for line in jd_text.split('\n') if line.strip()]
    job_title = lines[0] if lines else "Position"
    
    return {
        'text': jd_text,
        'skills': jd_skills,
        'title': job_title
    }

# ============================================================================
# ATS SKILL MATCHING ENGINE
# ============================================================================

def calculate_skill_match(resume_skills, jd_skills):
    """Calculate detailed skill matching between resume and JD"""
    
    results = {
        'matched': {},
        'missing': {},
        'partial': {},
        'category_scores': {},
        'overall_score': 0
    }
    
    total_points = 0
    earned_points = 0
    
    for category in SKILLS_TAXONOMY.keys():
        resume_cat_skills = set(resume_skills.get(category, []))
        jd_cat_skills = set(jd_skills.get(category, []))
        
        if not jd_cat_skills:
            continue
        
        # Calculate matches
        matched = resume_cat_skills & jd_cat_skills
        missing = jd_cat_skills - resume_cat_skills
        
        # Scoring
        category_total = len(jd_cat_skills) * 10
        category_earned = len(matched) * 10
        
        total_points += category_total
        earned_points += category_earned
        
        results['matched'][category] = list(matched)
        results['missing'][category] = list(missing)
        
        # Category score percentage
        cat_score = (category_earned / category_total * 100) if category_total > 0 else 0
        results['category_scores'][category] = round(cat_score, 1)
    
    # Calculate overall ATS score
    results['overall_score'] = round((earned_points / total_points * 100) if total_points > 0 else 0, 1)
    
    # Flatten matched and missing for easier display
    results['matched_flat'] = []
    results['missing_flat'] = []
    
    for cat, skills in results['matched'].items():
        for skill in skills:
            results['matched_flat'].append({'skill': skill, 'category': cat, 'confidence': 100})
    
    for cat, skills in results['missing'].items():
        for skill in skills:
            priority = 'High' if cat in ['Technical Skills', 'Tools & Platforms'] else 'Medium'
            results['missing_flat'].append({'skill': skill, 'category': cat, 'priority': priority})
    
    return results

# ============================================================================
# AI SEMANTIC ANALYSIS
# ============================================================================

def analyze_with_ai(resume_data, jd_data, match_results):
    """Perform semantic analysis using Groq LLM"""
    
    # Prepare context
    matched_skills_text = ", ".join([s['skill'] for s in match_results['matched_flat'][:15]])
    missing_skills_text = ", ".join([s['skill'] for s in match_results['missing_flat'][:15]])
    
    prompt_template = PromptTemplate(
        input_variables=["resume", "job_description", "ats_score", "matched_skills", "missing_skills"],
        template="""You are an expert HR recruiter and career strategist analyzing a candidate's fit for a role.

JOB DESCRIPTION:
{job_description}

RESUME SUMMARY:
{resume}

ATS ANALYSIS:
- Overall ATS Score: {ats_score}/100
- Matched Skills: {matched_skills}
- Missing Skills: {missing_skills}

PROVIDE COMPREHENSIVE EVALUATION IN JSON FORMAT:

{{
  "overall_fit": "2-3 sentence assessment of candidate fit",
  "strengths": [
    "Strength 1 with specific evidence",
    "Strength 2 with specific evidence",
    "Strength 3 with specific evidence",
    "Strength 4 with specific evidence",
    "Strength 5 with specific evidence"
  ],
  "weaknesses": [
    "Weakness 1 with priority",
    "Weakness 2 with priority",
    "Weakness 3 with priority",
    "Weakness 4 with priority",
    "Weakness 5 with priority"
  ],
  "red_flags": "Any concerns or empty string if none",
  "recommendation": "Strong Fit, Moderate Fit, or Weak Fit",
  "confidence": "High, Medium, or Low",
  "learning_plan_30": "Specific 30-day action items",
  "learning_plan_60": "Specific 60-day goals",
  "learning_plan_90": "Specific 90-day mastery plan",
  "resume_tips": "Specific optimization suggestions"
}}

Return ONLY valid JSON, no other text."""
    )
    
    try:
        # Prepare inputs
        resume_summary = resume_data['raw_text'][:2000]  # Limit length
        jd_summary = jd_data['text'][:2000]
        
        formatted_prompt = prompt_template.format(
            resume=resume_summary,
            job_description=jd_summary,
            ats_score=match_results['overall_score'],
            matched_skills=matched_skills_text,
            missing_skills=missing_skills_text
        )
        
        # Get AI response
        response = llm.invoke(formatted_prompt)
        response_text = response.content
        
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            ai_analysis = json.loads(json_match.group())
        else:
            # Fallback if JSON parsing fails
            ai_analysis = {
                "overall_fit": "Unable to generate detailed analysis. Please review ATS scores.",
                "strengths": ["Strong technical foundation", "Relevant experience", "Good educational background"],
                "weaknesses": ["Some skill gaps identified", "Additional certifications recommended"],
                "red_flags": "",
                "recommendation": "Moderate Fit",
                "confidence": "Medium",
                "learning_plan_30": "Focus on missing critical skills",
                "learning_plan_60": "Build portfolio projects",
                "learning_plan_90": "Gain advanced certifications",
                "resume_tips": "Optimize keywords for ATS"
            }
        
        # Calculate role-fit score (0-5 stars)
        if ai_analysis['recommendation'] == 'Strong Fit':
            role_fit_score = 4.5
        elif ai_analysis['recommendation'] == 'Moderate Fit':
            role_fit_score = 3.5
        else:
            role_fit_score = 2.0
        
        ai_analysis['role_fit_score'] = role_fit_score
        
        return ai_analysis
        
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        traceback.print_exc()
        # Return fallback analysis
        return {
            "overall_fit": "Analysis completed. Review detailed scores below.",
            "strengths": ["Technical skills present", "Relevant experience", "Educational background"],
            "weaknesses": ["Some gaps in required skills", "Additional training recommended"],
            "red_flags": "",
            "recommendation": "Moderate Fit",
            "confidence": "Medium",
            "role_fit_score": 3.0,
            "learning_plan_30": "Focus on top priority skills from missing list",
            "learning_plan_60": "Complete relevant certifications",
            "learning_plan_90": "Build real-world project portfolio",
            "resume_tips": "Add more quantifiable achievements and keywords"
        }

# ============================================================================
# CHATBOT ENGINE
# ============================================================================

def initialize_chatbot(analysis_context):
    """Initialize chatbot with full analysis context"""
    
    context_prompt = f"""You are ResumeIQ Pro's AI Career Coach. You just analyzed a resume.

ANALYSIS CONTEXT:

Candidate: {analysis_context['candidate_name']}
Target Role: {analysis_context['job_title']}
ATS Score: {analysis_context['ats_score']}/100
Role-Fit Score: {analysis_context['role_fit_score']}/5.0

MATCHED SKILLS ({len(analysis_context['matched_skills'])}):
{', '.join(analysis_context['matched_skills'][:20])}

MISSING SKILLS ({len(analysis_context['missing_skills'])}):
{', '.join(analysis_context['missing_skills'][:20])}

TOP STRENGTHS:
{chr(10).join(analysis_context['strengths'][:3])}

KEY GAPS:
{chr(10).join(analysis_context['weaknesses'][:3])}

YOUR ROLE:
- Answer questions about THIS specific analysis
- Cite specific evidence from resume or analysis
- Keep responses 50-150 words
- Be professional, honest, actionable
- No hallucinations - only reference provided data

Ready to help. Answer user questions about their resume analysis."""

    memory = ConversationBufferMemory()
    
    chatbot_chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )
    
    # Store context in memory
    memory.save_context(
        {"input": "System initialization"},
        {"output": context_prompt}
    )
    
    return chatbot_chain

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page with upload interface"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        # Get uploaded files
        resume_file = request.files.get('resume')
        jd_file = request.files.get('jd_file')
        jd_text = request.form.get('jd_text', '')
        
        if not resume_file:
            return jsonify({'error': 'No resume uploaded'}), 400
        
        # Save resume file
        resume_filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)
        
        # Parse resume
        resume_data = parse_resume(resume_path)
        
        # Parse job description
        if jd_file:
            jd_filename = secure_filename(jd_file.filename)
            jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_filename)
            jd_file.save(jd_path)
            jd_data = parse_job_description(file_path=jd_path)
        else:
            jd_data = parse_job_description(text=jd_text)
        
        # Perform ATS matching
        match_results = calculate_skill_match(resume_data['skills'], jd_data['skills'])
        
        # Perform AI analysis
        ai_analysis = analyze_with_ai(resume_data, jd_data, match_results)
        
        # Prepare complete analysis for session
        complete_analysis = {
            'candidate_name': resume_data['contact']['name'],
            'candidate_email': resume_data['contact']['email'],
            'candidate_phone': resume_data['contact']['phone'],
            'candidate_linkedin': resume_data['contact']['linkedin'],
            'candidate_github': resume_data['contact']['github'],
            'job_title': jd_data['title'],
            'ats_score': match_results['overall_score'],
            'role_fit_score': ai_analysis['role_fit_score'],
            'category_scores': match_results['category_scores'],
            'matched_skills': [s['skill'] for s in match_results['matched_flat']],
            'missing_skills': [s['skill'] for s in match_results['missing_flat']],
            'matched_skills_detailed': match_results['matched_flat'],
            'missing_skills_detailed': match_results['missing_flat'],
            'ai_analysis': ai_analysis,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store in session for chatbot
        session['analysis'] = complete_analysis
        
        # Clean up uploaded files
        os.remove(resume_path)
        if jd_file:
            os.remove(jd_path)
        
        return jsonify(complete_analysis)
        
    except Exception as e:
        print(f"Analysis Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    """Results page with visualizations"""
    analysis = session.get('analysis')
    if not analysis:
        return redirect(url_for('index'))
    
    return render_template('results.html', analysis=analysis)

@app.route('/chat', methods=['POST'])
def chat():
    """Chatbot endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        analysis = session.get('analysis')
        if not analysis:
            return jsonify({'error': 'No analysis found'}), 400
        
        # Initialize or get chatbot from session
        if 'chatbot_initialized' not in session:
            chatbot_context = {
                'candidate_name': analysis['candidate_name'],
                'job_title': analysis['job_title'],
                'ats_score': analysis['ats_score'],
                'role_fit_score': analysis['role_fit_score'],
                'matched_skills': analysis['matched_skills'][:15],
                'missing_skills': analysis['missing_skills'][:15],
                'strengths': analysis['ai_analysis']['strengths'],
                'weaknesses': analysis['ai_analysis']['weaknesses']
            }
            session['chatbot_initialized'] = True
        
        # Get response from LLM
        chatbot_prompt = f"""Based on the resume analysis context, answer this question:

User Question: {user_message}

Context:
- ATS Score: {analysis['ats_score']}/100
- Role Fit: {analysis['role_fit_score']}/5.0
- Matched Skills: {', '.join(analysis['matched_skills'][:10])}
- Missing Skills: {', '.join(analysis['missing_skills'][:10])}

Provide a helpful, specific answer in 50-150 words. Cite the analysis data."""

        response = llm.invoke(chatbot_prompt)
        bot_message = response.content
        
        return jsonify({'response': bot_message})
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'error': 'Failed to get response'}), 500

@app.route('/batch', methods=['POST'])
def batch_analyze():
    """Batch resume analysis for recruiters"""
    try:
        files = request.files.getlist('resumes')
        jd_text = request.form.get('jd_text', '')
        
        if not files:
            return jsonify({'error': 'No resumes uploaded'}), 400
        
        # Parse JD once
        jd_data = parse_job_description(text=jd_text)
        
        results = []
        
        for file in files:
            try:
                # Save and parse resume
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                resume_data = parse_resume(file_path)
                match_results = calculate_skill_match(resume_data['skills'], jd_data['skills'])
                
                results.append({
                    'name': resume_data['contact']['name'],
                    'email': resume_data['contact']['email'],
                    'ats_score': match_results['overall_score'],
                    'matched_count': len(match_results['matched_flat']),
                    'missing_count': len(match_results['missing_flat']),
                    'top_skills': [s['skill'] for s in match_results['matched_flat'][:3]]
                })
                
                os.remove(file_path)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        
        # Sort by ATS score
        results.sort(key=lambda x: x['ats_score'], reverse=True)
        
        return jsonify({'candidates': results})
        
    except Exception as e:
        print(f"Batch Analysis Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
