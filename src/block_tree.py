from pickle import NONE
import nacl.hash
from collections import defaultdict
from typing import DefaultDict
from util import get_hash

def obj_to_string(obj, extra='    '):
    return str(obj.__class__) + '\n' + '\n'.join(
        (extra + (str(item) + ' = ' +
                  (obj_to_string(obj.__dict__[item], extra + '    ') if hasattr(obj.__dict__[item], '__dict__') else str(
                      obj.__dict__[item])))
         for item in sorted(obj.__dict__)))

class Vote_Info:
    def __init__(self, id = -1, round = -1, parent_id = None,parent_round = None):
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round

    def __hash__(self):
        return hash((self.id,self.round,self.parent_id,self.parent_round))

class QC:
    def __init__(self, vote_info = Vote_Info(), ledger_commit_info = None, signatures = None, author = None, author_signature = None):
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures
        self.author = author
        self.author_signature = author_signature
        self.parent_id = None

class Block:
    def __init__(self, id, config, txns, round, qc=QC()) -> None:
        self.author = 0
        self.round = round
        self.payload = txns
        self.qc = qc
        self.children = []
        self.id = id
        self.parent_id = None
        self.pending_commit = True

class LedgerCommitInfo:
    def __init__(self, id) -> None:
        self.commit_state_id = id
        self.vote_info_hash = None

    def __hash__(self):
        return hash((self.commit_state_id,self.vote_info_hash))

class VoteMsg:
    def __init__(self, vote_info, ledger_commit_info, high_commit_qc,sender, signature) -> None:
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.high_commit_qc = high_commit_qc
        self.sender = sender
        self.signature = signature

class BlockTree:
    def __init__(self, modules) -> None:
        self.pending_block_tree = []
        self.pending_votes = defaultdict(set)
        self.high_qc = QC()
        self.high_commit_qc = None
        self.modules = modules
        self.root = Block(-1, 0, None, None) # genesis Block
        self.root.children = self.pending_block_tree
        self.pending_transactions = []

    def __prune(self, id):
        txns_to_commit = []
        # print("in prune ", id)
        while id:
            block_to_prune = self.find_block(self.pending_block_tree, id)
            id = None
            if block_to_prune:
                c_payload = block_to_prune.payload
                if c_payload and c_payload[0] == "dummy":
                    break
                txns_to_commit.append(block_to_prune.payload)
                block_to_prune.pending_commit = False
                id = block_to_prune.parent_id
                block_to_prune = None
        # print(" txns_to_commit ", txns_to_commit)
        return txns_to_commit

    def __add(self,block):
        blockid = self.high_qc.vote_info.id
        parent_block = self.find_block(self.pending_block_tree, blockid)
        if not parent_block:
            self.pending_block_tree.append(block)
        else:
            block.parent_id = parent_block.id
            parent_block.children.append(block)
        # print("After add", parent_block)
        # print(" Pending Tree", self.pending_transactions)
        # print(" Pending Tree res", self.find_block(self.pending_block_tree, block.id))

    # def get_pending_transactions(self):
    #     if not self.pending_block_tree:
    #         return []
    #     elif not self.pending_block_tree.child:
    #         return self.pending_block_tree.payload
    #     else:
    #         return self.pending_block_tree.child.payload

    def process_qc(self, qc):
        if qc and qc.ledger_commit_info  and qc.ledger_commit_info.commit_state_id != None and ((not self.high_commit_qc) or qc.vote_info.round > self.high_commit_qc.vote_info.round) :
            txns_to_commit = self.__prune(qc.vote_info.parent_id)
            print("validator", self.modules["config"]["id"] , " committing bid ", qc.vote_info.parent_id,txns_to_commit, " in ", self.modules["pace_maker"].current_round , " round")

            txns_to_commit = self.__prune(qc.vote_info.parent_id)
            for txn in txns_to_commit:
                self.modules["ledger"].commit(txn)
            self.high_commit_qc = qc
        if qc and self.high_qc and qc.vote_info.round > self.high_qc.vote_info.round: 
            self.high_qc = qc      

    def execute_and_insert(self, b):
        self.__add(b)

    def process_vote(self, vote):
        self.process_qc(vote.high_commit_qc)
        vote_idx = get_hash(vote.ledger_commit_info)
        self.pending_votes[vote_idx].add((vote.sender, vote.signature))
        if len(self.pending_votes[vote_idx]) == len(self.modules["validators_list"]) - self.modules['config']['nfaulty']:
            author_sign = self.modules['safety'].sign_message(self.pending_votes[vote_idx])
            qc = QC(vote.vote_info, vote.ledger_commit_info, self.pending_votes[vote_idx], self.modules['config']['id'], author_sign)
            return qc
        return None
    
    def find_block(self, blocks, id):
        found_block = None
        found_block_in_childs = None
        for block in blocks:
            if block is None:
                continue
            if block.id == id:
                found_block = block
                break
            if (not found_block) and block.children and len(block.children) > 0:
                found_block_in_childs = self.find_block(block.children, id)
                if found_block_in_childs:
                    found_block = found_block_in_childs
                    break
        return found_block

    def get_pending_txns(blocks):
        result = []
        for block in blocks:
            if block.pending_commit:
                result.append(block.payload)
            if block.children and len(block.children) > 0:
                child_pending = get_pending_txns(block.children)
                if child_pending and len(child_pending) > 0:
                    result.extend(child_pending)
        return result  

    def generate_block(self, config, txns, current_round):
        block_id = get_hash((config['id'], current_round, txns, self.high_qc.vote_info.id, self.high_qc.signatures))
        return Block(block_id, config, txns, current_round, self.high_qc)
