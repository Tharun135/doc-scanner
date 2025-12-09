# Additional optimization: HTTP connection pooling for Ollama requests
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Create a session with connection pooling
session = requests.Session()
retry_strategy = Retry(
    total=2,
    backoff_factor=0.1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=retry_strategy
)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Use this session instead of requests.post() directly
# response = session.post(ollama_url, json=payload, timeout=0.5)
