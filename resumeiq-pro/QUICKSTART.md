# QUICKSTART GUIDE - ResumeIQ Pro

Get up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] pip installed
- [ ] Groq API key obtained from https://console.groq.com/keys

## Setup Steps

### 1. Extract the ZIP file

```bash
unzip resumeiq-pro.zip
cd resumeiq-pro
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- LangChain & Groq (AI/LLM)
- pdfplumber (PDF parsing)
- python-docx (Word document parsing)
- Other required packages

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env
```

Edit `.env` file and add your API keys:

```
GROQ_API_KEY=your_actual_groq_api_key_here
FLASK_SECRET_KEY=generate_a_random_secret_key
```

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Create Upload Directory

```bash
mkdir uploads
```

### 6. Run the Application

```bash
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### 7. Open in Browser

Navigate to: `http://localhost:5000`

## First Test Run

1. **Upload a Resume**: Click the upload zone and select a PDF or DOCX resume
2. **Add Job Description**: Either:
   - Paste job description text, OR
   - Upload a JD file, OR
   - Import from URL (LinkedIn/Indeed)
3. **Click "Analyze Resume"**
4. **View Results**: See comprehensive analysis with charts, scores, and insights
5. **Chat with AI**: Click the chat icon in bottom-right to ask questions

## Troubleshooting

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "GROQ_API_KEY not found"
Make sure you:
1. Created `.env` file (copy from `.env.example`)
2. Added your actual Groq API key
3. Restarted the application

### PDF parsing error
- Ensure PDF is not password-protected
- Try converting to DOCX
- Check if PDF has actual text (not just images)

### Port already in use
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

## Testing the System

### Using Test Resume

1. Create a test resume PDF with:
   - Contact info (email, phone, LinkedIn)
   - Skills (Python, JavaScript, AWS, etc.)
   - Work experience
   - Education

2. Create a test job description with:
   - Job title
   - Required skills
   - Experience requirements
   - Responsibilities

3. Upload both and analyze

### Expected Results

You should see:
- ATS Score (0-100)
- Role-Fit Score (stars)
- Multiple interactive charts
- Matched skills (green tags)
- Missing skills (red tags)
- AI-generated strengths & weaknesses
- 30/60/90 day learning plan
- Working chatbot

## Next Steps

### Customize Skills Database

Edit `skills.json` to add industry-specific skills:

```json
{
  "Technical Skills": [
    "Python",
    "Your Custom Skill"
  ]
}
```

### Deploy to Production

See README.md for deployment guides to:
- Render (easiest)
- Heroku
- AWS

### Enable Additional Features

See README.md "Future Enhancements" section

## Support

If you encounter issues:
1. Check this guide first
2. Read full README.md
3. Check console/terminal for error messages
4. Ensure all dependencies installed correctly

## File Structure Overview

```
resumeiq-pro/
├── app.py              # Main application - START HERE
├── skills.json         # Skill database - CUSTOMIZE THIS
├── requirements.txt    # Dependencies
├── .env               # Your API keys - CREATE THIS
├── templates/
│   ├── index.html     # Upload page
│   └── results.html   # Results dashboard
└── uploads/           # Temp storage - CREATE THIS
```

## Key Features to Test

1. **ATS Scoring**: Upload resume and see detailed skill matching
2. **Visual Analytics**: 10+ charts showing different insights
3. **AI Analysis**: GPT-powered evaluation and recommendations
4. **Chatbot**: Ask questions about your analysis
5. **Batch Mode**: Upload multiple resumes at once (coming soon)

## Default Credentials

No login required - application is ready to use immediately after setup.

## Production Checklist

Before deploying to production:
- [ ] Change FLASK_SECRET_KEY to secure random value
- [ ] Set DEBUG=False
- [ ] Use production WSGI server (gunicorn included)
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Implement rate limiting
- [ ] Configure backup for analysis data

---

**Congratulations! You're ready to use ResumeIQ Pro.**

For detailed documentation, see README.md
For deployment instructions, see README.md "Deployment" section

**Happy analyzing!**
