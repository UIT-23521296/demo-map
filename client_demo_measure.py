import requests, json, time, csv
from datetime import datetime
from zk_simulator import hash_data

LOG_FILE = "measure_log.csv"

with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "tx_id", "step", "duration_sec"])

def log_duration(tx_id, step_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            duration = end - start
            with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), tx_id, step_name, f"{duration:.6f}"])
            return result
        return wrapper
    return decorator

def send_from_sc(port, tx_id, payload, receiver):
    print(f"\n=== Gửi từ SC port {port} ===")

    @log_duration(tx_id, "B1_SC_gửi_tx")
    def step1_send():
        return requests.post(f"http://localhost:{port}/send_tx",
                             json={"tx_id": tx_id, "receiver": receiver, "payload": payload}).json()
    r = step1_send()

    tx = r["tx"]
    block = r["block"]
    print("SC block:", block["header"]["height"])
    print(json.dumps(r, indent=2))

    @log_duration(tx_id, "B2_SC_get_proof")
    def step2_proof():
        return requests.post("http://localhost:5004/get_proof",
                             json={"tx": tx, "merkle_root": block["header"]["merkle_root"]}).json()
    pr = step2_proof()

    tx_obj = json.loads(tx)
    tx_obj = {
        "receiver": tx_obj["receiver"],
        "payload": tx_obj["payload"],
        "chain_id": tx_obj.get("chain_id")
    }

    @log_duration(tx_id, "B3_RC_relay_tx")
    def step3_relay():
        return requests.post("http://localhost:5002/relay_tx", json={
            "tx": tx_obj,
            "tx_hash_id": hash_data(tx_id),
            "tx_hash_mkl": hash_data(tx),
            "proof": pr["proof"],
            "zk_proof": pr["zk_proof"]
        }).json()
    rc_res = step3_relay()

    print("RC accept?", rc_res["accepted"])
    print(json.dumps(rc_res, indent=2))

# ==== Gửi từ SC1 và SC2 ====
send_from_sc(5001, "tx_sc1", {"msg": "SC1 → chainC"}, "chainC")
# send_from_sc(5006, "tx_sc2", {"msg": "SC2 → chainC"}, "chainC")

# ==== RC đóng block ====
print("\n=== Đóng block RC ===")

@log_duration("tx_all", "B4_RC_dong_block")
def get_rc_block():
    return requests.get("http://localhost:5002/get_block").json()
data = get_rc_block()
print(json.dumps(data, indent=2))

txs = data["tx"]
block = data["block"]

# ==== Gửi từng ctx sang DC ====
for tx in txs:
    tx_dict = json.loads(tx) if isinstance(tx, str) else tx
    tx_id   = tx_dict["tx_id"]
    tx_data = tx_dict["tx_data"]

    @log_duration(tx_id, "B5_RC_get_proof")
    def get_proof():
        return requests.post("http://localhost:5005/get_proof",
                             json={"tx": json.dumps(tx_dict), "merkle_root": block["header"]["merkle_root"]}).json()
    pr_rc_dc = get_proof()

    @log_duration(tx_id, "B6_DC_receive_ctx")
    def send_ctx():
        return requests.post("http://localhost:5003/receive_ctx", json={
            "tx": tx_data,
            "tx_hash_id": hash_data(tx_id),
            "tx_hash": hash_data(json.dumps(tx_dict)),
            "proof": pr_rc_dc["proof"],
            "merkle_root": pr_rc_dc["merkle_root"],
            "zk_proof": pr_rc_dc["zk_proof"]
        }).json()
    rc_res = send_ctx()
    print("DC accept?", rc_res["accepted"])


# ==== DC seal block ====
print("\n=== DC Block ===")

@log_duration("tx_all", "B7_DC_dong_block")
def get_dc_block():
    return requests.get("http://localhost:5003/get_block").json()
blk = get_dc_block()
print(json.dumps(blk, indent=2))
