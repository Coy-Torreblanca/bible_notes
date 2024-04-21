import secrets


def generate_random_id():

    return secrets.token_hex(8)
