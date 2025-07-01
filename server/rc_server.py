import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from relay_chain.relay_chain import RelayChain
from relay_chain.validator import ValidatorNode
from zk_simulator import verify_zk_proof
import requests
from lightclient.light_client_sc import LightClientSC
from lightclient.light_client_sc2 import LightClientSC2
from waitress import serve

app = Flask(__name__)
validators = [ValidatorNode(f"v{i}") for i in range(4)]
rc = RelayChain(validators)

lc_map = {
    "chainA": LightClientSC(),
    "chainB": LightClientSC2()
}

@app.route("/get_block", methods=["GET"])
def get_block():
    block = rc.generate_block()

    # Sync header to DC
    header = {
        "height":      block["header"]["height"],
        "merkle_root": block["header"]["merkle_root"]
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

@app.route("/sync_header", methods=["POST"])
def sync_header():
    header = request.json
    chain_id = header.get("chain_id")  

    if not chain_id or chain_id not in lc_map:
        return jsonify({"updated": False, "error": "missing/invalid chain_id"}), 400

    ok = lc_map[chain_id].update_header(header)
    return jsonify({"updated": ok})

@app.route("/relay_tx", methods=["POST"])
def relay_tx():
    d = request.json
    tx = d["tx"]
    receiver = tx["receiver"]
    payload  = tx["payload"]
    chain_id = tx.get("chain_id")
    
    tx_obj = {
        "receiver": receiver,
        "payload": payload
    }

    if chain_id:                         
        tx_obj["chain_id"] = chain_id

    tx_str = json.dumps(tx_obj, sort_keys=True)
    
    chain_id = tx.get("chain_id")
    lc = lc_map.get(chain_id)
    if not lc:
        return jsonify({"accepted": False, "error": "Unknown chain_id"}), 400

    # 1. Light Client verification
    ok = lc.verify_tx(
        hash_tx_mkl  = d["tx_hash_mkl"],
        tx_hash_id   = d["tx_hash_id"],
        merkle_proof = d["proof"],
        zk_proof     = d["zk_proof"]
    )
    if not ok:
        return jsonify({"accepted": False, "reason": "light client rejected"})

    # 2. Consensus RC
    accepted = rc.receive_tx(
        tx             = tx_str,
        tx_hash_formkl = d["tx_hash_mkl"],
        proof          = d["proof"],
        merkle_root    = lc.merkle_root
    )
    return jsonify({"accepted": accepted})

@app.route("/get_proof", methods=["POST"])
def get_proof():
    tx = request.json.get("tx")

    # Nếu tx là dict thì chuyển thành JSON string
    if isinstance(tx, dict):
        tx = json.dumps(tx, sort_keys=True)

    proof = rc.get_merkle_proof(tx)
    root = rc.get_merkle_root()

    if proof is None:
        print("⚠️ Không tìm thấy tx trong block RC:", tx)
        return jsonify({"error": "tx not found"}), 400

    return jsonify({
        "proof": proof,
        "merkle_root": root
    })


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5002, threaded = True)
