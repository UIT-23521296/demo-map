# prover_rc_dc.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
import requests
import json
from zk_simulator import generate_zk_proof, hash_data

app = Flask(__name__)

RC_URL = "http://localhost:5002"

# ---- API: lấy Merkle-proof thông qua SC-server -------
@app.route("/get_proof", methods=["POST"])
def get_proof():
    tx          = request.json["tx"]           # string transaction
    # Gọi SC-server để lấy proof + root
    resp = requests.post(f"{RC_URL}/get_proof", json={"tx": tx}, timeout=2)
    rc_data = resp.json()                      # {"proof": [...], "merkle_root": "...."}

    # zk_proof 
    tx_dict = json.loads(tx)         # ✅ chuyển string → dict
    tx_id   = tx_dict["tx_id"]       # ✅ lấy tx_id từ dict
    zk_proof    = generate_zk_proof(tx_id, rc_data["merkle_root"])

    return jsonify({
        "proof"      : rc_data["proof"],
        "merkle_root": rc_data["merkle_root"],
        "zk_proof"   : zk_proof,
        "tx"         : tx
    })

if __name__ == "__main__":
    app.run(port=5005)
