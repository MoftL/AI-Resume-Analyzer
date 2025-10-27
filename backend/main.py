"""
AI Resume Analyzer - FastAPI Backend

This is the main API server that handles:
- Resume file uploads
- Resume parsing and ATS scoring
- Job fetching and AI matching

Run with: uvicorn main:app --reload
Access docs at: http://localhost:8000/docs
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from typing import List, Optional
import os
import shutil
from datetime import datetime

from utils.parser import ResumeParser
from utils.ats_scorer import ATSScorer
from utils.job_fetcher import JobFetcher
from utils.job_matcher import JobMatcher

app = FastAPI(
    title="AI Resume Analyzer",
    description="Upload resumes, get ATS scores, and find matching jobs using AI.",
    version="1.0.0"
)

# Allow CORS for local development (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parser = ResumeParser()
scorer = ATSScorer()
fetcher = JobFetcher()
matcher = JobMatcher()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalyzeResponse(BaseModel):
    success: bool
    ats_score: int
    ats_grade: str
    feedback: dict
    parsed_data: dict
    message: Optional[str] = None

class JobMatchRequest(BaseModel):
    keywords: str
    location: str
    results_per_page: int = 20
    top_matches: int = 10

class JobMatchResponse(BaseModel):
    success: bool
    matches: List[dict]
    total_jobs_analyzed: int
    average_score: float
    message: Optional[str] = None


def save_upload_file(upload_file: UploadFile) -> str:
    timestamp=datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension=os.path.splitext(upload_file.filename)[1]
    unique_filename=f"resume_{timestamp}{file_extension}"
    file_path=os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path

def cleanup_file(filepath: str):
    """Delete file after processing"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"⚠️ Warning: Could not delete file {filepath}. Error: {e}")


@app.get("/")
async def root():
    return {
        "message": "AI Resume Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "upload_and_analyze": "/analyze",
            "match_jobs": "/match-jobs"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Used by monitoring tools to verify API is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "parser": "ready",
            "scorer": "ready",
            "job_fetcher": "ready",
            "ai_matcher": "ready"
        }
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)")
):
    """
    Upload and analyze a resume
    
    Process:
    1. Validate file type
    2. Save file temporarily
    3. Parse resume text and extract info
    4. Calculate ATS score
    5. Return analysis results
    6. Clean up temporary file
    
    Returns:
    - ATS score (0-100)
    - Grade (Excellent/Good/Fair/Poor)
    - Detailed feedback
    - Parsed resume data (skills, contact, etc.)
    """
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and DOCX files are supported."
        )
    
    file_path = None

    try:
        # Save uploaded file
        file_path = save_upload_file(file)
        
        # Parse resume
        parsed_resume = parser.parse_resume(file_path)
        
        # Calculate ATS score
        ats_result = scorer.calculate_ats_score(parsed_resume)
        
        # Return results
        return AnalyzeResponse(
            success=True,
            ats_score=ats_result['score'],
            ats_grade=ats_result['grade'],
            feedback=ats_result['feedback'],
            parsed_data={
                'skills': parsed_resume['skills'],
                'contact_info': parsed_resume['contact_info'],
                'entities': parsed_resume['entities'],
                'education': parsed_resume['education'],
                'word_count': parsed_resume['word_count']
            },
            message="Resume analyzed successfully"
        )
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    finally:
        if file_path is not None:
            cleanup_file(file_path)

@app.post("/match-jobs")
async def match_jobs_to_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    keywords: str = Query(..., description="Job search keywords (e.g., 'python developer')"),
    location: str = Query("gb", description="Country code (gb, de, fr, nl, etc.)"),
    results_per_page: int = Query(20, ge=1, le=50, description="Number of jobs to fetch"),
    top_matches: int = Query(10, ge=1, le=20, description="Number of top matches to return")
):
    """
    Upload resume and find matching jobs
    
    Process:
    1. Upload and parse resume
    2. Fetch jobs from Adzuna API
    3. Use AI to match resume to jobs
    4. Return top matches with scores
    
    Parameters:
    - file: Resume file
    - keywords: What to search for (e.g., "react developer")
    - location: Country code (default: gb = UK)
    - results_per_page: How many jobs to analyze
    - top_matches: How many top results to return
    
    Returns:
    - List of matched jobs with scores
    - Match explanations
    - Average match score
    """

    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and DOCX files are supported."
        )
    
    file_path = None

    try:
        file_path = save_upload_file(file)
        parsed_resume = parser.parse_resume(file_path)

        job_results=fetcher.search_jobs(
            keywords=keywords,
            location=location,
            results_per_page=results_per_page
        )

        if not job_results['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Job fetching error: {job_results.get('error', 'Unknown error')}"
            )
        
        if not job_results['jobs']:
            return {
                "success": False,
                "matches": [],
                "total_jobs_analyzed": 0,
                "average_score": 0.0,
                "message": "No jobs found for the given keywords and location."
            }
        
        match_results = matcher.match_resume_to_jobs(
            parsed_resume=parsed_resume,
            jobs=job_results['jobs'],
            top_n=top_matches
        )

        if not match_results['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Job matching error: {match_results.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "matches": match_results['matches'],
            "total_jobs_analyzed": match_results['total_jobs_analyzed'],
            "average_score": match_results['average_score'],
            "message": f"Found {len(match_results['matches'])} matching jobs."
        }
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
    finally:
        if file_path is not None:
            cleanup_file(file_path)

@app.get("/jobs/search")
async def search_jobs(
    keywords: str = Query(..., description="Job search keywords"),
    location: str = Query("gb", description="Country code"),
    results_per_page: int = Query(10, ge=1, le=50)
):
    """
    Search for jobs without resume matching
    
    Useful for:
    - Browsing available jobs
    - Testing the job API
    - Getting job data for analysis
    
    Returns: List of job postings
    """
    
    try:
        results = fetcher.search_jobs(
            keywords=keywords,
            location=location,
            results_per_page=results_per_page
        )
        
        if results['success']:
            return {
                "success": True,
                "jobs": results['jobs'],
                "count": results['count'],
                "total_results": results['total_results']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=results['error']
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Job search failed: {str(e)}"
        )

# STARTUP/SHUTDOWN EVENTS

@app.on_event("startup")
async def startup_event():
    """Run on API startup"""
    print("=" * 60)
    print("🚀 AI Resume Analyzer API Starting...")
    print("=" * 60)
    print("📚 Loading AI models...")
    print("✅ API ready!")
    print("📖 Docs available at: http://localhost:8000/docs")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on API shutdown"""
    print("\n👋 Shutting down API...")
    # Clean up uploads directory if needed
    # for file in os.listdir(UPLOAD_DIR):
    #     os.remove(os.path.join(UPLOAD_DIR, file))



