# prover_sc_rc.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
import json
import requests
from zk_simulator import generate_zk_proof, hash_data

app = Flask(__name__)


SC_URL = "http://localhost:5001" # địa chỉ Source-Chain server

# ---- API: lấy Merkle-proof thông qua SC-server -------
@app.route("/get_proof", methods=["POST"])
def get_proof():
    tx          = request.json["tx"]           # string transaction
    # Gọi SC-server để lấy proof + root
    resp = requests.post(f"{SC_URL}/get_proof", json={"tx": tx}, timeout=2)
    sc_data = resp.json()                      # {"proof": [...], "merkle_root": "...."}

    # Kèm thêm zk_proof (tuỳ bạn có cần hay không)
    tx_dict = json.loads(tx)         # ✅ chuyển string → dict
    tx_id   = tx_dict["tx_id"]       # ✅ lấy tx_id từ dict
    zk_proof    = generate_zk_proof(tx_id, sc_data["merkle_root"])

    return jsonify({
        "proof"      : sc_data["proof"],
        "merkle_root": sc_data["merkle_root"],
        "zk_proof"   : zk_proof,
        "tx"         : tx
    })

if __name__ == "__main__":
    app.run(port=5004)
