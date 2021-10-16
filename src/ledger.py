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
        if pending_tree.id != block_id:
            print('Error while committing : Block_id mismatch. Block_id: ' , block_id, ', pending_tree.id: ', pending_tree.id)
            exit(0)
        
        file_path = "../ledgers/ledger_" + str(self.modules_map["config"]["id"]) + ".txt"
        file = open(file_path, "a")
        payload = pending_tree.payload + "\n"
        file.write(payload)

        file.flush()
        os.fsync(file.fileno())
        file.close()


    def committed_block(self, block_id:int):
        return 1

def main():
    modules={}
    modules["config"] = {}
    modules["config"]["id"] = "0"
    l = Ledger(modules)
    l.commit(0, None)

if __name__ == "__main__":
    main()