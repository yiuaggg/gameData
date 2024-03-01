import time
import string
import base64
import random
from config import SECRET_KEY, API_EXPIRATION
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_aes_gcm(key, data, nonce_len=32):
    """
    AES-GCM加密
    :param key: 密钥。16, 24 or 32字符长度的字符串
    :param data: 待加密字符串
    :param nonce_len: 随机字符串长度
    """
    key = key.encode('utf-8')
    if not isinstance(data, str):
        data = str(data)
    data = data.encode('utf-8')
    # 生成32位长度的随机值，保证相同数据加密后得到不同的加密数据
    nonce = ''.join(random.sample(string.ascii_letters + string.digits, nonce_len))
    nonce = nonce.encode("utf-8")

    # 生成加密器
    cipher = AESGCM(key)
    # 加密数据
    crypt_bytes = cipher.encrypt(nonce, data, associated_data=None)
    return base64.b64encode(nonce + crypt_bytes).decode()


def decrypt_aes_gcm(key, cipher_data, nonce_len=32):
    """
    AES-GCM解密
    :param key: 密钥
    :param cipher_data: encrypt_aes_gcm 方法返回的数据
    :param nonce_len: 随机字符串长度
    :return:
    """
    key = key.encode('utf-8')

    # 进行base64解码
    debase64_cipher_data = base64.b64decode(cipher_data)

    # 提取密文数据
    nonce = debase64_cipher_data[:nonce_len]
    cipher_data = debase64_cipher_data[nonce_len:]

    # 解密数据
    cipher = AESGCM(key)
    plaintext = cipher.decrypt(nonce, cipher_data, associated_data=None)
    return plaintext.decode()


def generate_token(username, expiration=API_EXPIRATION):
    """ 生成token生成token的密钥
    :param username: 生成token的信息
    :param expiration: token有效时间，单位秒
    """
    expiration = int(time.time() + expiration)
    data = {'username': username, 'expiration': expiration}
    return data, encrypt_aes_gcm(SECRET_KEY, data)


def decrypt_token(token):
    """ 解析token """
    data = decrypt_aes_gcm(SECRET_KEY, token)
    return eval(data)
