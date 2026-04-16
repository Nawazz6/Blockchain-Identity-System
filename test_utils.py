from utils.otp_utils import generate_otp
from utils.userid_utils import generate_user_id
from utils.hash_utils import generate_sha256
from utils.encryption_utils import load_or_create_key
import os

print("Testing OTP:", generate_otp())
print("Testing User ID:", generate_user_id())

key = load_or_create_key()
print("Fernet key created successfully.")

if os.path.exists("secret.key"):
    print("secret.key file exists.")
else:
    print("secret.key file not found.")