from bls_utils import verify_aggregate, aggregate_signatures

class ConsensusEngine:
    def __init__(self, validators: list):
        self.validators = validators

    def commit_tx(self, tx_id: str, tx_list: list, merkle_root: str):
        message = merkle_root
        signatures = []
        pubkeys = []

        for v in self.validators:
            sig = v.sign(message)
            signatures.append(sig)
            pubkeys.append(v.pk)

        agg_sig = aggregate_signatures(signatures)

        is_valid = verify_aggregate(pubkeys, message, agg_sig)
        if not is_valid:
            print("❌ Aggregate signature invalid")
            return False, None, None

        return True, agg_sig.hex(), [pk.hex() for pk in pubkeys]
