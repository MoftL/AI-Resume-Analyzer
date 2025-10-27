import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.job_matcher import JobMatcher

# Test data
sample_resume = {
    'skills': ['python', 'react', 'docker', 'aws', 'sql'],
    'education': ['computer science', 'bachelor'],
    'raw_text': 'Software engineer with 3 years experience building web applications'
}

sample_jobs = [
    {
        'title': 'Senior Python Developer',
        'description': 'Looking for Python expert with AWS and Docker experience',
        'company': 'TechCorp',
        'url': 'https://example.com/job1'
    },
    {
        'title': 'React Frontend Developer',
        'description': 'Need React developer for building modern web apps',
        'company': 'WebStartup',
        'url': 'https://example.com/job2'
    },
    {
        'title': 'Java Backend Engineer',
        'description': 'Java Spring Boot developer needed for enterprise applications',
        'company': 'BigCorp',
        'url': 'https://example.com/job3'
    }
]

# Initialize matcher
matcher = JobMatcher()

# Match resume to jobs
results = matcher.match_resume_to_jobs(sample_resume, sample_jobs, top_n=3)

if results['success']:
    print("Top Matches:\n")
    for i, match in enumerate(results['matches'], 1):
        print(f"{i}. {match['job']['title']}")
        print(f"   Score: {match['match_score']}% - {match['match_grade']}")
        print(f"   Company: {match['job']['company']}\n")