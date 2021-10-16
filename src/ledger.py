import os

class Ledger:
    def __init__(self, modules_map):
        self.modules_map = modules_map

    def speculate(self, prev_block_id, block_id, txns):
        pass

    def pending_state(self, block_id:int):
        pass

    def commit(self, block_id:int):
        pending_tree = self.modules_map["block_tree"].pending_block_tree
        payload = str(pending_tree.payload[0]) + "\n" if len(pending_tree.payload) > 0 else None
        # print('Validator', self.modules_map["config"]["id"], " Payload :", payload)
        if pending_tree.id != block_id or not payload:
            print('Error while committing : Block_id mismatch. Block_id: ' , block_id, ', pending_tree.id: ', pending_tree.id)
            exit(0)
            # return
        
        file_path = "../ledgers/ledger_" + str(self.modules_map["config"]["id"]) + ".txt"
        file = open(file_path, "a+")

        file.write(payload)

        file.flush()
        os.fsync(file.fileno())
        file.close()


    def committed_block(self, block_id:int):
        return 1