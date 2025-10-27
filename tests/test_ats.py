import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.parser import ResumeParser
from utils.ats_scorer import ATSScorer

parser = ResumeParser()
scorer = ATSScorer()

parsed = parser.parse_resume('data/sample_resume.pdf')
result = scorer.calculate_ats_score(parsed)

print(f"ATS Score: {result['score']}/100 ({result['grade']})")
print("\nFeedback:")
for category, feedback_list in result['feedback'].items():
    print(f"\n{category.upper()}:")
    for item in feedback_list:
        print(f"  {item}")