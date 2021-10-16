from nacl.signing import SigningKey
import nacl.hash
import pickle

HASHER = nacl.hash.sha256


def get_signing_key_objects(n):
    return [SigningKey.generate() for _ in range(n)]


def get_hash(obj):
    serialized_obj = pickle.dumps(obj)
    return HASHER(serialized_obj, encoder=nacl.encoding.HexEncoder)
