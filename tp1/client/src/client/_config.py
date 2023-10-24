"""General client config."""
from paths import ROOT_DIR

DATA_DIR = ROOT_DIR / ".data"
AIRPORTS_FILE = DATA_DIR / "airports-codepublic.csv"
ITINERARIES_FILE = DATA_DIR / "itineraries.csv"

READ_BUFFER_SIZE = 1024
