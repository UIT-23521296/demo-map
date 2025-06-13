import json
from zk_simulator import hash_data, generate_zk_proof

class SCtoRCProver:
    def __init__(self, source_chain, relay_chain):
        self.sc = source_chain
        self.rc = relay_chain

    def send_transaction(self, tx_payload: dict, tx_receiver: str, tx_id: str):
        """
        1. Thêm giao dịch vào SC
        2. Tạo block
        3. Lấy Merkle proof
        4. Gửi lên RelayChain
        """
        print("\n📤 [Prover] Sending transaction from SC to RC")
        tx = self.sc.add_transaction(tx_payload, tx_receiver, tx_id)
        block = self.sc.generate_block()
        merkle_root = block["merkle_root"]
        proof = self.sc.get_merkle_proof(tx)
        
        #Prover
        tx_hash = hash_data(tx_id)
        tx_hash_for_mkl = hash_data(tx)
        zk_proof = generate_zk_proof(tx_id, merkle_root)

        accepted = self.rc.receive_tx(tx, tx_hash, tx_hash_for_mkl, proof, merkle_root, zk_proof)
        print("✅ RelayChain accepted TX:" if accepted else "❌ RelayChain rejected TX")
        return {
            "tx": tx,
            "tx_hash": tx_hash_for_mkl,
            "proof": proof,
            "merkle_root": merkle_root,
            "zk_proof": zk_proof,
            "accepted": accepted
        }
