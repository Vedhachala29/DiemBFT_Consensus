import nacl.encoding
import nacl.hash
from nacl.bindings.utils import sodium_memcmp
from util import get_hash
from block_tree import Vote_Info, VoteMsg, LedgerCommitInfo
import pickle
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from messages import TimeoutInfo
import logging

class Safety:
    def __init__(self, modules_map, private_key, public_keys, highest_qc_round, highest_vote_round):
        logging.info("Initializing Safety")
        self.modules_map = modules_map      # map of all the modules of the validator
        self.__private_key = private_key    # own private key of the validator
        self.__public_keys = public_keys    # public keys of all the validators
        self.__highest_qc_round = highest_qc_round
        self.__highest_vote_round = highest_vote_round
        logging.info("Private and public keys intialized")
        self.hasher = nacl.hash.sha256

    #Method to update __highest_vote_round for fault injection module
    def set_highest_qc_round(self,round):
        self.__highest_vote_round = round

    def __increase_highest_vote_round(self, round):
        # commit not to vote in rounds lower than round
        logging.info("Maximizing the highest vote round")
        logging.info(f"round: {round}, highest_vote_round:{self.__highest_vote_round}")
        self.__highest_vote_round = max(round, self.__highest_vote_round)

    def __update_highest_qc_round(self, qc_round):
        logging.info("Updating highest qc round")
        self.__highest_qc_round = max(qc_round, self.__highest_qc_round)

    def __consecutive(self, block_round, round):
        return round + 1 == block_round

    def __safe_to_extend(self, block_round, qc_round, tc):
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
        return tc is not None and self.__consecutive(round, qc_round) or self.__consecutive(round, tc.round)

    def __commit_state_id_candidate(self, block_round, qc):
        # find the committed id in case a qc is formed in the vote round
        if qc is not None and self.__consecutive(block_round, qc.vote_info.round) and qc.vote_info.round >= 0:
            return qc.vote_info.round 
        else:
            return None  #TODO check this symbol

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
            logging.error(f"Bad Signature, sender : {sender}, signed message: {signed_obj}")
            return False


    def valid_signatures(self, qc, tc):
        validity = True
        #dont check for genesis validity
        if qc is None or tc is None or qc.vote_info.round == -1 or tc.round == -1: 
            return validity
        #Validate signature of qc author
        validity = validity and self.verify_msg_signature(qc.author_signature,qc.author)
        #Validate signature for each of the signature in qc's quorum of signatures
        for qc_sign in qc.signatures:
            validity = validity and self.verify_msg_signature(qc_sign[1],qc_sign[0])
        logging.info(f"Validity of signatures in qc verified to be {validity}")

        for tmo_sign in tc.tmo_signatures:
            validity = validity and self.verify_msg_signature(tmo_sign[1],tmo_sign[0])

        logging.info(f"Validity of signatures in tc verified to be {validity}")
        return validity  

    def make_vote(self, b, last_tc):
        qc_round = b.qc.vote_info.round if b.qc else -1
        if b is not None and self.valid_signatures(b.qc, last_tc) and self.__safe_to_vote(b.round, qc_round, last_tc):
            self.__update_highest_qc_round(qc_round)  # Protect qc round
            self.__increase_highest_vote_round(b.round) # Don’t vote again in this (or lower) round
            # VoteInfo carries the potential QC info with ids and rounds of the parent QC
            vote_info = Vote_Info(b.id, b.round, None if not(b.qc) else b.qc.vote_info.id, qc_round)
            ledger_commit_info = LedgerCommitInfo(self.__commit_state_id_candidate(b.round, b.qc),get_hash(vote_info))
            signature = self.sign_message(ledger_commit_info)
            return VoteMsg(vote_info, ledger_commit_info, self.modules_map['block_tree'].high_commit_qc,self.modules_map['config']["id"], signature )
        return None

    def make_timeout(self, round, high_qc, last_tc):
        qc_round = high_qc.vote_info.round if high_qc is not None else -1
        if self.valid_signatures(high_qc, last_tc) and self.__safe_to_timeout(round, qc_round, last_tc):
            self.__increase_highest_vote_round(round)  # Stop voting for round
            return TimeoutInfo(round, high_qc, self.modules_map["config"]["id"],(self.modules_map["config"]["id"], self.sign_message({"round": round, "high_qc_round": high_qc.vote_info.round})))
        return None  # TODO
