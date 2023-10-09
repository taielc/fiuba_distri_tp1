"""General client config."""
from typing import Optional
from pathlib import Path

from paths import ROOT_DIR
from config import DATASET_SIZE

from .utils import build_itineraries_file

DATA_DIR = ROOT_DIR / ".data"
AIRPORTS_FILE = DATA_DIR / "airports-codepublic.csv"
FULL_ITINERARIES_FILE = DATA_DIR / "itineraries.csv"

ITINERARIES_FILE = build_itineraries_file(
    DATASET_SIZE,
    FULL_ITINERARIES_FILE,
    DATA_DIR,
)

READ_BUFFER_SIZE = 1024
