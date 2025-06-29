from blockchains.source_chain import SourceChain
from zk_simulator import verify_zk_proof, hash_data
from merkletools import MerkleTools
import json

class DestinationChain(SourceChain):
    def __init__(self, chain_id):
        super().__init__(chain_id)
        self.mt = MerkleTools(hash_type="sha256")

    def receive_ctx(self, tx, tx_hash_id: str, tx_hash: str, merkle_root_rc: str, proof_merkle: list, proof_zk: str) -> bool:
        """
        Nhận giao dịch đã relay từ RC, xác minh:
        1. tx_hash nằm trong Merkle tree của RC (proof_merkle)
        2. proof_zk hợp lệ với (tx_hash, merkle_root_rc)
        Nếu cả 2 đúng, thêm vào pending_tx để ghi block.
        """
        self.mt.reset_tree()

        # Bước 1: xác minh Merkle proof
        is_merkle_valid = self.mt.validate_proof(proof_merkle, tx_hash, merkle_root_rc)
        
        if not is_merkle_valid:
            print("❌ Merkle proof invalid")
            return False

        # Bước 2: xác minh zk giả lập
        is_zk_valid = verify_zk_proof(proof_zk, tx_hash_id, merkle_root_rc)

        if not is_zk_valid:
            print("❌ zk proof invalid")
            return False

        local_tx_id = hash_data(json.dumps(tx, sort_keys=True))

        # ✅ Gói lại tx để lưu
        wrapped = {
            "tx_id": local_tx_id,
            "tx_data": tx
        }
        self.pending_tx.append(json.dumps(wrapped, sort_keys=True))
        print("✅ DC accepted tx with new ID:", local_tx_id)
        return True
