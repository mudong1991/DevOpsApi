# -*- coding:utf-8 -*-
# Created by Administrator at 2017/3/8 0008
"""
加解密工具单元
"""
import base64

from M2Crypto.EVP import Cipher
from M2Crypto.util import pkcs7_pad

OP_ENCRYPT = 1
OP_DECRYPT = 0
unpad = lambda s: s[0:-ord(s[-1])]  # 去掉填充数据


def aes_api_data_encrypt(data):
    """
    加密api数据
    :param data: 字符串数据等
    :return: base64数据
    """
    key = '!@#$%^&*()_+|%^&'
    iv = '!@#$%^&*()_+|%^&'
    pad_data = pkcs7_pad(data, 16)
    encryptor = Cipher(alg="aes_128_cbc", key=key, iv=iv, op=OP_ENCRYPT, padding=0)
    str = encryptor.update(pad_data)
    str = str + encryptor.final()
    base64str = base64.b64encode(str)
    return base64str


def aes_html_data_decrypt(data):
    """
    解密Html传过来的数据
    :param data: 数据Base64编码
    :return: 解密后的字符串,如果为无效的字符串解密,则返回空串
    """
    key = '!@#$%^&*()_+|%^&'
    iv = '!@#$%^&*()_+|%^&'
    decryptor = Cipher(alg="aes_128_cbc", key=key, iv=iv, op=OP_DECRYPT, padding=0)
    encrypted_data = base64.b64decode(data)
    decrypted_data = decryptor.update(encrypted_data)
    decrypted_data += decryptor.final()

    return unpad(decrypted_data)


if __name__ == '__main__':
    # 测试
    data = "123"
    en_data = aes_api_data_encrypt(data)
    print en_data
    de_data = aes_html_data_decrypt('p3TEgPfBr3z+Isd3UJ6aoA==')
    print de_data
    print len(de_data)
