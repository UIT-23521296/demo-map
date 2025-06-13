from blockchains.source_chain import SourceChain
from blockchains.destination_chain import DestinationChain
from relay_chain.relay_chain import RelayChain
from relay_chain.validator import ValidatorNode
from sc_to_rc import SCtoRCProver
from rc_to_dc import RCtoDCProver

# Khởi tạo các chuỗi và validator
sc = SourceChain("chainA")
dc = DestinationChain("chainB")
validators = [ValidatorNode(f"v{i}") for i in range(4)]
rc = RelayChain(validators)

# Prover giữa SC và RC
sc_to_rc = SCtoRCProver(sc, rc)

# Gửi giao dịch từ SC → RC
tx_id = "tx_001"
receiver = "chainB"
result = sc_to_rc.send_transaction({"message": "Send 100 MAP"}, receiver, tx_id)

if result["accepted"]:
    # Prover giữa RC và DC
    rc.generate_block()
    rc_to_dc = RCtoDCProver(rc, dc)
    rc_to_dc.send_to_destination( {"message": "Send 100 MAP"}, result["tx_hash"], tx_id)

# Đóng block ở DestinationChain
dc.generate_block()

# In kết quả
print("\n🔗 SourceChain block:", sc.get_latest_block())
print("🔁 RelayChain block:", rc.get_latest_block())
print("✅ DestinationChain block:", dc.get_latest_block())
