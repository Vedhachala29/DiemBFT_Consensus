import os
from constants import *
from lru import LRU

class Ledger:
    def __init__(self, modules_map):
        self.modules_map = modules_map
        self.speculated_state = {}
        self.LRU_commited_cache = LRU(1000)       # LRU dict for limited size
        self.committed_txn_ids = set()
        self.pending_txn_ids = set()

    def speculate(self,prev_block_id, block_id, txn):
        """
        maintaining a specated state tree
        storing only parent pointer for optimizations
        """
        self.speculated_state[block_id] = {
            "payload": txn,
            "parent_id": prev_block_id
        }
        self.pending_txn_ids.add(txn[3])


    def commit(self, id):
        """
        gets the transactions from the speculated tree
        prunes the speculated tree during this process
        maintains pending and commited transactions for dedup
        Updates the LRU commited transactions
        """
        txns = []
        while self.speculated_state.get(id, None) is not None:
            state = self.speculated_state.pop(id)
            if state["payload"] and len(state["payload"]) and state["payload"][0] != DUMMY:
                self.LRU_commited_cache[id] = state["payload"]
                txns.insert(0,state["payload"])
            id = state["parent_id"]

        self.modules_map['latest_committed_payload'] = txns
        for txn in txns:
            self.persist_txn(txn)


    def pending_state(self, block_id):
        """
        looks up on the speculated states and returns the block id
        """
        return self.speculated_state.get(block_id, None)

    def get_committed_block(block_id):
        """
        gets the commited transaction if it is present in the LRU cache
        Makes the key MRU when accessed
        """
        if self.LRU_commited_cache.has_key(block_id):
            return self.LRU_commited_cache[block_id]
        else:
            return None

    def persist_txn(self, txn):
        """
        Persists the transaction to file
        """
        if txn is None:
            return
        if txn[0] == DUMMY:
            return
        payload = txn if len(txn) > 0 else None 
        if payload[3] not in self.committed_txn_ids:
            self.committed_txn_ids.add(payload[3])
        if payload[3] in self.pending_txn_ids:
            self.pending_txn_ids.remove(payload[3])

        payload = str(txn) + "\n"
        file_path = f'../ledgers/{self.modules_map[CONFIG]["config_num"]}/ledger_{str(self.modules_map[CONFIG][ID])}.txt'
        file = open(file_path, "a+")

        file.write(payload)

        file.flush()
        os.fsync(file.fileno())
        file.close()
