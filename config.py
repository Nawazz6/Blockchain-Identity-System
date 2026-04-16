import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(BASE_DIR, "database", "identity.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ENCRYPTED_FOLDER = os.path.join(BASE_DIR, "encrypted_files")
SECRET_KEY = "supersecretkey"

GANACHE_URL = "https://sepolia.infura.io/v3/c8616fcbc9ab41119770f2f7b6a0c0d7"
ABI_PATH = os.path.join(BASE_DIR, "blockchain", "abi.json")
CONTRACT_INFO_PATH = os.path.join(BASE_DIR, "blockchain", "contract_info.json")
FERNET_KEY_FILE = os.path.join(BASE_DIR, "secret.key")