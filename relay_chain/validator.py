from bls_utils import generate_private_key, sign_message, get_public_key

class ValidatorNode:
    def __init__(self, name):
        self.name = name
        self.sk = generate_private_key()
        self.pk = get_public_key(self.sk)

    def sign(self, message: str):
        return sign_message(self.sk, message)
    
    def get_public_key(self) -> str:
        return self.pk.hex()
