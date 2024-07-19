import secrets

secret_key = secrets.token_hex(16)  # Generates a 32-character hexadec token
print(secret_key)
