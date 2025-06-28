import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
import requests      
from blockchains.source_chain import SourceChain

app = Flask(__name__)
sc = SourceChain("chainB")

@app.route("/send_tx", methods=["POST"])
def send_tx():
    payload = request.json.get("payload")
    receiver = request.json.get("receiver")
    tx_id = request.json.get("tx_id")

    # Tạo transaction và sinh block
    tx = sc.add_transaction(payload, receiver, tx_id)
    block = sc.generate_block()

    # Chuẩn bị header để sync LC
    header = {
        "height": block["header"]["height"],
        "merkle_root": block["header"]["merkle_root"],
        "chain_id": sc.chain_id,
        "hash": block["hash"],
    }

    # Đồng bộ với LC
    try:
        rc_res = requests.post("http://localhost:5002/sync_header", json=header, timeout=2).json()
        print("Sync header → RC:", rc_res)
    except Exception as e:
        print("⚠️  Không sync được header sang RC:", e)
    
    return jsonify({
        "tx": tx,
        "block": block
    })

@app.route("/get_proof", methods=["POST"])
def get_proof():
    tx = request.json.get("tx")
    proof = sc.get_merkle_proof(tx)
    root = sc.get_merkle_root()
    return jsonify({
        "proof": proof,
        "merkle_root": root
    })

if __name__ == "__main__":
    app.run(port=5006)
