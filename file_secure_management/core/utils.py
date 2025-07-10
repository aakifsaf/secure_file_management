from cryptography.fernet import Fernet
import base64
import os

class FileEncryptor:
    @staticmethod
    def generate_key():
        """Generate a secure Fernet key"""
        return Fernet.generate_key()

    @staticmethod
    def encrypt_file(file_content, key):
        """Encrypt file content using Fernet"""
        fernet = Fernet(key)
        encrypted = fernet.encrypt(file_content)
        return {
            'encrypted_content': base64.b64encode(encrypted).decode('utf-8'),
            'key': base64.b64encode(key).decode('utf-8')
        }

    @staticmethod
    def _safe_b64decode(data):
        """Safely decode base64 string with correct padding"""
        data = data.strip()
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.b64decode(data)

    @staticmethod
    def decrypt_file(encrypted_data, key):
        """Decrypt file content using Fernet"""
        try:
            encrypted_content = encrypted_data['encrypted_content']
            encrypted_bytes = FileEncryptor._safe_b64decode(encrypted_content)
            key_bytes = FileEncryptor._safe_b64decode(key)
            fernet = Fernet(key_bytes)
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")