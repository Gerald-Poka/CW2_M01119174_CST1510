from pathlib import Path

# ROOT OF ENTIRE PROJECT (anchor point)
BASE_DIR = Path(__file__).resolve().parent

# DATA folder (same level as configpath.py)
DATA_DIR = BASE_DIR / "DATA"

# DATABASE
DB_FILE = DATA_DIR / "project_data.db"

# FILES
USERS_FILE = DATA_DIR / "users.txt"
CYBER_INCIDENTS_FILE = DATA_DIR / "cyber_incidents.csv"
DATASETS_METADATA_FILE = DATA_DIR / "datasets_metadata.csv"
IT_TICKETS_FILE = DATA_DIR / "it_tickets.csv"

print("DATA_DIR ACTUAL:", DATA_DIR)
print("IT TICKETS PATH:", IT_TICKETS_FILE)