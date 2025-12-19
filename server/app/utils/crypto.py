# -*- coding: utf-8 -*-
"""Encryption utilities using AES-256-CBC."""

import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def _derive_key(password: str, salt: bytes = b'salt') -> bytes:
    """Derive a 32-byte key from password using scrypt."""
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt(plaintext: str, key: str) -> str:
    """Encrypt plaintext using AES-256-CBC.
    
    Args:
        plaintext: Text to encrypt
        key: Encryption key/password
        
    Returns:
        Encrypted string in format: iv_hex:ciphertext_hex
    """
    iv = os.urandom(16)
    derived_key = _derive_key(key)
    
    cipher = Cipher(
        algorithms.AES(derived_key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Pad the plaintext
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    
    # Encrypt
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return iv.hex() + ':' + ciphertext.hex()


def decrypt(ciphertext: str, key: str) -> str:
    """Decrypt ciphertext using AES-256-CBC.
    
    Args:
        ciphertext: Encrypted string in format: iv_hex:ciphertext_hex
        key: Encryption key/password
        
    Returns:
        Decrypted plaintext
        
    Raises:
        ValueError: If ciphertext format is invalid
    """
    parts = ciphertext.split(':')
    if len(parts) != 2:
        raise ValueError("Invalid ciphertext format")
    
    iv = bytes.fromhex(parts[0])
    encrypted_data = bytes.fromhex(parts[1])
    derived_key = _derive_key(key)
    
    cipher = Cipher(
        algorithms.AES(derived_key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Decrypt
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Unpad
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    
    return plaintext.decode()
