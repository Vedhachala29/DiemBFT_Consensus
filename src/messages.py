
class TimeOutMsg:
    def __init__(self, tmo_info, last_round_tc, high_commit_qc) -> None:
        self.tmo_info = tmo_info
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc

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
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.sender = sender
        self.signature = signature