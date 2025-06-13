from zk_simulator import generate_zk_proof

class RCtoDCProver:
    def __init__(self, relay_chain, destination_chain):
        self.rc = relay_chain
        self.dc = destination_chain

    def send_to_destination(self, tx, tx_hash: str, tx_id: str):
        """
        1. Lấy block mới nhất trên RC
        2. Lấy Merkle root và Merkle proof của tx_hash
        3. Tạo zk proof từ tx_id + merkle_root
        4. Gửi sang DestinationChain
        """
        print("\n📤 [Prover] Sending proof from RC to DC")
        merkle_root_rc = self.rc.get_merkle_root()

        # Find index of tx_hash (do_hash=True -> hash match)
        index = None
        for i, tx in enumerate(self.rc.get_latest_block()["transactions"]):
            from zk_simulator import hash_data
            if hash_data(tx) == tx_hash:
                index = i
                break

        if index is None:
            print("❌ Không tìm thấy tx_hash trong RC")
            return False

        # Prover
        proof_merkle = self.rc.mt.get_proof(index)
        tx_hash_id = hash_data(tx_id)
        proof_zk = generate_zk_proof(tx_id, merkle_root_rc)

        success = self.dc.receive_ctx(tx, tx_hash_id, tx_hash, merkle_root_rc, proof_merkle, proof_zk)
        print("✅ DestinationChain accepted TX:" if success else "❌ DestinationChain rejected TX")
        return success