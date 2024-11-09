from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import zlib
import base64

KEY = os.urandom(32)


# AES-GCM加密函数
def encrypt_str(plain_text: str, key=KEY) -> str:
    # 压缩原始数据
    compressed_data = zlib.compress(plain_text.encode())

    # 生成随机的IV（初始化向量）
    iv = os.urandom(12)  # GCM推荐的12字节IV长度

    # 创建AES-GCM加密器
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # 加密数据
    encrypted_data = encryptor.update(compressed_data) + encryptor.finalize()

    # 获取GCM模式的标签（authentication tag）
    tag = encryptor.tag

    # 将IV、标签和加密数据拼接，使用Base64编码成字符串返回
    encrypted_message = base64.b64encode(iv + tag + encrypted_data).decode()

    encrypted_message = encrypted_message.replace(
        "/", "_"
    )  # 为了在URL中使用，将/替换为_

    return encrypted_message


# AES-GCM解密函数
def decrypt_str(encrypted_message: str, key=KEY) -> str:

    encrypted_message = encrypted_message.replace("_", "/")  # 将_替换回/
    # 解码Base64字符串并提取IV和标签
    encrypted_data = base64.b64decode(encrypted_message)
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    encrypted_data = encrypted_data[28:]

    # 创建AES-GCM解密器
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    # 解密数据
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # 解压数据
    plain_text = zlib.decompress(decrypted_data).decode()

    return plain_text


if __name__ == "__main__":

    # 示例
    # key = os.urandom(32)  # 32字节的密钥（AES-256）
    plain_text = "This is a secret message that we want to encrypt and keep short."

    # 加密
    encrypted_message = encrypt_str(plain_text)
    print(f"Encrypted (Base64): {encrypted_message}")

    # 解密
    decrypted_text = decrypt_str(encrypted_message)
    assert decrypted_text == plain_text
    print(f"Decrypted: {decrypted_text}")
