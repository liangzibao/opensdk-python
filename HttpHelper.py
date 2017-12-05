#!/usr/bin/env python
# -*- coding: utf-8 -*-

__verison__ = '1.0.0'
__author__ = 'liangzibao'

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import gzip
import urllib
import urllib2
import collections
import logging
import json

_HTTP_GET = 0
_HTTP_POST = 1

_METHOD_MAP = { 'GET': _HTTP_GET, 'POST': _HTTP_POST }

class APIClient(object):
    
    def __init__(self, url):
        self._url = str(url)

    def invokeGet(self, **kw):
        r = _http_get(self._url, **kw)
        return r
    
    def invokePost(self, **kw):
        r = _http_post(self._url, **kw)
        return r

    def __getattr__(self, attr):
        if '__' in attr:
            return getattr(self.get, attr)
        return _Callable(self, attr)

class _Executable(object):
    
    def __init__(self, client, method, path):
        self._client = client
        self._method = method
        self._path = path

    def __call__(self, **kw):
        method = _METHOD_MAP[self._method]
        return _http_call('%s%s' % (self,_client.api_rul, self.path), method, **kw)

    def __str__(self):
        return '_Executable (%s %s)' % (self._method, self._path)

    __repr__ = __str__
        

class _Callable(object):
    
    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        if attr == 'get':
            return _Executable(self._client, 'GET', self._name)
        if attr == 'post':
            return _Executable(self,_client, 'POST', self._name)
        name = '%s/%s' % (self._name, attr)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' % self._name

    __repr__ = __str__

def _http_get(url, **kw):
    logging.info('GET %s' % url)
    return _http_call(url, _HTTP_GET, **kw)

def _http_post(url, **kw):
    logging.info('POST %s' % url)
    return _http_call(url, _HTTP_POST, **kw)

def _http_call(url, method, **kw):
    params = None

    params = _encode_params(**kw)
    http_url = '%s?%s' % (url, params) if method == _HTTP_GET else url
    http_body = None if method == _HTTP_GET else params
    req = urllib2.Request(http_url, data = http_body)
    req.add_header('Accept-Encoding', 'gzip')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
    req.add_header('User-Agent', 'LZB/Openapi SDK/v1.0.0(Python)')

    try:
        resp = urllib2.urlopen(req, timeout = 5)
        body = _read_body(resp)
        r = _parse_json(body)
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, r.get('error', ''), r.get('request', ''))
        return r
    except urllib2.HTTPError, e:
        try:
            r = _parse_json(_read_body(e))
        except:
            r = None
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, r.get('error', ''), r.get('request', ''))
        raise e
            


def _encode_params(**kw):
    args = []
    for k, v in kw.iteritems():
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' % (k, urllib.quote(qv)))
        elif isinstance(v, collections.Iterable):
            for i in v:
                qv = i.encode('utf-8') if isinstance(i, unicode) else str(i)
                args.append('%s=%s' % (k, urllib.quote(qv)))
        else:
            qv = str(v)
            args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)

def _read_body(obj):
    using_gzip = obj.headers.get('Content-Encoding', '') == 'gzip'
    body = obj.read()
    if using_gzip:
        gzipper = gzip.GzipFile(fileobj = StringIO(body))
        fcontent = gzipper.read()
        gzipper.close()
        return fcontent
    return body

def _parse_json(s):
    def _obj_hook(pairs):
        o = JsonDict()
        for k, v in pairs.iteritems():
            o[str(k)] = v
        return o
    return json.loads(s, object_hook = _obj_hook)

class JsonDict(dict):

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value

class APIError(StandardError):
    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)
