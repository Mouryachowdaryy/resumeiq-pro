# ResumeIQ Pro - AI-Powered Resume Screening & Skill Gap Analyzer

A production-grade SaaS application that combines ATS (Applicant Tracking System) logic with AI-powered semantic intelligence to provide comprehensive resume analysis with visual analytics and career coaching.

## Features

- **Advanced ATS Screening**: Intelligent skill matching across 7 categories with detailed scoring
- **AI Semantic Analysis**: LangChain + Groq LLM for deep candidate evaluation
- **Comprehensive Visualizations**: 10+ interactive charts and graphs (Chart.js)
- **Context-Aware Chatbot**: Real-time AI career coach with full analysis context
- **Batch Processing**: Analyze multiple resumes simultaneously (Recruiter Mode)
- **Multi-Format Support**: PDF, DOCX resume uploads
- **Flexible JD Input**: Upload, paste, or URL import job descriptions
- **Personalized Roadmap**: 30/60/90 day learning plans
- **Professional UI**: Clean, modern design with Tailwind CSS

## Tech Stack

- **Backend**: Flask
- **AI/LLM**: LangChain, Groq (llama-3.1-8b-instant)
- **Frontend**: Tailwind CSS, Chart.js, Alpine.js
- **Resume Parsing**: pdfplumber, python-docx
- **Deployment**: Render, Heroku, AWS compatible

## Prerequisites

- Python 3.9 or higher
- Groq API Key ([Get one here](https://console.groq.com/keys))
- pip package manager

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd resumeiq-pro
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
GROQ_API_KEY=your_groq_api_key_here
FLASK_SECRET_KEY=your_random_secret_key_here
```

To generate a secure Flask secret key:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Create Upload Directory

```bash
mkdir uploads
```

## Running Locally

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Single Resume Analysis

1. Navigate to home page
2. Upload resume (PDF or DOCX)
3. Provide job description (upload file, paste text, or import from URL)
4. Click "Analyze Resume"
5. View comprehensive results with visualizations
6. Chat with AI career coach for personalized advice

### Batch Analysis (Recruiter Mode)

1. Upload multiple resumes (up to 20)
2. Provide single job description
3. View ranked candidate comparison table
4. Access individual detailed analyses

## Project Structure

```
resumeiq-pro/
├── app.py                 # Main Flask application
├── skills.json           # Skill taxonomy database
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment file
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── templates/
│   ├── index.html       # Upload page
│   └── results.html     # Results dashboard
├── static/              # Static assets (auto-created)
└── uploads/             # Temporary file storage (create manually)
```

## Deployment

### Deploy to Render

1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create new Web Service
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add GROQ_API_KEY and FLASK_SECRET_KEY
5. Deploy

### Deploy to Heroku

```bash
# Install Heroku CLI
heroku login

# Create new app
heroku create your-app-name

# Set environment variables
heroku config:set GROQ_API_KEY=your_key
heroku config:set FLASK_SECRET_KEY=your_secret

# Deploy
git push heroku main
```

### Deploy to AWS (EC2)

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install Python and dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```
4. Clone repository and set up application
5. Configure Nginx as reverse proxy
6. Use systemd for process management

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| GROQ_API_KEY | Groq API key for LLM access | Yes |
| FLASK_SECRET_KEY | Secret key for Flask sessions | Yes |
| MAX_FILE_SIZE | Max upload size in bytes | No (default: 5MB) |
| ALLOWED_EXTENSIONS | Allowed file extensions | No |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with upload interface |
| `/analyze` | POST | Analyze single resume |
| `/results` | GET | Display analysis results |
| `/chat` | POST | Chatbot interaction |
| `/batch` | POST | Batch resume analysis |

## Skill Categories

The system analyzes skills across 7 categories:

1. **Technical Skills**: Programming, frameworks, libraries
2. **Tools & Platforms**: SaaS tools, enterprise software
3. **Domain Knowledge**: Industry-specific expertise
4. **Soft Skills**: Leadership, communication, teamwork
5. **Methodologies**: Agile, Scrum, Six Sigma, etc.
6. **Certifications**: Professional credentials
7. **Languages**: Human languages (Spanish, Mandarin, etc.)

## Customization

### Adding New Skills

Edit `skills.json` and add skills to appropriate categories:

```json
{
  "Technical Skills": [
    "Python",
    "JavaScript",
    "Your New Skill"
  ]
}
```

### Modifying AI Prompts

Edit prompt templates in `app.py`:

```python
EVALUATION_PROMPT = PromptTemplate(
    input_variables=["resume", "job_description", ...],
    template="""Your custom prompt here..."""
)
```

### Adjusting Scoring Algorithm

Modify `calculate_skill_match()` function in `app.py`:

```python
# Customize weights
category_earned = len(matched) * 10  # Change multiplier
```

## Troubleshooting

### PDF Parsing Issues

If resume parsing fails:
- Ensure PDF is not password-protected
- Check if PDF has embedded text (not scanned image)
- Try converting to DOCX format

### API Rate Limits

Groq has rate limits:
- Free tier: Limited requests per minute
- If exceeded, wait or upgrade plan

### Memory Issues

For batch processing of many resumes:
- Increase server memory
- Process resumes in smaller batches
- Implement queue system (Redis + Celery)

## Performance Optimization

- **Caching**: Implement Redis for skill taxonomy caching
- **Async Processing**: Use Celery for batch jobs
- **CDN**: Serve static assets via CDN
- **Database**: Add PostgreSQL for storing analyses
- **Load Balancing**: Use Nginx or AWS ELB for scaling

## Security Best Practices

- Never commit `.env` file to Git
- Use HTTPS in production
- Implement rate limiting (Flask-Limiter)
- Sanitize all file uploads
- Enable CSRF protection (Flask-WTF)
- Regular dependency updates

## Future Enhancements

- [ ] Resume rewriting suggestions
- [ ] Interview question generator
- [ ] Salary insights based on skills
- [ ] Career path visualizations
- [ ] Email integration
- [ ] Chrome extension for LinkedIn
- [ ] API access tier
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Export to PDF/CSV

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create GitHub issue
- Email: support@resumeiq.com (example)
- Documentation: [Link to docs]

## Acknowledgments

- LangChain for LLM orchestration framework
- Groq for fast LLM inference
- Chart.js for beautiful visualizations
- Tailwind CSS for modern styling
- pdfplumber for PDF parsing

## Version History

- **v1.0.0** (2024-01) - Initial release
  - Core ATS functionality
  - AI analysis with Groq
  - Visual analytics dashboard
  - Context-aware chatbot
  - Batch processing

---

**Built with ❤️ for recruiters, job seekers, and HR professionals**

**ResumeIQ Pro** - Unlock Your Resume's Potential
