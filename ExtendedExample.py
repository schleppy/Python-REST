#!/usr/bin/python

import REST_Connect
import config
import os

try:
    import json
except:
    import simplejson as json

class Connection(REST_Connect.Connection):

    @classmethod
    def factory(self, key):
        _cfg = config.Config(file(os.path.join(os.path.dirname(__file__), 'example.cfg')))
        _conn = _cfg.connection
        return Connection(base_url = "%s://%s" %(_conn.scheme, _conn[key]))

    def __init__(self, base_url, username=None, password=None):
        super(Connection, self).__init__(base_url, username, password)

    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}):
        if body:
            body = json.dumps(body)
        response = super(Connection, self).request(resource, method, args, body, filename, headers)
        body = response['body']
        headers = response['headers']
        content_type = headers['content-type']
        if content_type == "application/json":
            body = json.loads(body)

        return {'headers':response['headers'], 'body':body}

