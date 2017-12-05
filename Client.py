#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
from RSAHelper import *
from HttpHelper import *

__verison__ = '1.0.0'
__author__ = 'liangzibao'

class Client(object):
    def __init__(self, base_url, private_key, lzb_public_key, app_key):
        self._base_url = base_url
        self._private_key = private_key
        self._lzb_public_key = lzb_public_key
        self._app_key = app_key

    def invoke(self, service_name, **biz_content):
        rsa_object = RSAHelper()
        biz_content = rsa_object.encrypt(self._lzb_public_key, **biz_content)

        public_params = {
            'service_name':service_name,
            'app_key':self._app_key,
            'version':'1.0.0', 
            'format':'JSON',
            'charset':'UTF-8',
            'sign_type':'RSA',
            'timestamp':str(int(time.time())),
            'biz_content':biz_content
        }

        sign = rsa_object.genSign(self._private_key, **public_params)
        public_params['sign'] = sign

        http_object = APIClient(self._base_url)
        res = http_object.invokePost(**public_params)

        if 'ret_code' not in res or 200 != res['ret_code']:
            raise APIError(res.error_code, res.get('error', ''), res.get('request', ''))
        ret = self._verify_sign(**res)
        return ret

    def _verify_sign(self, **common_params):
        rsa_object = RSAHelper()
        sign_str = str(common_params.get('sign'))

        request_time = str(common_params.get('timestamp'))
        common_params.pop('timestamp')
        common_params['timestamp'] = request_time
        
        ret_code = str(common_params.get('ret_code'))
        common_params.pop('ret_code')
        common_params['ret_code'] = ret_code
        
        if False == rsa_object.checkSign(self._lzb_public_key, sign_str, **common_params):
            raise APIError(res.error_code, res.get('error', ''), res.get('request', ''))
    
        ret_params = rsa_object.decrypt(self._private_key, common_params['biz_content'])
        if False == ret_params:
            raise APIError(res.error_code, res.get('error', ''), res.get('request', ''))
        return ret_params

class APIError(StandardError):
    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)

