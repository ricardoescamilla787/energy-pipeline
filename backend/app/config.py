import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/"

DATA_PATH = os.getenv("DATA_PATH", "data/outages.parquet")

REQUEST_TIMEOUT = 10
MAX_RETRIES = 2
PAGE_SIZE = 5000
