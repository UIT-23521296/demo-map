import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from relay_chain.relay_chain import RelayChain
from relay_chain.validator import ValidatorNode
from zk_simulator import verify_zk_proof
import requests
from lightclient.light_client_sc import LightClientSC

app = Flask(__name__)
validators = [ValidatorNode(f"v{i}") for i in range(4)]
rc = RelayChain(validators)

# @app.route("/relay_tx", methods=["POST"])
# def relay_tx():
#     data = request.json
#     result = rc.receive_tx(
#         tx=data["tx"],
#         tx_hash=data["tx_hash"],
#         tx_hash_formkl=data["tx_hash_for_mkl"],
#         proof=data["proof"],
#         merkle_root=data["merkle_root"],
#         zk_proof=data["zk_proof"]
#     )
#     return jsonify({"accepted": result})

@app.route("/get_block", methods=["GET"])
def get_block():
    block = rc.generate_block()

    # Đồng bộ rc LC
    header = {
        "height":      block["height"],
        "merkle_root": block["merkle_root"]
    }

    try:
        rc_res = requests.post("http://localhost:5003/sync_header", json=header, timeout=2).json()
        print("Sync header → DC:", rc_res)
    except Exception as e:
        print("⚠️  Không sync được header sang DC:", e)
    
    return jsonify({
        "tx": block["transactions"],
        "block": block
    })

# rc_server.py
lc_sc = LightClientSC()

@app.route("/sync_header", methods=["POST"])
def sync_header():
    header = request.json        # {height, merkle_root, ...}
    ok = lc_sc.update_header(header)
    return jsonify({"updated": ok})

@app.route("/relay_tx", methods=["POST"])
def relay_tx():
    d = request.json
    # 1. LC kiểm tra
    ok = lc_sc.verify_tx(
        ctx           = d["tx"],
        merkle_proof  = d["proof"],
        zk_proof      = d["zk_proof"]
    )
    if not ok:
        return jsonify({"accepted": False})

    # 2. chuyển qua lớp consensus của RC
    accepted = rc.receive_tx(
        tx              = d["tx"],
        tx_hash         = d["tx_hash"],
        tx_hash_formkl  = d["tx_hash_mkl"],
        proof           = d["proof"],
        merkle_root     = lc_sc.merkle_root,
        zk_proof        = d["zk_proof"]
    )
    return jsonify({"accepted": accepted})

@app.route("/get_proof", methods=["POST"])
def get_proof():
    tx = request.json.get("tx")
    proof = rc.get_merkle_proof(tx)
    root = rc.get_merkle_root()
    return jsonify({
        "proof": proof,
        "merkle_root": root
    })


if __name__ == "__main__":
    app.run(port=5002)
