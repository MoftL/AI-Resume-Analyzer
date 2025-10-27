import os
import requests
from dotenv import load_dotenv

load_dotenv()

class JobFetcher:
    def __init__(self):
        """
        Initializes the JobFetcher with Adzuna API credentials.
        """
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"

        if not self.app_id or not self.app_key:
            raise ValueError("Adzuna API credentials are not set in environment variables.")
    
    def search_jobs(self, keywords, location="gb", results_per_page=10, page=1):
        """
        Search for jobs by keywords
        
        Parameters:
        -----------
        keywords : str
            Job title or skills to search for
            Examples: "python developer", "data scientist", "react engineer"
        
        location : str
            Country code (us, gb, de, fr, nl, pl, etc.)
            European codes: gb=UK, de=Germany, fr=France, nl=Netherlands
        
        results_per_page : int
            Number of jobs to return (max 50)
        
        page : int
            Page number for pagination (get more results)
        
        Returns:
        --------
        dict with structure:
        {
            'success': bool,
            'count': int (jobs returned),
            'total_results': int (total available),
            'jobs': [
                {
                    'title': str,
                    'company': str,
                    'location': str,
                    'description': str,
                    'salary_min': float or None,
                    'salary_max': float or None,
                    'contract_type': str,
                    'url': str (application link),
                    'created': str (date posted)
                }
            ],
            'error': str (only if success=False)
        }
        
        How it works:
        -------------
        1. Builds API URL: https://api.adzuna.com/v1/api/jobs/{country}/search/{page}
        2. Adds your credentials and search parameters
        3. Makes HTTP GET request
        4. Parses JSON response
        5. Extracts relevant job fields
        6. Returns clean, structured data
        """
        
        # Build the endpoint URL
        url = f"{self.base_url}/{location}/search/{page}"
        
        # Prepare query parameters
        params = {
            'app_id': self.app_id,
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': results_per_page,
            'what': keywords,  # "what" parameter = job title/keywords
            'content-type': 'application/json'
        }
        
        try:
            # Make the API request with 10 second timeout
            response = requests.get(url, params=params, timeout=10)
            
            # Check if request was successful (HTTP 200 OK)
            if response.status_code == 200:
                data = response.json()
                
                # Extract and structure job listings
                jobs = []
                for result in data.get('results', []):
                    # Parse each job posting
                    job = {
                        'title': result.get('title', 'N/A'),
                        'company': result.get('company', {}).get('display_name', 'N/A'),
                        'location': result.get('location', {}).get('display_name', 'N/A'),
                        'description': result.get('description', 'N/A'),
                        'salary_min': result.get('salary_min'),
                        'salary_max': result.get('salary_max'),
                        'contract_type': result.get('contract_type', 'N/A'),
                        'url': result.get('redirect_url', 'N/A'),
                        'created': result.get('created', 'N/A')
                    }
                    jobs.append(job)
                
                return {
                    'success': True,
                    'count': len(jobs),
                    'jobs': jobs,
                    'total_results': data.get('count', 0)  # Total jobs available
                }
            
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Invalid API credentials. Check your .env file',
                    'jobs': []
                }
            
            elif response.status_code == 429:
                return {
                    'success': False,
                    'error': 'Rate limit exceeded. Try again later',
                    'jobs': []
                }
            
            else:
                return {
                    'success': False,
                    'error': f"API returned status code {response.status_code}",
                    'jobs': []
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timed out. Check your internet connection',
                'jobs': []
            }
        
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection error. Check your internet connection',
                'jobs': []
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'jobs': []
            }
    
    def get_jobs_by_category(self,category,location='us',results_per_page=10):
        """
        Get jobs by predefined category instead of keywords
        
        Parameters:
        -----------
        category : str
            Job category from Adzuna's list
            Examples: "it-jobs", "engineering-jobs", "healthcare-nursing-jobs"
            Full list: https://developer.adzuna.com/docs/search
        
        location : str
            Country code
        
        results_per_page : int
            Number of results
        
        Returns:
        --------
        Same format as search_jobs()
        """
        url=f"{self.base_url}/{location}/serarch/1"

        params={
            'app_id': self.app_id,
            'app_key': self.app_key,
            'category': category,
            'results_per_page': results_per_page,
        }

        try:
            response=requests.get(url,params=params,timeout=10)

            if response.status_code==200:
                data=response.json()
                jobs=[
                    {
                        'title': job.get('title','N/A'),
                        'company': job.get('company',{}).get('display_name','N/A'),
                        'location': job.get('location',{}).get('display_name','N/A'),
                        'description': job.get('description','N/A'),
                        'url': job.get('redirect_url','N/A'),
                    }
                    for job in data.get('results',[])
                ]
                return{
                    'success':True,
                    'count':len(jobs),
                    'jobs':jobs,
                }
            else:
                return{
                    'success':False,
                    'error':f"API returned status code {response.status_code}",
                    'jobs':[]
                }
        except requests.exceptions.RequestException as e:
            return{
                'success':False,
                'error':f"Request failed: {str(e)}",
                'jobs':[]
            }
    
    def search_multiple_locations(self,keywords,locations,results_per_location=5):
        """
        Search across multiple countries at once
        
        Parameters:
        -----------
        keywords : str
            Search keywords
        
        locations : list
            List of country codes, e.g. ['gb', 'de', 'fr']
        
        results_per_location : int
            Jobs to fetch per country
        
        Returns:
        --------
        dict with jobs grouped by country:
        {
            'success': True,
            'results_by_country': {
                'gb': {'jobs': [...], 'count': 5},
                'de': {'jobs': [...], 'count': 5}
            }
        }
        """
        results_by_country={}

        for location in locations:
            result=self.search_jobs(keywords,location=location,results_per_page=results_per_location)
            results_by_country[location]={
                'jobs': result.get('jobs',[]),
                'count': result.get('count',0),
                'success': result.get('success',False)
            }
        return {
            'success': True,
            'results_by_country': results_by_country
        }