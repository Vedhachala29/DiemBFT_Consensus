import nacl.hash
from collections import defaultdict
from util import get_hash
import logging
from constants import *

class Vote_Info:
    def __init__(self, id = -1, round = -1, parent_id = None,parent_round = None):
        self.id = id                                # ID of the current block
        self.round = round                          # Round number of the current block
        self.parent_id = parent_id                  # ID of the parent block
        self.parent_round = parent_round            # Round number of the parent block

    def __hash__(self):
        return hash((self.id,self.round,self.parent_id,self.parent_round))

class QC:
    def __init__(self, vote_info = Vote_Info(), ledger_commit_info = None, signatures = None, author = None, author_signature = None):
        self.vote_info = vote_info                      
        self.ledger_commit_info = ledger_commit_info    
        self.signatures = signatures                    # A quorum of signatures
        self.author = author                            # Validator that produced the qc
        self.author_signature = author_signature        # Signature of the author 
        self.parent_id = None                           

class Block:
    def __init__(self, id, config, txns, round, qc=QC()) -> None:
        self.author = 0             # The author of the block. Initialized later in process_new_round_event
        self.round = round          # The round that generated this proposal
        self.payload = txns         # Proposed transactions
        self.qc = qc                # QC for parent block
        self.children = []           
        self.id = id                # A unique digest of author, round, payload, qc:vote info:id and qc:signatures
        self.parent_id = None       
        self.pending_commit = True  

class LedgerCommitInfo:
    def __init__(self, id, vote_info_hash) -> None:
        self.commit_state_id = id
        self.vote_info_hash = vote_info_hash

    def __hash__(self):
        return hash((self.commit_state_id,self.vote_info_hash))

class VoteMsg:
    def __init__(self, vote_info, ledger_commit_info, high_commit_qc,sender, signature) -> None:
        self.vote_info = vote_info                      # A VoteInfo record
        self.ledger_commit_info = ledger_commit_info    # Speculated ledger info
        self.high_commit_qc = high_commit_qc            # QC to synchronize on committed blocks
        self.sender = sender                            
        self.signature = signature                      

class BlockTree:
    def __init__(self, modules) -> None:
        self.pending_block_tree = []                    # Tree of blocks pending commitment
        self.pending_votes = defaultdict(set)
        self.high_qc = QC()                                 # Highest known QC
        self.high_commit_qc = None                          # Highest QC that serves as a commit certificate
        self.modules = modules
        self.root = Block(-1, 0, None, None) # genesis Block
        self.root.children = self.pending_block_tree
        self.prev_block_id = None

    def __prune(self, id):
        """
        prunes all the nodes from the given block id to all its parent node
        it keeps pruning until we prune all the commited blocks after ledger commits the blocks
        """
        while id:
            block_to_prune = self.find_block(self.pending_block_tree, id)
            id = None
            if block_to_prune:
                if not block_to_prune.pending_commit:
                    break
                block_to_prune.pending_commit = False
                id = block_to_prune.parent_id
                block_to_prune = None

    def __add(self,block):
        """
        adds a children to high qc block
        find block method will get the high qc by searching the pending block tree
        """
        blockid = self.high_qc.vote_info.id
        self.prev_block_id = block.id
        parent_block = self.find_block(self.pending_block_tree, blockid)
        if not parent_block:
            self.pending_block_tree.append(block)
        else:
            block.parent_id = parent_block.id
            parent_block.children.append(block)

    def process_qc(self, qc):
        """
        commits only if ledger commit info is present and qc is more than high commit qc
        else it just updates the high qc
        """
        if qc and qc.ledger_commit_info  and qc.ledger_commit_info.commit_state_id != None and ((not self.high_commit_qc) or qc.vote_info.round > self.high_commit_qc.vote_info.round) : 
            self.modules[LEDGER].commit(qc.vote_info.parent_id)           #   Ledger.commit
            self.__prune(qc.vote_info.parent_id)                            #   Prunes the Block Tree
            validator_id = self.modules[CONFIG][ID]
            current_round = self.modules[PACEMAKER].current_round
            logging.info(f"{VALIDATOR} {validator_id} committing bid {qc.vote_info.parent_id}, txns : {self.modules['latest_committed_payload']}")
            self.high_commit_qc = qc                                        #  Updates the high commit qc
        if qc and self.high_qc and qc.vote_info.round > self.high_qc.vote_info.round: 
            self.high_qc = qc      

    def execute_and_insert(self, b):
        self.modules[LEDGER].speculate(self.prev_block_id, b.id, b.payload)  # updates the ledger speculated states
        self.__add(b)                                                          # adds to the pending block tree

    def process_vote(self, vote):
        """
        Processes Vote messages 
        checks signatures
        tries to form a qc and return qc when there is a quorum
        """
        self.process_qc(vote.high_commit_qc)
        vote_idx = get_hash(vote.ledger_commit_info)
        self.pending_votes[vote_idx].add((vote.sender, vote.signature))
        if len(self.pending_votes[vote_idx]) == len(self.modules['validators_list']) - self.modules['config']['nfaulty'] :
            author_sign = self.modules['safety'].sign_message(self.pending_votes[vote_idx])
            qc = QC(vote.vote_info, vote.ledger_commit_info, self.pending_votes[vote_idx], self.modules['config']['id'], author_sign)
            del self.pending_votes[vote_idx]
            return qc
        return None
    
    def find_block(self, blocks, id):
        """
        Searches and returns the block in the pending block tree
        """
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
        block_id = get_hash((config[ID], current_round, txns, self.high_qc.vote_info.id, self.high_qc.signatures))
        return Block(block_id, config, txns, current_round, self.high_qc)
