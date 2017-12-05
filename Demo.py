#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from Client import *

__verison__ = '1.0.0'
__author__ = 'liangzibao'

class Demo(object):
    def __init__(self, base_url, private_key, lzb_public_key, app_key):
        self._base_url = base_url
        self._private_key = private_key
        self._lzb_public_key = lzb_public_key
        self._app_key = app_key

    def create(self, **common_params):
        client = Client(self._base_url, self._private_key, self._lzb_public_key, self._app_key)
        service_name = 'lzb.policy.create'
        result = client.invoke(service_name, **common_params)
        return result
        

    def get_info(self, **common_params):
        client = Client(self._base_url, self._private_key, self._lzb_public_key, self._app_key)
        service_name = 'lzb.policy.info'
        result = client.invoke(service_name, **common_params)
        return result


if __name__ == '__main__':
    base_url = 'http://openapi.liangzibao.com.cn/getway/do' # Sandbox
    #base_url = 'http://openapi.liangzibao.cn/getway/do' # Product
    
    # 量子保公钥，可以登录量子保SaaS平台获取
    lzbpub = """-----BEGIN RSA PUBLIC KEY-----
    xxxxxxx
    xxxxx
    xxxx
    -----END RSA PUBLIC KEY-----"""
   
    # 商户公钥
    pubkey = """-----BEGIN RSA PUBLIC KEY-----
    xxxx
    xxxx
    xxxx
    -----END RSA PUBLIC KEY-----"""

    # 商户私钥
    prikey = """-----BEGIN RSA PRIVATE KEY-----
    ***
    ***
    ****
    -----END RSA PRIVATE KEY-----"""

    app_key = '*****' # TODO 量子保提供的app_key 可登陆量子保SaaS平台获取

    demo = Demo(base_url, prikey, lzbpub, app_key)
    product_mask = '***' # TODO 量子保提供的product_mask 可登陆量子保SaaS平台获取

    params = {}
    params['product_mask'] = product_mask
    params['mer_order_id'] = '123_abcd'
    params['mer_order_uuid'] = 'uuid_123456'
    currentTime = int(time.time())
    params['start_time'] = str(currentTime + 600)
    params['end_time'] = str(currentTime + 86400 * 1.5)

    insure_user_info = {}
    insure_user_info['user_id'] = '888'
    insure_user_info['name'] = '发发发'
    insure_user_info['idno'] = 'xxxxxxxxxxxxxxxx'
    insure_user_info['cellphone'] = '16810125281'
    params['insure_user_info'] = insure_user_info

    mer_order_info = {}
    mer_order_info['city'] = '北京'
    mer_order_info['country'] = '中国'
    params['mer_order_info'] = mer_order_info
    ret = demo.create(**params)
    print ret

    policy_id = ret['policy_id']
    
    params = {'product_mask':product_mask, 'policy_id':policy_id}
    ret = demo.get_info(**params)
    print ret
