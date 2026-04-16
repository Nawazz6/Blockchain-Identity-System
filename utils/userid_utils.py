import random
import string

def generate_user_id():
    digits = ''.join(random.choices(string.digits, k=6))
    return f"UID-{digits}"