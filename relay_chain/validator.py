from merkletools import MerkleTools

class ValidatorNode:
    def __init__(self, node_id: str, is_honest: bool = True):
        self.node_id = node_id
        self.is_honest = is_honest
        self.mt = MerkleTools(hash_type="sha256")

    def vote(self, tx_hash: str, proof: list, merkle_root: str) -> bool:
        """
        Honest validator sẽ tự xác minh Merkle proof:
        - Nếu hợp lệ thì bỏ phiếu 'đồng ý'
        - Nếu không hoặc validator gian lận thì từ chối
        """
        if not self.is_honest:
            return False

        # Dùng MerkleTools để kiểm tra proof
        is_valid = self.mt.validate_proof(proof, tx_hash, merkle_root)
        return is_valid
