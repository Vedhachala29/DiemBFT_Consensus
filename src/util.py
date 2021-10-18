from nacl.signing import SigningKey
import nacl.hash
import pickle

HASHER = nacl.hash.sha256


def get_signing_key_objects(n):
    return [SigningKey.generate() for _ in range(n)]


def get_hash(obj):
    serialized_obj = pickle.dumps(obj)
    return HASHER(serialized_obj, encoder=nacl.encoding.HexEncoder)

def obj_to_string(obj, extra='    '):
    return str(obj.__class__) + '\n' + '\n'.join(
        (extra + (str(item) + ' = ' +
                  (obj_to_string(obj.__dict__[item], extra + '    ') if hasattr(obj.__dict__[item], '__dict__') else str(
                      obj.__dict__[item])))
         for item in sorted(obj.__dict__)))
