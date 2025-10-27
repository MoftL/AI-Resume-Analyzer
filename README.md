# AI Resume Analyzer

An intelligent resume analysis tool that provides ATS scores, actionable feedback, and AI-powered job matching.

## Features

- 📄 **Resume Parsing**: Extract information from PDF and DOCX files
- 📊 **ATS Scoring**: Get scored 0-100 on ATS compatibility
- 💡 **Smart Feedback**: Receive actionable improvement suggestions
- 🎯 **AI Job Matching**: Find jobs that match your resume using semantic similarity
- 🔄 **Smart Keywords**: Auto-generate job search keywords from your skills

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **spaCy** - NLP for text extraction
- **Sentence Transformers** - AI-powered job matching
- **Adzuna API** - Real job postings

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **Lucide React** - Icons

## Installation

### Prerequisites
- Python 3.13
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn[standard] python-multipart python-dotenv
pip install spacy PyPDF2 python-docx sentence-transformers
pip install torch scikit-learn requests pydantic

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env file with your Adzuna API credentials
echo "ADZUNA_APP_ID=your_app_id" > .env
echo "ADZUNA_APP_KEY=your_app_key" >> .env

# Run backend
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend runs at: http://localhost:5173

## Usage

1. **Upload Resume**: Upload your PDF or DOCX resume
2. **Analyze**: Get instant ATS score and detailed feedback
3. **Find Jobs**: Auto-generated keywords search for matching jobs
4. **Apply**: Browse AI-matched jobs with similarity scores

## API Endpoints

- `GET /health` - Health check
- `POST /analyze` - Analyze resume and get ATS score
- `POST /match-jobs` - Find matching jobs for resume
- `GET /jobs/search` - Search jobs without resume

## Project Structure
```
ai-resume-analyzer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── utils/
│   │   ├── parser.py        # Resume parsing
│   │   ├── ats_scorer.py    # ATS scoring logic
│   │   ├── job_fetcher.py   # Job API integration
│   │   └── job_matcher.py   # AI matching
│   └── uploads/             # Temporary file storage
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── config.js        # API configuration
│   │   └── App.css          # Styles
│   └── package.json
├── tests/                   # Test scripts
└── data/                    # Sample resumes
```

## License

MIT

## Author

Puie Sebastian

Built with ❤️ using FastAPI and React
```

---
