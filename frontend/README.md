# 🎯 AI Resume Analyzer

An intelligent, full-stack resume analysis tool that provides ATS compatibility scores, actionable feedback, and AI-powered job matching using semantic similarity.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)

## ✨ Features

- **📄 Smart Resume Parsing** - Extract information from PDF and DOCX files with international format support
- **📊 ATS Scoring (0-100)** - Comprehensive analysis based on industry-standard ATS criteria
- **💡 Actionable Feedback** - Detailed, categorized suggestions for improvement
- **🤖 AI Job Matching** - Semantic similarity matching using sentence transformers
- **🔄 Smart Keywords** - Auto-generate job search keywords based on resume analysis
- **🌍 International Support** - Handles phone numbers and formats from multiple countries (US, UK, EU, Romania)
- **🎨 Modern UI** - Beautiful, responsive interface with real-time updates

## 🚀 Demo

### Resume Analysis
Upload your resume → Get instant ATS score → Receive detailed feedback

### Job Matching
Automatically generate search keywords → Find matching jobs → Get AI-powered similarity scores

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **spaCy** - Advanced NLP for text extraction and entity recognition
- **Sentence Transformers** - AI-powered semantic similarity for job matching
- **PyPDF2 & python-docx** - Resume file parsing
- **Adzuna API** - Real-time job postings integration

### Frontend
- **React** - Component-based UI framework
- **Vite** - Fast build tool and dev server
- **Axios** - HTTP client for API communication
- **Lucide React** - Modern icon library

## 📦 Installation

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Create .env file for API credentials (see below)
# Start backend server
uvicorn main:app --reload
```

#### Setting up Adzuna API (Required for Job Matching)

1. **Get Free API Credentials:**
   - Go to [Adzuna Developer Portal](https://developer.adzuna.com/)
   - Click "Request API Key"
   - Fill out the registration form
   - You'll receive your `app_id` and `app_key` via email

2. **Create `.env` file in `backend/` directory:**
   ```bash
   cd backend
   touch .env  # Linux/Mac
   # Or create manually on Windows
   ```

3. **Add your credentials to `.env`:**
   ```env
   ADZUNA_APP_ID=your_app_id_here
   ADZUNA_APP_KEY=your_app_key_here
   ```
   
   **Example:**
   ```env
   ADZUNA_APP_ID=12345678
   ADZUNA_APP_KEY=abc123def456ghi789jkl012mno345pq
   ```

4. **Important Notes:**
   - ⚠️ **Never commit `.env` to GitHub** (already in `.gitignore`)
   - ✅ Free tier: 50 API calls/month
   - ✅ No credit card required
   - 📍 Supports multiple countries: US, UK, Germany, France, Netherlands, Poland

Backend runs at `http://localhost:8000`  
API docs available at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`

## 🎮 Usage

1. **Upload Resume** - Select your PDF or DOCX resume file
2. **Analyze** - Get instant ATS score with detailed breakdown:
   - Contact Information (15 pts)
   - Section Headers (20 pts)
   - Skills (25 pts)
   - Formatting (15 pts)
   - Quantifiable Achievements (15 pts)
   - Action Verbs (10 pts)
3. **Review Feedback** - See color-coded suggestions organized by category
4. **Find Jobs** - Auto-generated keywords search for matching positions
5. **Browse Matches** - View AI-ranked job listings with similarity scores

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze resume and return ATS score |
| `/match-jobs` | POST | Find matching jobs for uploaded resume |
| `/jobs/search` | GET | Search jobs without resume upload |

## 🏗️ Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── utils/
│   │   ├── parser.py           # Resume parsing with international support
│   │   ├── ats_scorer.py       # ATS scoring algorithm
│   │   ├── job_fetcher.py      # Job API integration
│   │   └── job_matcher.py      # AI-powered matching engine
│   ├── uploads/                # Temporary file storage
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── App.css             # Styling
│   │   └── config.js           # API configuration
│   ├── public/
│   │   ├── logo.png
│   │   └── favicon.ico
│   └── package.json
├── tests/                      # Test scripts
├── data/                       # Sample resumes
└── README.md
```

## 🔑 Environment Variables

The application requires Adzuna API credentials for job matching functionality.

### Required Variables (`.env` file in `backend/` directory):

| Variable | Description | How to Get |
|----------|-------------|------------|
| `ADZUNA_APP_ID` | Your Adzuna application ID | Register at [developer.adzuna.com](https://developer.adzuna.com/) |
| `ADZUNA_APP_KEY` | Your Adzuna API key | Received via email after registration |

### Example `.env` file:
```env
ADZUNA_APP_ID=12345678
ADZUNA_APP_KEY=abc123def456ghi789jkl012mno345pq
```

⚠️ **Security Note:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

## 🎯 ATS Scoring Breakdown

The system evaluates resumes across 6 key categories:

1. **Contact Info (15%)** - Email and phone presence
2. **Sections (20%)** - Standard headers (Experience, Education, Skills)
3. **Skills (25%)** - Technical skills count and relevance
4. **Formatting (15%)** - Bullet points, length, readability
5. **Achievements (15%)** - Quantifiable results with numbers
6. **Action Verbs (10%)** - Strong verbs (Led, Developed, Implemented)

**Grading:**
- 90-100: Excellent - ATS-optimized
- 75-89: Good - Minor improvements needed
- 60-74: Fair - Moderate revisions required
- 0-59: Poor - Major overhaul needed

## 🌍 International Support

Supports phone number formats from:
- 🇺🇸 United States
- 🇬🇧 United Kingdom
- 🇷🇴 Romania
- 🇪🇺 European Union countries
- And more international formats

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built with ❤️ using FastAPI, React, and AI

---

### 🌟 Star this repo if you find it helpful!
