# consensus.py
import json, hashlib
from typing import List
from ecdsa import VerifyingKey, SECP256k1, BadSignatureError
from relay_chain.validator import ValidatorNode

class ConsensusEngine:
    def __init__(self, validators: List[ValidatorNode]):
        self.validators = {v.node_id: v for v in validators}
        self.quorum = (2 * len(validators)) // 3 + 1   # ≥ 2/3

    def _verify_vote(self, vote: dict) -> bool:
        """
        Kiểm chữ ký vote bằng public-key kèm theo.
        """
        message   = json.dumps({"tx_hash": vote["tx_hash"],
                                "merkle_root": vote["merkle_root"]},
                               sort_keys=True)
        digest    = hashlib.sha256(message.encode()).digest()
        try:
            vk = VerifyingKey.from_string(bytes.fromhex(vote["pubkey"]), curve=SECP256k1)
            vk.verify(bytes.fromhex(vote["signature"]), digest)
            return True
        except BadSignatureError:
            return False

    def commit_tx(self, tx_hash: str, proof: list, merkle_root: str) -> bool:
        message = json.dumps({"tx_hash": tx_hash, "merkle_root": merkle_root}, sort_keys=True)

        votes_valid = 0
        for vid, validator in self.validators.items():
            vote = validator.vote(tx_hash, merkle_root)

            if self._verify_vote(vote):
                votes_valid += 1
            else:
                print(f"❌  Vote spoof / bad sig from {vid}")

        print(f"✅  ECDSA votes: {votes_valid}/{len(self.validators)}")
        return votes_valid >= self.quorum
