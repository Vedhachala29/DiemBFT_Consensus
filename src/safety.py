import nacl.encoding
import nacl.hash
from nacl.bindings.utils import sodium_memcmp
from block_tree import Vote_Info, VoteMsg, LedgerCommitInfo
import pickle
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


def obj_to_string(obj, extra='    '):
    return str(obj.__class__) + '\n' + '\n'.join(
        (extra + (str(item) + ' = ' +
                  (obj_to_string(obj.__dict__[item], extra + '    ') if hasattr(obj.__dict__[item], '__dict__') else str(
                      obj.__dict__[item])))
         for item in sorted(obj.__dict__)))
class Safety:
    def __init__(self, modules_map, private_key, public_keys, highest_qc_round, highest_vote_round):
        self.modules_map = modules_map  # map of all the modules of the validator
        self.__private_key = private_key  # own private key of the validator
        self.__public_keys = public_keys  # public keys of all the validators
        self.__highest_qc_round = highest_qc_round
        self.__highest_vote_round = highest_vote_round
        self.hasher = nacl.hash.sha256

    def __increase_highest_vote_round(self, round):
        # commit not to vote in rounds lower than round
        self.__highest_vote_round = max(round, self.__highest_vote_round)

    def __update_highest_qc_round(self, qc_round):
        self.__highest_qc_round = max(qc_round, self.__highest_qc_round)

    def __consecutive(self, block_round, round):
        return round + 1 == block_round

    def __safe_to_extend(self, block_round, qc_round, tc):
        # TODO align the code after deciding tc structure
        return self.__consecutive(block_round, tc.round) and (qc_round >= max(tc.tmo_high_qc_rounds))

    def __safe_to_vote(self, block_round, qc_round, tc):
        if block_round <= max(self.__highest_vote_round, qc_round):
            # 1. must vote in monotonically increasing rounds
            # 2. must extend a smaller round
            return False

        # Extending qc from previous round or safe to extend due to tc
        return self.__consecutive(block_round, qc_round) or self.__safe_to_extend(block_round, qc_round, tc)

    def __safe_to_timeout(self, round, qc_round, tc):
        if (qc_round < self.__highest_qc_round) or (round <= max(self.__highest_vote_round-1, qc_round)):
            # respect highest qc round and don’t timeout in a past round
            return False

        # qc or tc must allow entering the round to timeout
        return self.__consecutive(round, qc_round) or self.__consecutive(round, tc.round)

    def __commit_state_id_candidate(self, block_round, qc):
        # find the committed id in case a qc is formed in the vote round
        if self.__consecutive(block_round, qc.vote_info.round) and qc.vote_info.round >= 0:
            # print('cs cand id ', self.modules_map['config']['id'], obj_to_string(qc))
            # return self.modules_map['ledger'].pending_state(qc.id)  # TODO qc structure and align with it 
            return qc.vote_info.round 
        else:
            return None  #TODO check this symbol

    def encode_message(self, msg):
        encoded_msg_obj = {
            'digest': self.hasher(msg, encoder=nacl.encoding.HexEncoder),
            'encoded_msg': nacl.encoding.HexEncoder.encode(msg)
        }
        return encoded_msg_obj

    def validate_message_integrity(self, msg_obj):
        msg = nacl.encoding.HexEncoder.decode(msg_obj)['encoded_msg']
        dgst = self.hasher(msg, encoder=nacl.encoding.HexEncoder)
        return sodium_memcmp(dgst, msg_obj['digest'])

    def sign_message(self, msg_obj):
        serialized_msg = pickle.dumps(msg_obj)
        return self.__private_key.sign(serialized_msg)

    def verify_msg_signature(self, signed_obj, sender):
        try:
            verify_key_bytes = self.__public_keys[sender]
            verify_key = VerifyKey(verify_key_bytes)
            verify_key.verify(signed_obj)
            return True
        except BadSignatureError:
            print("Bad Signature")
            return False


    def valid_signatures(self, block, tc):
        validity = True
        #dont check for genesis validity
        if block.qc.vote_info.round == -1: 
            return validity
        qc = block.qc
        #Validate signature of qc author
        validity = validity and self.verify_msg_signature(qc.author_signature,qc.author)
        #Validate signature for each of the signature in qc's quorum of signatures
        for qc_sign in qc.signatures:
            validity = validity and self.verify_msg_signature(qc_sign[1],qc_sign[0])
        return validity  

    def make_vote(self, b, last_tc):
        qc_round = b.qc.vote_info.round
        #print("in makeout", qc_round)
        if self.valid_signatures(b, last_tc) and self.__safe_to_vote(b.round, qc_round, last_tc):
            self.__update_highest_qc_round(qc_round)  # Protect qc round
            #print("in makeout voteinfo for loop")
            self.__increase_highest_vote_round(b.round) # Don’t vote again in this (or lower) round
            # VoteInfo carries the potential QC info with ids and rounds of the parent QC
            vote_info = Vote_Info(b.id, b.round, None if not(b.qc) else b.qc.vote_info.id, qc_round)
            #print("in makeout voteinfo", obj_to_string(vote_info))
            ledger_commit_info = LedgerCommitInfo(self.__commit_state_id_candidate(b.round, b.qc))  # TODO
            #print("in makeout lcinfo", obj_to_string(vote_info))
            signature = self.sign_message(ledger_commit_info)
            return VoteMsg(vote_info, ledger_commit_info, self.modules_map['block_tree'].high_commit_qc,self.modules_map['config']["id"], signature )  # TODO
        return None

    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round
        if self.valid_signatures(high_qc, last_tc) and self.__safe_to_timeout(round, qc_round, last_tc):
            self.__increase_highest_vote_round(round)  # Stop voting for round
            return TimeoutInfo(round, high_qc)  # TODO
        return "⊥"  # TODO
