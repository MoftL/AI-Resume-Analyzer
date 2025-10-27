import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
Complete Pipeline Test: Resume Analysis + Job Matching

This script demonstrates the full workflow:
1. Parse a resume
2. Calculate ATS score
3. Fetch real jobs
4. Match resume to jobs using AI
"""

from utils.parser import ResumeParser
from utils.ats_scorer import ATSScorer
from utils.job_fetcher import JobFetcher
from utils.job_matcher import JobMatcher

def test_complete_pipeline():
    """
    Test the entire AI Resume Analyzer pipeline
    """
    
    print("=" * 80)
    print("AI RESUME ANALYZER - COMPLETE PIPELINE TEST")
    print("=" * 80)
    
    # ===== STEP 1: PARSE RESUME =====
    print("\n📄 STEP 1: Parsing Resume...")
    print("-" * 80)
    
    parser = ResumeParser()
    
    # You need to place a sample resume in data/ folder
    # Change this path to your resume file
    resume_path = 'data/sample_resume.pdf'  # or .docx
    
    try:
        parsed_resume = parser.parse_resume(resume_path)
        print(f"✅ Resume parsed successfully!")
        print(f"   - Skills found: {len(parsed_resume['skills'])}")
        print(f"   - Word count: {parsed_resume['word_count']}")
        print(f"   - Contact: {parsed_resume['contact_info']['email']}")
    except FileNotFoundError:
        print("❌ Error: Resume file not found!")
        print(f"   Please place a resume at: {resume_path}")
        return
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        return
    
    # ===== STEP 2: ATS SCORING =====
    print("\n📊 STEP 2: Calculating ATS Score...")
    print("-" * 80)
    
    scorer = ATSScorer()
    ats_result = scorer.calculate_ats_score(parsed_resume)
    
    print(f"✅ ATS Score: {ats_result['score']}/100 ({ats_result['grade']})")
    print("\nTop Recommendations:")
    for category, feedback_list in list(ats_result['feedback'].items())[:3]:
        if feedback_list:
            print(f"  • {feedback_list[0]}")
    
    # ===== STEP 3: FETCH JOBS =====
    print("\n🌍 STEP 3: Fetching Jobs from Europe...")
    print("-" * 80)
    
    fetcher = JobFetcher()
    
    # Determine search keywords from resume skills
    if parsed_resume['skills']:
        # Use top skills as search keywords
        search_keywords = ' '.join(parsed_resume['skills'][:3])
    else:
        search_keywords = "software developer"  # Default
    
    print(f"Searching for: '{search_keywords}'")
    
    # Search in UK (change to 'de', 'fr', etc. for other countries)
    job_results = fetcher.search_jobs(
        keywords=search_keywords,
        location="gb",  # United Kingdom
        results_per_page=20
    )
    
    if job_results['success']:
        jobs = job_results['jobs']
        print(f"✅ Found {len(jobs)} jobs")
    else:
        print(f"❌ Job search failed: {job_results['error']}")
        return
    
    # ===== STEP 4: AI JOB MATCHING =====
    print("\n🎯 STEP 4: Matching Resume to Jobs (AI)...")
    print("-" * 80)
    
    matcher = JobMatcher()
    
    match_results = matcher.match_resume_to_jobs(
        parsed_resume=parsed_resume,
        jobs=jobs,
        top_n=5  # Get top 5 matches
    )
    
    if match_results['success']:
        print(f"✅ Analysis complete!")
        print(f"   Average match score: {match_results['average_score']}%")
        
        # ===== DISPLAY TOP MATCHES =====
        print("\n" + "=" * 80)
        print("🏆 TOP 5 JOB MATCHES")
        print("=" * 80)
        
        for i, match in enumerate(match_results['matches'], 1):
            job = match['job']
            score = match['match_score']
            grade = match['match_grade']
            
            print(f"\n{i}. {job['title']}")
            print(f"   {'─' * 70}")
            print(f"   🏢 Company: {job['company']}")
            print(f"   📍 Location: {job['location']}")
            print(f"   🎯 Match Score: {score}% - {grade}")
            
            if job['salary_min']:
                print(f"   💰 Salary: £{job['salary_min']:,.0f} - £{job['salary_max']:,.0f}")
            
            # Show description preview
            desc_preview = job['description'][:150] + "..." if len(job['description']) > 150 else job['description']
            print(f"   📝 Description: {desc_preview}")
            print(f"   🔗 Apply: {job['url'][:60]}...")
            
            # Explain the match
            explanation = matcher.explain_match(parsed_resume, job, score)
            if explanation['matched_skills']:
                print(f"   ✨ Matched Skills: {', '.join(explanation['matched_skills'][:5])}")
        
        # ===== SUMMARY =====
        print("\n" + "=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print(f"Resume ATS Score: {ats_result['score']}/100")
        print(f"Jobs Analyzed: {match_results['total_jobs_analyzed']}")
        print(f"Best Match Score: {match_results['matches'][0]['match_score']}%")
        print(f"Average Match: {match_results['average_score']}%")
        
        if ats_result['score'] < 75:
            print("\n💡 Tip: Improve your ATS score to increase job match quality!")
        
    else:
        print(f"❌ Matching failed: {match_results['error']}")
    
    print("\n" + "=" * 80)
    print("✅ PIPELINE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_complete_pipeline()