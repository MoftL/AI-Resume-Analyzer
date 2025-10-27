import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils.job_fetcher import JobFetcher

fetcher = JobFetcher()

# Now defaults to UK (Europe)
results = fetcher.search_jobs("python developer")  # Automatically searches UK

# Or specify any European country
results = fetcher.search_jobs("react developer", location="de")  # Germany