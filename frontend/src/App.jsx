import { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Briefcase, TrendingUp, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { API_ENDPOINTS } from './config';
import './App.css';

function App() {
  // State management
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [jobMatches, setJobMatches] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [error, setError] = useState(null);

  // Keywords and location for job search
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('gb');

  /**
   * Analyze skills to determine best job role
   */
  const analyzeSkillsForRole = (skills) => {
    if (!skills || skills.length === 0) return 'software developer';
    
    const skillsLower = skills.map(s => s.toLowerCase());
    
    // Skill category scoring
    const categories = {
      frontend: {
        keywords: ['react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css', 'tailwind', 'bootstrap'],
        role: 'frontend developer'
      },
      backend: {
        keywords: ['python', 'java', 'node.js', 'nodejs', 'django', 'flask', 'fastapi', 'spring', 'express'],
        role: 'backend developer'
      },
      fullstack: {
        keywords: ['full stack', 'fullstack', 'mern', 'mean'],
        role: 'full stack developer'
      },
      mobile: {
        keywords: ['android', 'ios', 'swift', 'kotlin', 'react native', 'flutter'],
        role: 'mobile developer'
      },
      dataScience: {
        keywords: ['machine learning', 'tensorflow', 'pytorch', 'data science', 'pandas', 'numpy', 'scikit-learn'],
        role: 'machine learning engineer'
      },
      dataAnalyst: {
        keywords: ['data analyst', 'sql', 'tableau', 'power bi', 'excel'],
        role: 'data analyst'
      },
      devops: {
        keywords: ['devops', 'kubernetes', 'docker', 'jenkins', 'ci/cd', 'terraform', 'ansible'],
        role: 'devops engineer'
      },
      cloud: {
        keywords: ['aws', 'azure', 'gcp', 'cloud'],
        role: 'cloud engineer'
      },
    };
    
    // Score each category
    const scores = {};
    for (const [category, data] of Object.entries(categories)) {
      scores[category] = skillsLower.filter(skill => 
        data.keywords.some(keyword => skill.includes(keyword))
      ).length;
    }
    
    // Special case: If has both frontend + backend skills = fullstack
    if (scores.frontend >= 2 && scores.backend >= 2) {
      return 'full stack developer';
    }
    
    // Find category with highest score
    const topCategory = Object.keys(scores).reduce((a, b) => 
      scores[a] > scores[b] ? a : b
    );
    
    // If top score is 0, use first skill
    if (scores[topCategory] === 0) {
      return `${skills[0]} developer`;
    }
    
    return categories[topCategory].role;
  };

  /**
   * Generate alternative roles from skills (for regenerate button)
   */
  const generateAlternativeRole = (skills, currentKeyword) => {
    if (!skills || skills.length === 0) return 'software developer';
    
    const skillsLower = skills.map(s => s.toLowerCase());
    const currentLower = currentKeyword.toLowerCase();
    
    // Find all possible roles from skills
    const possibleRoles = [];
    
    const roleMap = {
      'react': 'react developer',
      'angular': 'angular developer',
      'vue': 'vue developer',
      'python': 'python developer',
      'java': 'java developer',
      'javascript': 'javascript developer',
      'typescript': 'typescript developer',
      'node.js': 'node developer',
      'nodejs': 'node developer',
      'django': 'django developer',
      'flask': 'flask developer',
      'fastapi': 'fastapi developer',
      'spring': 'java spring developer',
      'php': 'php developer',
      'ruby': 'ruby developer',
      'go': 'golang developer',
      'rust': 'rust developer',
      'swift': 'ios developer',
      'kotlin': 'android developer',
      'machine learning': 'machine learning engineer',
      'tensorflow': 'machine learning engineer',
      'pytorch': 'ml engineer',
      'data science': 'data scientist',
      'aws': 'aws cloud engineer',
      'azure': 'azure cloud engineer',
      'devops': 'devops engineer',
      'kubernetes': 'kubernetes engineer',
      'docker': 'devops engineer',
    };
    
    // Find all matching roles
    for (const [skill, role] of Object.entries(roleMap)) {
      if (skillsLower.some(s => s.includes(skill))) {
        possibleRoles.push(role);
      }
    }
    
    // Remove duplicates
    const uniqueRoles = [...new Set(possibleRoles)];
    
    // Filter out current keyword
    const alternatives = uniqueRoles.filter(role => {
      const roleWords = role.split(' ');
      return !roleWords.some(word => currentLower.includes(word));
    });
    
    // Return alternative or fallback
    if (alternatives.length > 0) {
      return alternatives[0];
    } else if (uniqueRoles.length > 1) {
      return uniqueRoles[1]; // Return second option
    } else if (uniqueRoles.length > 0) {
      return uniqueRoles[0];
    }
    
    return 'software engineer';
  };

  /**
   * Regenerate keywords from resume (cycles through available roles)
   */
  const regenerateKeywords = () => {
    if (analysisResult?.parsed_data?.skills) {
      const newKeywords = generateAlternativeRole(analysisResult.parsed_data.skills, keywords);
      setKeywords(newKeywords);
    }
  };

  /**
   * Get useful tips based on ATS score
   */
  const getUsefulTips = (score) => {
    if (score >= 90) {
      return [
        "Your resume passes most ATS systems. Focus on tailoring it for specific job descriptions.",
        "Consider creating multiple versions targeting different roles or industries.",
        "Keep your resume updated with recent projects and achievements."
      ];
    } else if (score >= 75) {
      return [
        "Good foundation! Add 2-3 more quantified achievements (e.g., 'Increased performance by 40%').",
        "Ensure all major sections use clear headers: Experience, Skills, Education.",
        "Use industry-standard job titles that match job postings."
      ];
    } else if (score >= 60) {
      return [
        "Add 5-8 technical skills relevant to your target role.",
        "Include numbers and metrics in your achievements (percentages, dollar amounts, team sizes).",
        "Use strong action verbs: Led, Developed, Implemented, Optimized.",
        "Keep your resume to 1-2 pages (400-1000 words)."
      ];
    } else {
      return [
        "Critical: Add contact information (email and phone number).",
        "Create clear sections with headers: Professional Summary, Experience, Skills, Education.",
        "List at least 8 relevant technical skills.",
        "Rewrite experience bullets starting with action verbs and including numbers.",
        "Target length: 1-2 pages. Remove irrelevant information."
      ];
    }
  };

  /**
   * Get ATS score color
   */
  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#3b82f6';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  /**
   * Get feedback icon
   */
  const getFeedbackIcon = (feedback) => {
    if (feedback.startsWith('✓')) return '✅';
    if (feedback.startsWith('⚠')) return '⚠️';
    if (feedback.startsWith('✗')) return '❌';
    return '•';
  };

  /**
   * Handle file selection
   */
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.name.endsWith('.pdf') || selectedFile.name.endsWith('.docx')) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Please upload a PDF or DOCX file');
        setFile(null);
      }
    }
  };

  /**
   * Analyze resume - get ATS score
   */
  const analyzeResume = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(API_ENDPOINTS.analyze, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAnalysisResult(response.data);
      
      // Smart role detection based on ALL skills
      if (response.data.parsed_data?.skills?.length > 0) {
        const suggestedKeywords = analyzeSkillsForRole(response.data.parsed_data.skills);
        setKeywords(suggestedKeywords);
      }
      
      setActiveTab('analysis');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing resume');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Find matching jobs
   */
  const findMatchingJobs = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    if (!keywords.trim()) {
      setError('Please enter job keywords');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${API_ENDPOINTS.matchJobs}?keywords=${encodeURIComponent(keywords)}&location=${location}&results_per_page=20&top_matches=10`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setJobMatches(response.data);
      setActiveTab('jobs');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error finding matching jobs');
      console.error('Job matching error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset everything
   */
  const reset = () => {
    setFile(null);
    setAnalysisResult(null);
    setJobMatches(null);
    setActiveTab('upload');
    setError(null);
    setKeywords('');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1 className="title">
            <img src="/logo.png" alt="Logo" style={{ width: '150px', height: '150px' }} />
            AI Resume Analyzer
          </h1>
          <p className="subtitle">
            Get ATS scores and find matching jobs with AI
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container main-content">
        {/* Tab Navigation */}
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <Upload size={20} />
            Upload Resume
          </button>
          <button
            className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
            onClick={() => setActiveTab('analysis')}
            disabled={!analysisResult}
          >
            <TrendingUp size={20} />
            ATS Analysis
          </button>
          <button
            className={`tab ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
            disabled={!jobMatches}
          >
            <Briefcase size={20} />
            Job Matches
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="upload-section">
            <div className="upload-card">
              <div className="upload-icon">
                <Upload size={48} />
              </div>
              <h2>Upload Your Resume</h2>
              <p>Support for PDF and DOCX files</p>

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="file-input"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="file-label">
                {file ? file.name : 'Choose File'}
              </label>

              {file && (
                <div className="file-info">
                  <CheckCircle size={16} style={{ color: '#10b981' }} />
                  File selected: {file.name}
                </div>
              )}

              <div className="action-buttons">
                <button
                  className="btn btn-primary"
                  onClick={analyzeResume}
                  disabled={!file || loading}
                >
                  {loading ? 'Analyzing...' : '📊 Analyze Resume'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && analysisResult && (
          <div className="analysis-section">
            <div className="score-card">
              <h2>ATS Score</h2>
              <div
                className="score-circle"
                style={{ borderColor: getScoreColor(analysisResult.ats_score) }}
              >
                <span className="score-number">{analysisResult.ats_score}</span>
                <span className="score-label">/ 100</span>
              </div>
              <p className="score-grade" style={{ color: getScoreColor(analysisResult.ats_score) }}>
                {analysisResult.ats_grade}
              </p>
              
              {/* Useful Tips */}
              <div className="useful-tips">
                <h4>📋 Action Items</h4>
                <ul>
                  {getUsefulTips(analysisResult.ats_score).map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Job Search Section */}
            <div className="job-search-card">
              <h3>🎯 Find Matching Jobs</h3>
              <p>Search for jobs that match your resume profile:</p>
              
              <div className="job-search-form-inline">
                <div className="input-group-with-refresh">
                  <label>Job Keywords:</label>
                  <div className="input-with-button">
                    <input
                      type="text"
                      placeholder="Job keywords"
                      value={keywords}
                      onChange={(e) => setKeywords(e.target.value)}
                      className="input"
                    />
                    <button 
                      className="btn-refresh"
                      onClick={regenerateKeywords}
                      title="Regenerate keywords from resume"
                    >
                      <RefreshCw size={18} />
                    </button>
                  </div>
                  {keywords && (
                    <span className="auto-filled-badge">✨ Auto-generated (click 🔄 to regenerate)</span>
                  )}
                </div>
                
                <div className="input-group">
                  <label>Location:</label>
                  <select
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="select"
                  >
                    <option value="gb">🇬🇧 United Kingdom</option>
                    <option value="de">🇩🇪 Germany</option>
                    <option value="fr">🇫🇷 France</option>
                    <option value="nl">🇳🇱 Netherlands</option>
                    <option value="pl">🇵🇱 Poland</option>
                    <option value="us">🇺🇸 United States</option>
                  </select>
                </div>
                
                <button
                  className="btn btn-primary btn-find-jobs"
                  onClick={findMatchingJobs}
                  disabled={!keywords || loading}
                >
                  {loading ? 'Searching Jobs...' : '🔍 Find Matching Jobs'}
                </button>
              </div>
            </div>

            {/* Feedback Section - Two Columns */}
            <div className="feedback-section">
              <h3>Detailed Analysis</h3>
              <div className="feedback-grid">
                {Object.entries(analysisResult.feedback).map(([category, items]) => (
                  items.length > 0 && category !== 'overall_tips' && (
                    <div key={category} className="feedback-category-card">
                      <h4>
                        {category === 'contact_info' && '📧'}
                        {category === 'sections' && '📑'}
                        {category === 'skills' && '🛠️'}
                        {category === 'formatting' && '📐'}
                        {category === 'achievements' && '🎯'}
                        {category === 'action_verbs' && '⚡'}
                        {' '}
                        {category.replace(/_/g, ' ').toUpperCase()}
                      </h4>
                      <ul>
                        {items.map((item, idx) => (
                          <li key={idx} className={
                            item.startsWith('✓') ? 'feedback-success' :
                            item.startsWith('⚠') ? 'feedback-warning' :
                            'feedback-error'
                          }>
                            <span className="feedback-icon">{getFeedbackIcon(item)}</span>
                            <span className="feedback-text">{item.replace(/^[✓⚠✗]\s*/, '')}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )
                ))}
              </div>
            </div>

            {/* Extracted Information */}
            <div className="parsed-data">
              <h3>📊 Extracted Information</h3>
              <div className="data-grid">
                <div className="data-item">
                  <strong>💼 Skills Found ({analysisResult.parsed_data.skills.length}):</strong>
                  <div className="skills-list">
                    {analysisResult.parsed_data.skills.slice(0, 15).map((skill, idx) => (
                      <span key={idx} className="skill-tag">{skill}</span>
                    ))}
                    {analysisResult.parsed_data.skills.length > 15 && (
                      <span className="skill-tag">+{analysisResult.parsed_data.skills.length - 15} more</span>
                    )}
                  </div>
                </div>
                <div className="data-item">
                  <strong>📧 Email:</strong> 
                  <span className={analysisResult.parsed_data.contact_info.email ? 'text-success' : 'text-error'}>
                    {analysisResult.parsed_data.contact_info.email || '❌ Not found'}
                  </span>
                </div>
                <div className="data-item">
                  <strong>📱 Phone:</strong>
                  <span className={analysisResult.parsed_data.contact_info.phone ? 'text-success' : 'text-error'}>
                    {analysisResult.parsed_data.contact_info.phone || '❌ Not found'}
                  </span>
                </div>
                <div className="data-item">
                  <strong>📝 Word Count:</strong> {analysisResult.parsed_data.word_count} words
                </div>
              </div>
            </div>

            <button className="btn btn-secondary" onClick={reset}>
              ⬅️ Upload New Resume
            </button>
          </div>
        )}

        {/* Jobs Tab */}
        {activeTab === 'jobs' && jobMatches && (
          <div className="jobs-section">
            <div className="jobs-header">
              <h2>Top Job Matches</h2>
              <p>Analyzed {jobMatches.total_jobs_analyzed} jobs • Average match: {jobMatches.average_score}%</p>
            </div>

            <div className="jobs-grid">
              {jobMatches.matches.map((match, idx) => (
                <div key={idx} className="job-card">
                  <div className="job-header">
                    <h3>{match.job.title}</h3>
                    <div
                      className="match-score"
                      style={{ backgroundColor: getScoreColor(match.match_score) }}
                    >
                      {match.match_score}%
                    </div>
                  </div>
                  <p className="job-company">{match.job.company}</p>
                  <p className="job-location">📍 {match.job.location}</p>
                  <p className="match-grade">{match.match_grade}</p>
                  {match.job.salary_min && (
                    <p className="job-salary">
                      💰 {match.job.salary_min.toLocaleString()} - {match.job.salary_max.toLocaleString()}
                    </p>
                  )}
                  <p className="job-description">
                    {match.job.description.substring(0, 150)}...
                  </p>
                  <a
                    href={match.job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary btn-small"
                  >
                    Apply Now
                  </a>
                </div>
              ))}
            </div>

            <button className="btn btn-secondary" onClick={reset}>
              Search Again
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Built with FastAPI + React • AI-powered resume analysis</p>
      </footer>
    </div>
  );
}

export default App;