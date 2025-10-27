from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class JobMatcher:
    """
    Uses AI to match resumes with job postings based on semantic similarity
    
    How it works:
    1. Loads a pre-trained language model (sentence-transformers)
    2. Converts resume text into a 384-dimensional vector (embedding)
    3. Converts each job description into a vector
    4. Calculates cosine similarity between resume and job vectors
    5. Higher similarity score = better match
    
    Why sentence-transformers?
    - Understands context and meaning, not just keywords
    - Pre-trained on millions of sentences
    - Fast and accurate
    - Industry standard for semantic search
    """

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the matcher with a pre-trained model
        
        Model: all-MiniLM-L6-v2
        - Size: 80MB (small, fast)
        - Dimensions: 384
        - Performance: Very good for short texts
        - Speed: ~14,000 sentences/second on CPU
        
        Alternative models you could use:
        - 'all-mpnet-base-v2' (better quality, slower)
        - 'paraphrase-MiniLM-L3-v2' (faster, smaller)
        """
        print(f"Loading model '{model_name}'...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded.")

    def create_resume_embedding(self, parsed_resume):
        """
        Convert resume into a vector representation
        
        Process:
        1. Combine relevant resume sections (skills, experience text)
        2. Pass through the transformer model
        3. Get back a 384-dimensional vector
        
        Parameters:
        -----------
        parsed_resume : dict
            Output from ResumeParser.parse_resume()
            
        Returns:
        --------
        numpy.ndarray: 384-dimensional vector representing the resume
        """
        resume_text_parts=[]

        if parsed_resume.get('skills'):
            skills_text = " ".join(parsed_resume['skills'])
            resume_text_parts.append(f"Skills: {skills_text}")
        
        if parsed_resume.get('education'):
            education_text = " ".join(parsed_resume['education'])
            resume_text_parts.append(f"Education: {education_text}")
        
        if parsed_resume.get('raw_text'):
            raw_text_sample = parsed_resume['raw_text'][:1000]
            resume_text_parts.append(raw_text_sample)

        full_resume_text = " ".join(resume_text_parts)

        embedding = self.model.encode(full_resume_text, convert_to_numpy=True)

        return embedding
    
    def create_job_embedding(self, jobs):
        """
        Convert multiple job descriptions into vectors
        
        Parameters:
        -----------
        jobs : list of dict
            List of jobs from JobFetcher.search_jobs()
            Each job should have 'title' and 'description'
            
        Returns:
        --------
        numpy.ndarray: Matrix of shape (num_jobs, 384)
        """
        job_texts=[]

        for job in jobs:
            title = job.get('title', '')
            description = job.get('description', '')
            
            description_sample = description[:500] if description else ''

            job_text=f"{title}. {description_sample}"
            job_texts.append(job_text)

        job_embeddings = self.model.encode(job_texts, convert_to_numpy=True)

        return job_embeddings
    
    def calculate_match_scores(self, resume_embedding, job_embeddings):
        """
        Calculate similarity scores between resume and jobs
        
        Uses cosine similarity:
        - 1.0 = identical vectors (perfect match)
        - 0.0 = orthogonal vectors (no relation)
        - -1.0 = opposite vectors (unlikely in practice)
        
        Formula: cosine(A,B) = (A·B) / (||A|| × ||B||)
        
        Parameters:
        -----------
        resume_embedding : numpy.ndarray
            Vector representing the resume
            
        job_embeddings : numpy.ndarray
            Matrix of job vectors
            
        Returns:
        --------
        numpy.ndarray: Array of similarity scores (0-1 range)
        """
        resume_embedding = resume_embedding.reshape(1, -1)

        similarities=cosine_similarity(resume_embedding, job_embeddings)
        scores=similarities[0]*100
        return scores
    
    def match_resume_to_jobs(self, parsed_resume, jobs, top_n=10):
        """
        Main matching function - finds best job matches for a resume
        
        Process:
        1. Create resume embedding
        2. Create job embeddings
        3. Calculate similarity scores
        4. Rank jobs by score
        5. Return top N matches with details
        
        Parameters:
        -----------
        parsed_resume : dict
            Output from ResumeParser.parse_resume()
            
        jobs : list of dict
            Jobs from JobFetcher.search_jobs()
            
        top_n : int
            Number of top matches to return
            
        Returns:
        --------
        list of dict: Top matched jobs with scores
        [
            {
                'job': {...},  # Original job data
                'match_score': 85.4,  # 0-100 score
                'match_grade': 'Excellent'  # Rating
            },
            ...
        ]
        """
        if not jobs:
            return {
                'success': False,
                'error': 'No jobs provided to match',
                'matches': []
            }
        
        try:
            print("Creating resume embedding...")
            resume_embedding = self.create_resume_embedding(parsed_resume)
            
            print(f"Creating job embeddings for {len(jobs)}...")
            job_embeddings = self.create_job_embedding(jobs)

            print("Calculating match scores...")
            scores = self.calculate_match_scores(resume_embedding, job_embeddings)

            job_matches=[]
            for i,job in enumerate(jobs):
                match_score=float(scores[i])
                if match_score >= 80:
                    grade = "Excellent Match"
                elif match_score >= 70:
                    grade = "Good Match"
                elif match_score >= 60:
                    grade = "Fair Match"
                else:
                    grade = "Poor Match"

                job_matches.append({
                    'job': job,
                    'match_score': round(match_score, 2),
                    'match_grade': grade
                })
            
            job_matches.sort(key=lambda x: x['match_score'], reverse=True)
            top_matches = job_matches[:top_n]

            print(f"✅ Found {len(top_matches)} top matches!")

            return {
                'success': True,
                'matches': top_matches,
                'total_jobs_analyzed': len(jobs),
                'average_score': round(float(np.mean(scores)), 2)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'matches': []
            }
        
    def explain_match(self,parsed_resume,job,match_score):
        """
        Explain WHY a job matched (for user transparency)
        
        Analyzes:
        - Skill overlap
        - Common keywords
        - Match strength
        
        Parameters:
        -----------
        parsed_resume : dict
            Parsed resume data
            
        job : dict
            Job posting data
            
        match_score : float
            Calculated match score
            
        Returns:
        --------
        dict: Explanation with matched skills and keywords
        """
        explanation={
            'match_score': match_score,
            'matched_skills': [],
            'missing_skills': [],
            'key_highlights': []
        }

        job_text=(job.get('description', "") + ' ' + job.get('title', "")).lower()
        resume_skills=[s.lower() for s in parsed_resume.get('skills', [])]

        for skill in resume_skills:
            if skill in job_text:
                explanation['matched_skills'].append(skill)

        common_skills=['python','java','c++','sql','javascript','aws','docker','kubernetes','machine learning','data analysis','java','react','node.js','linux','git','html','css','tensorflow','pandas','excel']
        for skill in common_skills:
            if skill in job_text and skill not in resume_skills:
                explanation['missing_skills'].append(skill)
        
        if match_score >= 80:
            explanation['key_highlights'].append("Strong overall fit")
            explanation['key_highlights'].append(f"{len(explanation['matched_skills'])} matching skills")
        elif match_score >= 70:
            explanation['key_highlights'].append("Good potential match")
        else:
            explanation['key_highlights'].append("Consider gaining additional skills")
        
        return explanation
