# coding: utf-8
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import zlib
import base64

# KEY = os.urandom(32)

KEY = b")\xa8\xd1u\xb5\xa2\x84:6\\@\x93\x02\x17E\x15\x8c\x93\xae\x88\xc2\x8ds\xc5\xe4\x8cTU\x11\xbb\xd8\x05"


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
