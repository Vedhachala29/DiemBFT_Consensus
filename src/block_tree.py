
import nacl.hash
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

class QC:
    def __init__(self, vote_info = Vote_Info(), ledger_commit_info = None, signatures = None, author = None, author_signatures = None):
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures
        self.author = author
        self.author_signatures = author_signatures
        self.parent_id = None

class Block:
    def __init__(self, config, txns, round, qc=QC()) -> None:
        self.author = 0
        self.round = round
        self.payload = txns
        self.qc = qc
        self.child = None
        self.id = 'B' + str(round)

class LedgerCommitInfo:
    def __init__(self, id) -> None:
        self.commit_state_id = id
        self.vote_info_hash = None

class VoteMsg:
    def __init__(self, vote_info, ledger_commit_info, high_commit_qc,sender, signature) -> None:
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.high_commit_qc = high_commit_qc
        self.sender = sender
        self.signature = None # have to implement the signature

class BlockTree:
    def __init__(self, modules) -> None:
        self.pending_block_tree = None
        self.pending_votes = {}
        self.high_qc = QC()
        self.high_commit_qc = None
        self.modules = modules
        self.root = Block(-1, 0, None, None) # genesis Block
        self.root.child = self.pending_block_tree

    def __prune(self, id):
        self.pending_block_tree = None
    def __add(self,block):
        if(self.pending_block_tree != None):
            self.pending_block_tree.child = block
        else:
            self.pending_block_tree = block

    def process_qc(self, qc):
        if qc != None and qc.ledger_commit_info != None and qc.ledger_commit_info.commit_state_id != None:
            self.modules.Ledger.commit(qc.vote_info.parent_id)
            self.__prune(qc.vote_info.parent_id)
            self.high_commit_qc = max(qc.vote_info.id, self.high_commit_qc)
        if qc and qc.vote_info.round > self.high_qc.vote_info.round: 
            self.high_qc = qc
        #print('in pqc', qc)

    def execute_and_insert(self, b):
        #print('execute_and_insert ', b)
        # self.modules.Ledger.speculate(b.qc.block_id, b.id, b.payload)
        self.__add(b)
        #print('pb ', obj_to_string(self.pending_block_tree))


    def process_vote(self, vote):
        print('v1')
        self.process_qc(vote.high_commit_qc)
        # vote_idx = hash(vote.ledger_commit_info)
        # self.pending_votes[vote_idx] = self.pending_votes[vote_idx] + vote.signature
        # if self.pending_votes[vote_idx] == 2*(self.modules.config.nfaulty)+1:
        #     qc = QC(vote.vote_info, vote.state_id, self.pending_votes[vote_idx])
        #     return qc
        print('v2', vote.vote_info.round)
        count = 1 if not (self.pending_votes.get(vote.vote_info.round,None)) else self.pending_votes[vote.vote_info.round] + 1
        self.pending_votes[vote.vote_info.round] = count
        print('v3', count)
        if count == 2:
            return QC(vote.vote_info, vote.ledger_commit_info, None, None, None)
        return None

    def generate_block(self, config, txns, current_round):
        #print('hereee ', config)
        return Block(config, txns, current_round, self.high_qc)
