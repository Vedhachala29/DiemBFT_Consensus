import os
import util

class Ledger:
    def __init__(self, modules_map):
        self.modules_map = modules_map
        self.committed_txns = {}

    def speculate(self, prev_block_id, block_id, txns):
        pass

    def pending_state(self, block_id:int):
        pass

    def commit(self, block_id:int):
        pending_tree = self.modules_map["block_tree"].pending_block_tree
        # pending_transactions = util.get_pending_transactions(self.modules_map)
        pending_transactions = self.modules_map["block_tree"].pending_transactions
        if len(pending_transactions) == 0:
            print("Nothing to print for validator", self.modules_map["config"]["id"])
            exit(0)
        payload = str(pending_transactions[0]) + "\n" if len(pending_transactions) > 0 else None
        if pending_tree.id != block_id:
            print('Error while committing : Block_id mismatch. Block_id: ' , block_id, ', pending_tree.id: ', pending_tree.id)
            exit(0)
        
        self.committed_txns[payload[3]] = payload
        self.modules_map['latest_committed_payload'] = payload
        file_path = "../ledgers/ledger_" + str(self.modules_map["config"]["id"]) + ".txt"
        file = open(file_path, "a+")

        file.write(payload)

        file.flush()
        os.fsync(file.fileno())
        file.close()


    def committed_block(self, block_id:int):
        return 1