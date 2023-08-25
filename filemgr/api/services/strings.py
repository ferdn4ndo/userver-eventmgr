import base64
import random
import re
import string
from typing import List


def break_string_into_words(original_str: str) -> List:
    name = original_str.upper().replace(" ", "_")
    return re.sub("_+", "_", name).split("_")


def generate_random_encoded_string() -> str:
    """ Generate a random string of letters and digits and special characters and base64 encode it """
    password_characters = string.ascii_letters + string.digits
    generated_key = ''.join(random.choice(password_characters) for i in range(32))
    return str(base64.urlsafe_b64encode(generated_key.encode('utf-8')).decode('utf-8'))
