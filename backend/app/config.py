import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directorio base del proyecto (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Credenciales y URL de la API
API_KEY  = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/"

# Rutas de archivos de datos
RAW_PATH    = str(DATA_DIR / "outages_raw.parquet")
CLEAN_PATH  = str(DATA_DIR / "outages_clean.parquet")
STATS_PATH  = str(DATA_DIR / "outage_stats.parquet")

# Configuración HTTP
REQUEST_TIMEOUT = 10
MAX_RETRIES     = 3
PAGE_SIZE       = 5000

# ── Supabase (almacenamiento en la nube) ───────────────────
# Si estas variables existen, el sistema usa Supabase
# Si no existen, usa archivos locales
SUPABASE_URL    = os.getenv("SUPABASE_URL")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "parquet-data"

# True si estamos en la nube, False si estamos local
USE_CLOUD = bool(SUPABASE_URL and SUPABASE_KEY)
