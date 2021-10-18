from collections import deque
import logging
from constants import *

class MemPool:
    def __init__(self, modules) -> None:
        self.modules = modules
        self.commands = []

    def add_command_to_mempool(self, client_command):

        # Handling deduplicates by checking ledger's committed_Txns, pending_Txns and Mem_pool

        txn_id = client_command[3]
        already_received_command = False
        if client_command[0] != DUMMY:
            if txn_id in self.modules[LEDGER].committed_txn_ids:
                already_received_command = True
 
            if txn_id in self.modules[LEDGER].pending_txn_ids:
                already_received_command = True
        
            for item in self.commands:  
                if txn_id in item:
                    already_received_command = True
                    break
        
        if not already_received_command:
            self.commands.append(client_command)
        else:
            logging.info(f"Already Received {client_command} at Validator{self.modules[CONFIG][ID]}")

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