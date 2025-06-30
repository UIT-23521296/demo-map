from py_ecc.bls import G2ProofOfPossession as bls
import os

# Hằng số order cho BLS12-381
BLS12_381_ORDER = int("52435875175126190479447740508185965837690552500527637822603658699938581184512")

def generate_private_key():
    return int.from_bytes(os.urandom(32), 'big') % BLS12_381_ORDER

def get_public_key(sk):
    return bls.SkToPk(sk)

def sign_message(sk, message: str):
    return bls.Sign(sk, message.encode())

def verify_signature(pk, message: str, signature):
    return bls.Verify(pk, message.encode(), signature)

def aggregate_signatures(signatures: list):
    return bls.Aggregate(signatures)

def verify_aggregate(pubkeys: list, message: str, agg_sig):
    return bls.AggregateVerify(pubkeys, [message.encode()] * len(pubkeys), agg_sig)
