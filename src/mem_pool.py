from collections import deque


class MemPool:
    def __init__(self, modules) -> None:
        self.modules = modules
        self.commands = []

    def add_command_to_mempool(self, client_command):

        # Handling deduplicates by checking ledger's committed_Txns and Mem_pool 

        txn_id = client_command[3]
        # if txn_id in self.modules['ledger'].committed_txns:
        #     return 
        
        # for item in self.commands:  
        #     if txn_id in item:
        #         return

        # TODO : Also check in pending states?
        self.commands.append(client_command)

    def is_empty(self):
        return len(self.commands) == 0

    def get_transaction(self):
        if not self.is_empty():
            return self.commands.pop(0)
        return None
    
    def update_mempool(self, payload):
        for item in self.commands:
            if item[0] == payload[0] and item[1] == payload[1] and item[2] == payload[2]:
                self.commands.remove(item)
                break