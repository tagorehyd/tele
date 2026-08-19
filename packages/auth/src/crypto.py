import base64, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
class SecretBox:
    def __init__(self, key_b64: str): self.key=base64.b64decode(key_b64)
    @staticmethod
    def generate_key() -> str: return base64.b64encode(AESGCM.generate_key(bit_length=256)).decode()
    def encrypt(self, plaintext: str, aad: bytes=b'tmc') -> str:
        nonce=os.urandom(12); data=AESGCM(self.key).encrypt(nonce, plaintext.encode(), aad)
        return base64.b64encode(nonce+data).decode()
    def decrypt(self, token: str, aad: bytes=b'tmc') -> str:
        raw=base64.b64decode(token); return AESGCM(self.key).decrypt(raw[:12], raw[12:], aad).decode()
    def mask(self, value: str) -> str: return '' if not value else value[:2]+'***'+value[-2:]
