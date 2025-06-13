from typing import List
from relay_chain.validator import ValidatorNode

class ConsensusEngine:
    def __init__(self, validators: List[ValidatorNode]):
        self.validators = validators
        self.quorum = (2 * len(validators)) // 3 + 1  # BFT: > 2/3 đồng thuận

    def commit_tx(self, tx: str, proof: list, merkle_root: str) -> bool:
        """
        Lấy phiếu từ tất cả validator. Nếu số validator đồng ý >= quorum, 
        thì giao dịch được chấp nhận.
        """
        votes = 0
        for validator in self.validators:
            if validator.vote(tx, proof, merkle_root):
                votes += 1
        print(f"✅ BFT votes: {votes}/{len(self.validators)}")
        return votes >= self.quorum
