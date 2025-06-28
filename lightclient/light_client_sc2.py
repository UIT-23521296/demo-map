# light_client_sc.py  (chạy bên trong RC)
from merkletools import MerkleTools
import json
from zk_simulator import verify_zk_proof, hash_data

class LightClientSC2:
    """
    Light-client đồng bộ & xác minh block SC (chainB) ở phía RC.
    """
    def __init__(self):
        self.finalized_header = None          # lưu header mới nhất
        self.merkle_root      = None          # r_mkl của header
        # tuỳ thiết kế bạn thêm validator_set, epoch, v.v.

    # ---------- phase “sync header” ----------
    def update_header(self, header: dict):
        """
        header = {height, merkle_root, ...}   (giả lập header tối giản)
        """
        # ở bản đầy đủ bạn sẽ verify chữ ký + BFT threshold trước khi chấp nhận
        if (self.finalized_header is None) or (header["height"] > self.finalized_header["height"]):
            self.finalized_header = header
            self.merkle_root      = header["merkle_root"]
            return True
        return False

    # ---------- phase “verify proof” ----------
    def verify_tx(self, ctx: str, merkle_proof: list, zk_proof: str) -> bool:
        """
        ctx  : chuỗi tx (đã JSON.dumps)
        merkle_proof : proof kèm theo
        zk_proof     : proof giả lập
        """
        if self.finalized_header is None:
            return False                      # chưa sync header

        mt = MerkleTools(hash_type="sha256")
        tx_hash_mkl = hash_data(ctx)

        mkl_ok = mt.validate_proof(
            merkle_proof,
            tx_hash_mkl,
            self.merkle_root
        )

        # tx_id nằm trong payload ⇒ lôi ra để tạo tx_hash_id
        tx_id        = json.loads(ctx)["tx_id"]
        tx_hash_id   = hash_data(tx_id)
        zk_ok        = verify_zk_proof(zk_proof, tx_hash_id, self.merkle_root)

        return mkl_ok and zk_ok
