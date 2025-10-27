import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.parser import ResumeParser

parser = ResumeParser()

# Test with a sample resume (put one in your data/ folder)
result = parser.parse_resume('data/sample_resume.pdf')

print("✅ Parser working!")
print(f"Skills found: {result['skills']}")
print(f"Contact: {result['contact_info']}")
print(f"Entities: {result['entities']}")