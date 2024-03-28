import time
import string
import base64
import random

import db
from config import SECRET_KEY, API_EXPIRATION
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
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


def get_token():
    """
    获取token
    :return:
    """
    old_token = db.Redis(0).get_value('token')
    if old_token:
        return old_token
    else:
        username = 'livehouse'
        password = 'livehouse@123'
        driver_path = r'./chromedriver'
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')  # 无头浏览器
        option.add_argument('--disable-gpu')  # 不需要GPU加速
        option.add_argument('--no-sandbox')  # 无沙箱
        driver = webdriver.Chrome(options=option, service=Service(driver_path))
        driver.get('https://www.gekipachi.com/index')
        time.sleep(4)
        # 登录
        try:
            login_btn = driver.find_element(By.XPATH, '//button[@class="btn lore poke-blue mr-8px"]')
            if login_btn:
                login_btn.click()
            username_input = driver.find_element(By.XPATH, '//input[@type="text"]')
            username_input.send_keys(username)
            password_input = driver.find_element(By.XPATH, '//input[@type="password"]')
            password_input.send_keys(password)
            time.sleep(1)
            button = driver.find_element(By.XPATH, '//div[@class="my-30px"]/button')
            button.click()
            time.sleep(2)
            active_ele = driver.find_element(By.XPATH, '//section[@class="game"]//button[@class="more"]')
            if active_ele:
                active_ele.click()
                time.sleep(3)
                url = driver.current_url
                token = url.split('token=')[1].split('%26')[0]
            else:
                token = ""
        except Exception as e:
            print(e)
            token = ""
        if token:
            db.Redis(0).insert_data('token', token, ex=36000)
        return token


if __name__ == '__main__':
    get_token()
