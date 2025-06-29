import json, uuid
from typing import List, Dict
from merkletools import MerkleTools
import hashlib
from relay_chain.validator import ValidatorNode
from relay_chain.consensus import ConsensusEngine
from zk_simulator import *
from merkletools import MerkleTools

class RelayChain:
    def __init__(self, validators: List[ValidatorNode]):
        self.chain: List[Dict] = []
        self.pending_tx: List[Dict] = []
        self.block_height = 0
        self.mt = MerkleTools(hash_type="sha256")
        self.consensus = ConsensusEngine(validators)

    def receive_tx(self, tx: str, tx_hash_formkl: str, proof: List[Dict], merkle_root: str) -> bool:
        # Step 1: verify Merkle proof
        # is_valid_proof = self.mt.validate_proof(proof, tx_hash_formkl, merkle_root)
        # if not is_valid_proof:
        #     print("❌ Merkle proof invalid")
        #     return False

        # # Step 2: verify zk proof
        # is_valid_zk = verify_zk_proof(zk_proof, tx_hash, merkle_root)
        # if not is_valid_zk:
        #     print("❌ zk proof invalid")
        #     return False

        # Step 3: BFT Consensus
        approved = self.consensus.commit_tx(tx_hash_formkl, proof, merkle_root)
        if not approved:
            print("❌ BFT Consensus invalid")
            return False
       
        tx_id = hashlib.sha256(tx.encode()).hexdigest()
        wrapped_tx = {
            "tx_id": tx_id,
            "tx_data": tx  
        }

        self.pending_tx.append(json.dumps(wrapped_tx))
        return True

    def generate_block(self):
        if not self.pending_tx:
            return None

        self.mt.reset_tree()
        for tx in self.pending_tx:
            self.mt.add_leaf(tx, do_hash=True)
        self.mt.make_tree()

        block = {
            "height": self.block_height,
            "merkle_root": self.mt.get_merkle_root(),
            "transactions": self.pending_tx.copy()
        }
        self.chain.append(block)
        self.block_height += 1
        self.pending_tx.clear()
        return block

    def get_latest_block(self):
        return self.chain[-1] if self.chain else None

    def get_merkle_root(self):
        block = self.get_latest_block()
        return block["merkle_root"] if block else None
    
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