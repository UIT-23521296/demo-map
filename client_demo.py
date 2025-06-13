import requests, json, time
from zk_simulator import hash_data

tx_id   = "tx_001"
payload = {"msg": "Send 100 MAP"}
reiceiver = "chainB"

# 1. SC
r = requests.post("http://localhost:5001/send_tx",
                  json={"tx_id": tx_id, "receiver": reiceiver, "payload": payload}).json()
tx  = r["tx"]; print("SC block:", r["block"]["height"])
block = r["block"]

# 2. Lấy proof
pr = requests.post("http://localhost:5004/get_proof", json={"tx":tx, "merkle_root": block["merkle_root"]}).json()

# 3. Hỏi prover SC→RC để lấy zk_proof, tx_hash
# pv = requests.post("http://localhost:5004/prove",
#                    json={"tx_id":tx_id, "merkle_root":pr["merkle_root"]}).json()

# 3. Push lên RC
rc_res = requests.post("http://localhost:5002/relay_tx", json={
    "tx"           : tx,
    "tx_hash"      : hash_data(tx_id),
    "tx_hash_mkl"  : hash_data(tx),
    "proof"        : pr["proof"],
    "merkle_root"  : pr["merkle_root"],
    "zk_proof"     : pr["zk_proof"]
}).json()
print("RC accept?", rc_res["accepted"])

# 5. RC đóng block
requests.get("http://localhost:5002/get_block")

pr_rc_dc = requests.post("http://localhost:5005/get_proof", json={"tx":tx, "merkle_root": block["merkle_root"]}).json()

# 6. Gửi ctx sang DC
rc_res = requests.post("http://localhost:5003/receive_ctx", json={
    "tx"           : tx,
    "tx_hash_id"      : hash_data(tx_id),
    "tx_hash"  : hash_data(tx),
    "proof"        : pr_rc_dc["proof"],
    "merkle_root"  : pr_rc_dc["merkle_root"],
    "zk_proof"     : pr_rc_dc["zk_proof"]
}).json()
print("DC accept?", rc_res["accepted"])

# 7. DC seal
blk = requests.get("http://localhost:5003/get_block").json()
print("DC block:", json.dumps(blk, indent=2))
