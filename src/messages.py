from enum import Enum

class TimeOutMsg:
    def __init__(self, tmo_info, last_round_tc, high_commit_qc) -> None:
        self.tmo_info = tmo_info                # TimeoutInfo for some round with a high qc 
        self.last_round_tc = last_round_tc      # TC for tmo_info.round - 1 if tmo_info.high_qc.round != tmo_info.round - 1, else None
        self.high_commit_qc = high_commit_qc    # QC to synchronize on committed blocks

class TimeoutInfo:
    def __init__(self, round, high_qc, sender, signature) -> None:
        self.round = round              
        self.high_qc = high_qc          
        self.sender = sender            
        self.signature = signature      

class TC:
    def __init__(self, round, tmo_high_qc_rounds, tmo_signatures) -> None:
        self.round = round
        self.tmo_high_qc_rounds = tmo_high_qc_rounds
        self.tmo_signatures = tmo_signatures

class ProposalMsg:
    def __init__(self, block, last_round_tc, high_commit_qc, sender, signature:None) -> None:
        self.block = block                      
        self.last_round_tc = last_round_tc      # TC for block.round - 1 if block.qc.vote_info.round != block.round - 1, else None
        self.high_commit_qc = high_commit_qc    # QC to synchronize on committed blocks
        self.sender = sender                    
        self.signature = signature

class MsgType(Enum):
    PROPOSE = 1
    REMOTE_TIMEOUT = 2
    VOTE = 3
    DONE = 4
    ACK = 5
    TERMINATE = 6
    WILDCARD = 7
    CLIENT = 8