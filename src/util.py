from nacl.signing import SigningKey


def get_signing_key_objects(n):
    return [SigningKey.generate() for _ in range(n)]
