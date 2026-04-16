from cryptography.fernet import Fernet
import os
from config import FERNET_KEY_FILE

def load_or_create_key():
    if not os.path.exists(FERNET_KEY_FILE):
        key = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as key_file:
            key_file.write(key)
    else:
        with open(FERNET_KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

def encrypt_file(input_file_path, output_file_path):
    key = load_or_create_key()
    fernet = Fernet(key)

    with open(input_file_path, "rb") as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    with open(output_file_path, "wb") as enc_file:
        enc_file.write(encrypted_data)