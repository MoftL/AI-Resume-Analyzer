import re

class ATSScorer:
    """
    ATS (Applicant Tracking System) Scorer
    
    Evaluates resumes based on common ATS criteria:
    - Contact information (15 pts)
    - Standard sections (20 pts)
    - Skills (25 pts)
    - Formatting (15 pts)
    - Quantifiable achievements (15 pts)
    - Action verbs (10 pts)
    
    Total: 100 points
    """
    
    def __init__(self):
        """Initialize with required sections and action verbs lists"""
        self.required_sections = [
            'experience', 'education', 'skills', 'certifications',
            'work experience', 'professional experience', 'technical skills',
            'projects'
        ]
        
        self.action_verbs = [
            'developed', 'managed', 'created', 'implemented', 'designed',
            'led', 'improved', 'increased', 'reduced', 'achieved',
            'built', 'launched', 'optimized', 'analyzed', 'coordinated',
            'collaborated', 'delivered', 'executed', 'facilitated'
        ]
    
    def check_contact_info(self, parsed_resume):
        """
        Score: 15 points
        Check for email and phone number
        """
        score = 0
        feedback = []
        
        email = parsed_resume.get('contact_info', {}).get('email')
        phone = parsed_resume.get('contact_info', {}).get('phone')
        
        if email:
            score += 10
            feedback.append("✓ Email found")
        else:
            feedback.append("✗ Email missing - Add a professional email address")
        
        if phone:
            score += 5
            feedback.append("✓ Phone number found")
        else:
            feedback.append("✗ Phone number missing - Include a valid phone number")
        
        return score, feedback
    
    def check_sections(self, text):
        """
        Score: 20 points
        Check for standard resume sections
        """
        score = 0
        feedback = []
        text_lower = text.lower()
        
        found_sections = [section for section in self.required_sections if section in text_lower]
        
        if len(found_sections) >= 3:
            score = 20
            feedback.append(f"✓ Found sections: {', '.join(found_sections[:3])}")
        elif len(found_sections) >= 2:
            score = 15
            feedback.append(f"✓ Found sections: {', '.join(found_sections)}. Add more standard headers")
        else:
            score = 5
            feedback.append("✗ Few or no standard sections. Include headers like Experience, Education, Skills")
        
        return score, feedback
    
    def check_skills(self, skills):
        """
        Score: 25 points
        Check number of skills listed
        """
        score = 0
        feedback = []
        
        num_skills = len(skills) if skills else 0
        
        if num_skills >= 8:
            score = 25
            feedback.append(f"✓ Excellent - {num_skills} skills found")
        elif num_skills >= 5:
            score = 18
            feedback.append(f"⚠ Good - {num_skills} skills found. Add 3-5 more relevant skills")
        elif num_skills >= 3:
            score = 10
            feedback.append(f"⚠ Fair - {num_skills} skills found. Add 5-8 more skills")
        else:
            score = 5
            feedback.append(f"✗ Weak - Only {num_skills} skills. Add a dedicated Skills section with 8+ skills")
        
        return score, feedback
    
    def check_formatting(self, text):
        """
        Score: 15 points
        Check for bullet points and appropriate length
        """
        score = 0
        feedback = []
        
        # Check for bullet points
        bullet_count = text.count('•') + text.count('-') + text.count('*')
        if bullet_count >= 5:
            score += 8
            feedback.append(f"✓ {bullet_count} bullet points found - Good use of lists")
        else:
            feedback.append(f"⚠ Only {bullet_count} bullet points - Use more lists for readability")
        
        # Check word count
        word_count = len(text.split())
        if 400 <= word_count <= 1000:
            score += 7
            feedback.append(f"✓ Word count is {word_count} - Ideal length")
        elif word_count < 400:
            feedback.append(f"⚠ Word count is {word_count} - Consider adding more detail")
        else:
            score += 3
            feedback.append(f"⚠ Word count is {word_count} - Ensure content is relevant and concise")
        
        return score, feedback
    
    def check_quantifiable_achievements(self, text):
        """
        Score: 15 points
        Check for numbers and percentages (quantified achievements)
        """
        score = 0
        feedback = []
        
        percentages = re.findall(r'\b\d{1,3}%\b', text)
        numbers = re.findall(r'\b\d+\b', text)
        
        achievements_count = len(percentages) + (len(numbers) // 3)
        
        if achievements_count >= 5:
            score = 15
            feedback.append(f"✓ Great - {len(percentages)} quantified achievements found")
        elif achievements_count >= 3:
            score = 10
            feedback.append(f"⚠ Good - {len(percentages)} quantified achievements. Add 2-3 more")
        else:
            score = 5
            feedback.append("✗ Weak - Add numbers to show impact (e.g., 'Increased efficiency by 30%')")
        
        return score, feedback
    
    def check_action_verbs(self, text):
        """
        Score: 10 points
        Check for strong action verbs
        """
        score = 0
        feedback = []
        text_lower = text.lower()
        
        found_verbs = [verb for verb in self.action_verbs if verb in text_lower]
        
        if len(found_verbs) >= 8:
            score = 10
            feedback.append(f"✓ Excellent use of action verbs ({len(found_verbs)} found)")
        elif len(found_verbs) >= 5:
            score = 7
            feedback.append(f"⚠ Good action verbs ({len(found_verbs)}). Add more like 'achieved', 'optimized'")
        else:
            score = 3
            feedback.append("✗ Weak - Start bullet points with action verbs like 'Developed', 'Managed', 'Led'")
        
        return score, feedback
    
    def calculate_ats_score(self, parsed_resume):
        """
        Main scoring function - combines all checks
        
        Parameters:
            parsed_resume (dict): Output from ResumeParser.parse_resume()
        
        Returns:
            dict: {
                'score': int (0-100),
                'grade': str (Excellent/Good/Fair/Poor),
                'feedback': dict (detailed feedback by category)
            }
        """
        total_score = 0
        all_feedback = {
            'contact_info': [],
            'sections': [],
            'skills': [],
            'formatting': [],
            'achievements': [],
            'action_verbs': [],
            'overall_tips': []
        }
        
        text = parsed_resume.get('raw_text', '')
        
        # Run all checks
        score, feedback = self.check_contact_info(parsed_resume)
        total_score += score
        all_feedback['contact_info'] = feedback
        
        score, feedback = self.check_sections(text)
        total_score += score
        all_feedback['sections'] = feedback
        
        score, feedback = self.check_skills(parsed_resume.get('skills', []))
        total_score += score
        all_feedback['skills'] = feedback
        
        score, feedback = self.check_formatting(text)
        total_score += score
        all_feedback['formatting'] = feedback
        
        score, feedback = self.check_quantifiable_achievements(text)
        total_score += score
        all_feedback['achievements'] = feedback
        
        score, feedback = self.check_action_verbs(text)
        total_score += score
        all_feedback['action_verbs'] = feedback
        
        # Determine grade
        if total_score >= 90:
            grade = "Excellent"
            all_feedback['overall_tips'].append("Your resume is ATS-optimized! 🎉")
        elif total_score >= 75:
            grade = "Good"
            all_feedback['overall_tips'].append("Strong resume. Fix minor issues to reach 90+")
        elif total_score >= 60:
            grade = "Fair"
            all_feedback['overall_tips'].append("Needs improvement. Focus on skills and achievements")
        else:
            grade = "Poor"
            all_feedback['overall_tips'].append("Major revisions needed. Follow all recommendations above")
        
        return {
            'score': total_score,
            'grade': grade,
            'feedback': all_feedback
        }