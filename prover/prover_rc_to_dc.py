# prover_rc_dc.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
import requests
import json
from zk_simulator import generate_zk_proof, hash_data
from waitress import serve

app = Flask(__name__)

RC_URL = "http://localhost:5002"

# ---- API: lấy Merkle-proof thông qua SC-server -------
@app.route("/get_proof", methods=["POST"])
def get_proof():
    tx = request.json["tx"]

    resp = requests.post(f"{RC_URL}/get_proof", json={"tx": tx}, timeout=2)
    if resp.status_code != 200:
        print("❌ Không lấy được Merkle proof từ RC:", resp.status_code, resp.text)
        return jsonify({"error": "RC không trả về hợp lệ"}), 500

    rc_data = resp.json()

    if isinstance(tx, str):
        tx_dict = json.loads(tx)
    else:
        tx_dict = tx

    tx_id = tx_dict["tx_id"]
    zk_proof = generate_zk_proof(tx_id, rc_data["merkle_root"])

    return jsonify({
        "proof": rc_data["proof"],
        "merkle_root": rc_data["merkle_root"],
        "zk_proof": zk_proof,
        "tx": tx
    })


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5005)
