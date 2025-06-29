# validator.py
import json, hashlib, os
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

class ValidatorNode:
    def __init__(self, node_id: str, sk_hex: str = None):
        self.node_id = node_id

        # ⬇️  Tạo key mới hoặc nhận keyHex sẵn có
        if sk_hex:
            self.sk = SigningKey.from_string(bytes.fromhex(sk_hex), curve=SECP256k1)
        else:
            self.sk = SigningKey.generate(curve=SECP256k1)
        self.vk = self.sk.verifying_key           # public key

    # -------- API tiện dụng ----------
    def export_priv(self) -> str: return self.sk.to_string().hex()
    def export_pub(self)  -> str: return self.vk.to_string().hex()
    # ---------------------------------

    # Hash + sign  (dùng SHA-256 trước khi ký)
    def sign(self, message: str) -> str:
        digest = hashlib.sha256(message.encode()).digest()
        return self.sk.sign(digest).hex()

    # Verify chữ ký
    def verify(self, message: str, signature_hex: str) -> bool:
        digest = hashlib.sha256(message.encode()).digest()
        try:
            self.vk.verify(bytes.fromhex(signature_hex), digest)
            return True
        except BadSignatureError:
            return False

    # Vote cho một giao dịch (trả về object chứa chữ ký)
    def vote(self, tx_hash: str, merkle_root: str) -> dict:
        message = json.dumps({"tx_hash": tx_hash, "merkle_root": merkle_root}, sort_keys=True)
        sig = self.sign(message)
        return {
            "voter": self.node_id,
            "pubkey": self.export_pub(),   # gửi PK để người khác verify
            "tx_hash": tx_hash,
            "merkle_root": merkle_root,
            "signature": sig
        }
