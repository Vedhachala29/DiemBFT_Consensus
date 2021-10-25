from util import get_hash
import pickle


class Vote_Info:
    def __init__(self, id = -1, round = -1, parent_id = None,parent_round = None):
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round

    def __hash__(self):
        return hash((self.id,self.round,self.parent_id,self.parent_round))

vote_info = Vote_Info(1,'1',1,1)
# print(get_hash(pickle.dumps(vote_info)))
# vote_info2 = Vote_Info(1,1,1,1)
# vote_info3 = Vote_Info(1,1,1,4)


# print(pickle.dumps(vote_info))
# print(pickle.dumps(vote_info2))
# print(pickle.dumps(vote_info3))
# print(pickle.dumps(vote_info) == pickle.dumps(vote_info3))
# print(hash(vote_info))
# print(hash(vote_info2))
# print(hash(vote_info3))

from nacl.signing import SigningKey

signing_key = SigningKey.generate()

# Sign a message with the signing key
signed = signing_key.sign(pickle.dumps(vote_info))

# Obtain the verify key for a given signing key
verify_key = signing_key.verify_key

# Serialize the verify key to send it to a third party
verify_key_bytes = verify_key.encode()

from nacl.signing import VerifyKey

# Create a VerifyKey object from a hex serialized public key
verify_key = VerifyKey(verify_key_bytes)

# Check the validity of a message's signature
# The message and the signature can either be passed together, or
# separately if the signature is decoded to raw bytes.
# These are equivalent:
print(verify_key.verify(signed))
verify_key.verify(signed.message, signed.signature)
# print(pickle.loads(signed.message))
# print(signed.signature)