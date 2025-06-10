from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import os

class DigitalSignature:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.keys_dir = "keys"
        os.makedirs(self.keys_dir, exist_ok=True)

    def generate_keys(self):
        """Генерация пары ключей (приватный и публичный)"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self._save_keys()

    def _save_keys(self):
        """Сохранение ключей в файлы"""
        # Сохраняем приватный ключ
        with open(f"{self.keys_dir}/private_key.pem", "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Сохраняем публичный ключ
        with open(f"{self.keys_dir}/public_key.pem", "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def load_keys(self):
        """Загрузка ключей из файлов"""
        try:
            with open(f"{self.keys_dir}/private_key.pem", "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            with open(f"{self.keys_dir}/public_key.pem", "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            return True
        except FileNotFoundError:
            return False

    def sign_data(self, data: str) -> str:
        """Создание подписи для данных"""
        if not self.private_key:
            raise ValueError("Приватный ключ не загружен")
        
        signature = self.private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, data: str, signature: str) -> bool:
        """Проверка подписи"""
        if not self.public_key:
            raise ValueError("Публичный ключ не загружен")
        
        try:
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            self.public_key.verify(
                signature_bytes,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False