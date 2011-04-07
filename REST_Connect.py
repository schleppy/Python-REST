#!/usr/bin/env python

__author__ = "Sean Berry <sberry@2advanced.com>"
__version__ = '1.0'

import httplib2
import urlparse
import urllib
import base64
from base64 import encodestring
from MimeTypes import *
import MimeTypes
from cStringIO import StringIO

class Connection(object):
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.username = username
        m = mimeTypes()
        self.mimetypes = m.getDictionary()

        self.url = urlparse.urlparse(base_url)

        (scheme, netloc, path, query, fragment) = urlparse.urlsplit(base_url)

        self.scheme = scheme
        self.host = netloc
        self.path = path

        self.h = httplib2.Http(".cache")
        self.h.follow_all_redirects = True
        if username and password:
            self.h.add_credentials(username, password)

    def get(self, resource, args = None, headers={}):
        return self.request(resource, "get", args, headers=headers)

    def delete(self, resource, args = None, headers={}):
        return self.request(resource, "delete", args, headers=headers)

    def head(self, resource, args = None, headers={}):
        return self.request(resource, "head", args, headers=headers)

    def post(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, "post", args , body = body, filename=filename, headers=headers)

    def put(self, resource, args = None, body = None, filename=None, headers={}):
        return self.request(resource, "put", args , body = body, filename=filename, headers=headers)

    def get_content_type(self, filename):
        extension = filename.split('.')[-1]
        guessed_mimetype = self.mimetypes.get(extension, mimetypes.guess_type(filename)[0])
        return guessed_mimetype or 'application/octet-stream'

    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}):
        params = None
        path = resource
        headers['User-Agent'] = 'Basic Agent'
        BOUNDARY = u'42b6e4a2f239d809df2c9c3602d463f2'
        CRLF = u'\r\n'
        if filename and body:
            fn = open(filename ,'r')
            chunks = fn.read()
            fn.close()
            # Attempt to find the Mimetype
            content_type = self.get_content_type(filename)
            headers['Content-Type']='multipart/form-data; boundary='+BOUNDARY
            encode_string = StringIO()
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + CRLF)
            encode_string.write(u'Content-Disposition: form-data; name="file"; filename="%s"' % filename)
            encode_string.write(CRLF)
            encode_string.write(u'Content-Type: %s' % content_type + CRLF)
            encode_string.write(CRLF)
            encode_string.write(body)
            encode_string.write(CRLF)
            encode_string.write(u'--' + BOUNDARY + u'--' + CRLF)
            body = encode_string.getvalue()
            headers['Content-Length'] = str(len(body))
        elif body:
            if not headers.get('Content-Type', None):
                headers['Content-Type']='application/json'
            headers['Content-Length'] = str(len(body)) 
        else: 
            if not headers.get('Content-Type', None):
                headers['Content-Type']= 'application/json'

        if args:
            path += u"?" + urllib.urlencode(args)

        request_path = []
        if self.path != "/":
            if self.path.endswith('/'):
                request_path.append(self.path[:-1])
            else:
                request_path.append(self.path)
            if path.startswith('/'):
                request_path.append(path[1:])
            else:
                request_path.append(path)

        resp, body = self.h.request(u"%s://%s%s" % (self.scheme, self.host, u'/'.join(request_path)), method.upper(), body=body, headers=headers )
        return {u'headers':resp, u'body':body}

if __name__ == "__main__":
	conn = Connection("http://www.google.com")
	print conn.get("/")


