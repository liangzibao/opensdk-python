#!/usr/bin/env python
# -*- coding: utf-8 -*-

__verison__ = '1.0.0'
__author__ = 'liangzibao'

import base64
import rsa
import json

class RSAHelper(object):

    def encrypt(self, public_key, **params):
        _p = rsa.PublicKey.load_pkcs1(public_key)
        biz_content = self._filter_param(**params)
        biz_content = json.dumps(biz_content)
        # 1024bit key
        default_encrypt_length = 117
        len_content = len(biz_content)
        if len_content < default_encrypt_length:
            return base64.b64encode(rsa.encrypt(biz_content, _p))
        offset = 0
        params_lst = []
        while len_content - offset > 0:
            if len_content - offset > default_encrypt_length:
                params_lst.append(rsa.encrypt(biz_content[offset:offset+default_encrypt_length], _p))
            else:
                params_lst.append(rsa.encrypt(biz_content[offset:], _p))
            offset += default_encrypt_length
        target = ''.join(params_lst)
        ret =  base64.b64encode(target)
        return ret

    def decrypt(self, private_key, biz_content):
        _pri = rsa.PrivateKey.load_pkcs1(private_key)
        biz_content = base64.b64decode(biz_content)
        # 1024bit key
        default_length = 128
        if len(private_key) > 1000:
            default_length = 256
        len_content = len(biz_content)
        if len_content < default_length:
            return rsa.decrypt(biz_content, _pri)
        offset = 0
        params_lst = []
        while len_content - offset > 0:
            if len_content - offset > default_length:
                params_lst.append(rsa.decrypt(biz_content[offset: offset+default_length], _pri))
            else:
                params_lst.append(rsa.decrypt(biz_content[offset:], _pri))
            offset += default_length
        target = ''.join(params_lst)
        return json.loads(target)

    def genSign(self, private_key, **params):
        _pri = rsa.PrivateKey.load_pkcs1(private_key)
        data = self._filter_param(**params)
        data = data.items()
        data.sort()
        sign_str = json.dumps(data)
        sign_str = sign_str.replace('\\', '')

        sign_str = sign_str.replace('[[', '{')
        sign_str = sign_str.replace(']]', '}')
        sign_str = sign_str.replace('\", ', '":')
        sign_str = sign_str.replace('[','');
        sign_str = sign_str.replace('], ', ',');
        sign = rsa.sign(sign_str, _pri, 'SHA-1')
        ret = base64.b64encode(sign)
        return ret

    def checkSign(self, public_key, sign_str, **params):
        _p = rsa.PublicKey.load_pkcs1(public_key)
        data = self._filter_param(**params)
        if 'sign' in data:
            data.pop('sign')
        data = data.items()
        data.sort()
        str = json.dumps(data)
        str = str.replace('\\', '')
        str = str.replace('[[', '{')
        str = str.replace(']]', '}')
        str = str.replace('\", ', '":')
        str = str.replace('[', '');
        str = str.replace('], ', ',');

        sign = base64.b64decode(sign_str)
        return rsa.verify(str, sign, _p)

    def _filter_param(self, **params):
        data = {}
        for k, v in params.iteritems():
            if '' != params[k]:
                data[k] = v
        return data

