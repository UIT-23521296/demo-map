import hashlib
import json
import time
from typing import List, Dict
from merkletools import MerkleTools

class SourceChain:
    def __init__(self, chain_id: str):
        self.chain_id = chain_id
        self.chain: List[Dict] = []
        self.pending_tx: List[str] = []
        self.block_height = 0
        self.mt = MerkleTools(hash_type="sha256")

    def add_transaction(self, payload: Dict, tx_receiver: str, tx_id: str) -> str:
        tx = {
            "tx_id": tx_id,
            "chain_id": self.chain_id,
            "receiver": tx_receiver,
            "payload": payload
        }
        tx_str = json.dumps(tx, sort_keys=True)
        self.pending_tx.append(tx_str)
        return tx_str
    
    def _hash_block_header(self, header: Dict) -> str:
        header_bytes = json.dumps(header, sort_keys=True).encode()
        return hashlib.sha256(header_bytes).hexdigest()
    
    def _calculate_merkle_root(self, txs: List[str]) -> str:
        self.mt.reset_tree()
        for tx in txs:
            self.mt.add_leaf(tx, do_hash=True)
        self.mt.make_tree()
        return self.mt.get_merkle_root()

    def generate_block(self):
        if not self.pending_tx:
            return None

        root = self._calculate_merkle_root(self.pending_tx)

         # 2. Header
        header = {
            "height": self.block_height,
            "prev_hash": self.chain[-1]["hash"] if self.chain else "0"*64,
            "merkle_root": root,
            "timestamp": int(time.time())
        }

        # 3. Block hash
        header_hash = self._hash_block_header(header)
        block = {
            "header": header,
            "hash": header_hash,
            "transactions": self.pending_tx.copy()
        }

        self.chain.append(block)
        self.block_height += 1
        self.pending_tx.clear()
        return block

    def get_latest_block(self):
        return self.chain[-1] if self.chain else None

    def get_merkle_proof(self, tx: str):
        block = self.get_latest_block()
        if not block:
            return None

        self.mt.reset_tree()
        for t in block["transactions"]:
            self.mt.add_leaf(t, do_hash=True)
        self.mt.make_tree()

        try:
            index = block["transactions"].index(tx)
        except ValueError:
            return None

        return self.mt.get_proof(index)

    def get_merkle_root(self):
        block = self.get_latest_block()
        return block["header"]["merkle_root"] if block else None


    def get_block_header(self):
        block = self.get_latest_block()
        if block:
            return {
                "height": block["header"]["height"],
                "merkle_root": block["header"]["merkle_root"]
            }
        return None
