#  ResumeIQ Pro  
### AI-Powered Resume Screening & Skill Gap Analyzer

ResumeIQ Pro is a **production-ready, full-stack AI recruitment intelligence platform** that analyzes resumes against job descriptions across **any industry**.  
It combines **ATS-style deterministic logic** with **LLM-powered semantic intelligence** to deliver **clear, explainable, and actionable feedback**.

This is **not a demo or academic project** — it is designed like a **real-world SaaS ATS system**.

##  Key Highlights
✅ Industry-agnostic (Tech, Finance, HR, Healthcare, Marketing, Operations, etc.)  
✅ Hybrid ATS logic + AI reasoning  
✅ Batch resume screening support  
✅ Visual analytics (bars, pies, progress indicators)  
✅ Embedded AI chatbot for real-time guidance  
✅ Secure, cloud-ready, production architecture  

##  What ResumeIQ Pro Does
- Parses real-world resumes (PDF)
- Accepts job descriptions via upload or manual paste
- Mimics real ATS skill matching logic
- Uses AI to understand **semantic role fit**
- Identifies:
  - Matched skills
  - Missing skills
  - Skill match percentage
- Generates:
  - Professional candidate evaluation
  - Skill gap analysis
  - Personalized learning roadmap
- Provides **visual insights + chatbot support**

---

## 🏗️ Tech Stack

### Backend
- **Flask**
- **Python**

### AI & NLP
- **LangChain**
- **Groq LLM**
- **ChatGroq (llama-3.1-8b-instant)**
- **ConversationChain**
- **ConversationBufferMemory**
- **PromptTemplate**

### Parsing
- **pdfplumber**

### Frontend
- Flask templates (HTML, CSS, JS)
- Chart-based visual analytics (bars, pies, progress bars)

### Deployment
- Render-ready
- Linux-safe
- Environment-variable based secrets

## 📁 Project Structure
resumeiq-pro/
│
├── app.py # Flask routes & orchestration
├── resume_parser.py # Resume text extraction
├── skill_matcher.py # ATS-style skill matching logic
├── ai_analyzer.py # LangChain + Groq semantic analysis
├── chatbot_engine.py # Conversational AI logic
├── skills.json # Curated skill taxonomy
├── templates/ # UI templates
├── static/ # CSS, JS, assets
├── requirements.txt # Dependencies
├── runtime.txt # Python runtime
├── config.py # Configuration
└── README.md


---

## ⚙️ Core Features

### 📄 Resume Parsing
- Extracts clean text from real resumes
- Handles multi-column layouts, bullets, and formatting issues

### 🧮 ATS-Style Skill Matching
- Uses curated skill taxonomy
- Identifies matched, missing, and partial skills
- Generates explainable match percentage

### 🤖 AI Semantic Analysis
- Understands job intent and resume context
- Produces professional recruiter-style feedback
- Generates actionable improvement suggestions

### 📊 Visual Analytics
- Skill match bar charts
- Match vs missing skill pie charts
- ATS score & role-fit progress bars

### 💬 Embedded AI Chatbot
- Context-aware (resume + JD + scores)
- Answers questions like:
  - “Why is my score low?”
  - “Which skills should I focus on?”
  - “How can I improve in 30 days?”
- Acts as a **career coach + recruiter assistant**
- 
## 🖥️ How to Run Locally
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Mouryachowdaryy/resumeiq-pro.git
cd resumeiq-pro

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables
Create a .env file:
GROQ_API_KEY=your_groq_api_key_here

5️⃣ Run the Application
python app.py
Visit:
http://127.0.0.1:5000

