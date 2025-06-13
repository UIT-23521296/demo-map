import hashlib

def hash_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def generate_zk_proof(tx_id: str, merkle_root: str) -> str:
    """
    Prover tạo zk proof từ dữ liệu bí mật (tx_id) và public (merkle root)
    """
    tx_hash = hash_data(tx_id)
    return hash_data(tx_hash + merkle_root)

def verify_zk_proof(proof: str, tx_hash: str, merkle_root: str) -> bool:
    """
    Verifier không biết tx_id, chỉ biết hash(tx_id), và merkle_root.
    """
    expected = hash_data(tx_hash + merkle_root)
    return proof == expected
