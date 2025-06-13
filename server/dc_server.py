import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from blockchains.destination_chain import DestinationChain
from lightclient.light_client_rc import LightClientRC

app = Flask(__name__)
dc = DestinationChain("chainB")

lc_rc = LightClientRC()

@app.route("/receive_ctx", methods=["POST"])
def receive_ctx():
    data = request.json
    result = dc.receive_ctx(
        tx=data["tx"],
        tx_hash_id=data["tx_hash_id"],
        tx_hash=data["tx_hash"],
        merkle_root_rc= lc_rc.merkle_root,
        proof_merkle=data["proof"],
        proof_zk=data["zk_proof"]
    )
    return jsonify({"accepted": result})

@app.route("/get_block", methods=["GET"])
def get_block():
    dc.generate_block()
    return jsonify(dc.get_latest_block())

@app.route("/sync_header", methods=["POST"])
def sync_header():
    header = request.json        # {height, merkle_root, ...}
    ok = lc_rc.update_header(header)
    return jsonify({"updated": ok})

if __name__ == "__main__":
    app.run(port=5003)
