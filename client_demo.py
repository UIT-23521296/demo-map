# import requests, json, time
# from zk_simulator import hash_data

# tx_id   = "tx_001"
# payload = {"msg": "Send 100 MAP"}
# reiceiver = "chainC"

# # 1. SC
# # r = requests.post("http://localhost:5001/send_tx",
# #                   json={"tx_id": tx_id, "receiver": reiceiver, "payload": payload}).json()
# r = requests.post("http://localhost:5006/send_tx",
#                   json={"tx_id": tx_id, "receiver": reiceiver, "payload": payload}).json()
# tx  = r["tx"]; 
# print("SC block:", r["block"]["header"]["height"])
# block = r["block"]

# # 2. Lấy proof
# pr = requests.post("http://localhost:5004/get_proof", json={"tx":tx, "merkle_root": block["header"]["merkle_root"]}).json()

# # 3. Hỏi prover SC→RC để lấy zk_proof, tx_hash
# # pv = requests.post("http://localhost:5004/prove",
# #                    json={"tx_id":tx_id, "merkle_root":pr["merkle_root"]}).json()

# # 3. Push lên RC
# rc_res = requests.post("http://localhost:5002/relay_tx", json={
#     "tx"           : tx,
#     "tx_hash"      : hash_data(tx_id),
#     "tx_hash_mkl"  : hash_data(tx),
#     "proof"        : pr["proof"],
#     "zk_proof"     : pr["zk_proof"]
# }).json()
# print("RC accept?", rc_res["accepted"])

# # 5. RC đóng block
# res = requests.get("http://localhost:5002/get_block")
# data = res.json()
# tx = data["tx"][0]
# block = data["block"]

# pr_rc_dc = requests.post("http://localhost:5005/get_proof", json={"tx":tx, "merkle_root": block["merkle_root"]}).json()

# # 6. Gửi ctx sang DC
# rc_res = requests.post("http://localhost:5003/receive_ctx", json={
#     "tx"           : tx,
#     "tx_hash_id"      : hash_data(tx_id),
#     "tx_hash"  : hash_data(tx),
#     "proof"        : pr_rc_dc["proof"],
#     "merkle_root"  : pr_rc_dc["merkle_root"],
#     "zk_proof"     : pr_rc_dc["zk_proof"]
# }).json()
# print("DC accept?", rc_res["accepted"])

# # 7. DC seal
# blk = requests.get("http://localhost:5003/get_block").json()
# print("DC block:", json.dumps(blk, indent=2))

import requests, json
from datetime import datetime
from zk_simulator import hash_data

def send_from_sc(port, tx_id, payload, receiver):
    print(f"\n=== Gửi từ SC port {port} ===")
    r = requests.post(f"http://localhost:{port}/send_tx",
                      json={"tx_id": tx_id, "receiver": receiver, "payload": payload}).json()
    tx = r["tx"]
    block = r["block"]
    print("SC block:", block["header"]["height"])
    print(json.dumps(r, indent=2))

    # 2. Lấy proof
    pr = requests.post("http://localhost:5004/get_proof",
                       json={"tx": tx, "merkle_root": block["header"]["merkle_root"]}).json()
    
    tx_obj = json.loads(tx)        # chuyển tx-string → dict
    receiver   = tx_obj["receiver"]
    payload    = tx_obj["payload"]
    chain_id   = tx_obj.get("chain_id")     # có thể None nếu bạn không lưu chain_id

    tx_obj = {
        "receiver": receiver,
        "payload": payload,
        "chain_id": chain_id
    }

    # 3. Push lên RC
    rc_res = requests.post("http://localhost:5002/relay_tx", json={
        "tx"          : tx_obj,
        "tx_hash_id"  : hash_data(tx_id),
        "tx_hash_mkl" : hash_data(tx),
        "proof"       : pr["proof"],
        "zk_proof"    : pr["zk_proof"]
    }).json()
    print("RC accept?", rc_res["accepted"])
    print(json.dumps(rc_res, indent=2))


# ==== Gửi từ SC1 (port 5001) ====
send_from_sc(5001, "tx_sc1", {"msg": "SC1 → chainC"}, "chainC")

# ==== Gửi từ SC2 (port 5006) ====
send_from_sc(5006, "tx_sc2", {"msg": "SC2 → chainC"}, "chainC")


# ==== RC đóng block ====
print("\n=== Đóng block RC ===")
res = requests.get("http://localhost:5002/get_block")
print(json.dumps(res.json(), indent=2))
data = res.json()
txs = data["tx"]
block = data["block"]

# ==== Gửi từng ctx sang DC ====
for tx in txs:
    pr_rc_dc = requests.post("http://localhost:5005/get_proof",
                             json={"tx": tx, "merkle_root": block["header"]["merkle_root"]}).json()
    
    tx = json.loads(tx)
    tx_id    = tx["tx_id"]        
    tx_data  = tx["tx_data"]   
    
    rc_res = requests.post("http://localhost:5003/receive_ctx", json={
        "tx"           : tx_data,
        "tx_hash_id"   : hash_data(tx_id), 
        "tx_hash"      : hash_data(json.dumps(tx)),
        "proof"        : pr_rc_dc["proof"],
        "merkle_root"  : pr_rc_dc["merkle_root"],
        "zk_proof"     : pr_rc_dc["zk_proof"]
    }).json()
    print("DC accept?", rc_res["accepted"])


# ==== DC seal block ====
print("\n=== DC Block ===")
blk = requests.get("http://localhost:5003/get_block").json()
print(json.dumps(blk, indent=2))
