from cryptography.fernet import Fernet
import base64
from config import settings


class TokenEncryption:
    def __init__(self):
        # Menggunakan encryption key dari environment variable
        key = settings.encryption_key.encode()
        # Pastikan key memiliki panjang yang tepat untuk Fernet
        key = base64.urlsafe_b64encode(key[:32].ljust(32, b'0'))
        self.fernet = Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """
        Enkripsi bot token
        """
        encrypted_token = self.fernet.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted_token).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Dekripsi bot token
        """
        encrypted_data = base64.urlsafe_b64decode(encrypted_token.encode())
        decrypted_token = self.fernet.decrypt(encrypted_data)
        return decrypted_token.decode()


# Instance global untuk digunakan di seluruh aplikasi
token_encryption = TokenEncryption()