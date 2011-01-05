import urllib2
import urllib

class BaseStore(object):
    jar = {}

    def __init__(self):
        pass

    def get(self, scope, **kwargs):
        return self.jar.get(scope)

    def set(self, scope, value, **kwargs):
        self.jar[scope] = value

class FileStore(BaseStore):

    def __init__(self, filename):
        self.filename = filename
        self.load()

    def load(self):
        with open(self.filename) as r:
            self.jar.update(dict([tuple(line.strip().split(' ', 2))
                for line in r.readlines()]))
    
    def save(self):
        content = '\n'.join(['%s %s' % k, v for k, v in self.jar.iteritems()])
        with open(self.filename, 'w') as r:
            r.write(content)

    def get(self, scope, **kwargs):
        return self.jar.get(scope)
        
    def set(self, scope, value, **kwargs):
        self.jar[scope] = value
        self.save()

class Client(object):

    AUTHSUB_URL = 'https://www.google.com/accounts/AuthSubRequest'
    SESSION_TOKEN_URL = 'https://www.google.com/accounts/AuthSubSessionToken'

    def __init__(self, scope, store=None, **kwargs):
        self.store = store or BaseStore()
        self.params = {}
        self.scope = self.params['scope'] = scope
        self.params.update(kwargs)

    def auth(self, next, callback=None):
        self.params['next'] = next
        url = '%s?%w'% (self.AUTHSUB_URL, urllib.urlencode(self.params))
        if callback:
            callback(url)
        return url

    def upgrade_token(self):
        storage = FileAuthSubStore()
        headers, content = self.request(self.SESSION_TOKEN_URL,
            {'token': self.store.get(self.scope)})
        dummy, self.token = map(lambda s: s.strip(), content.split('='))
        self.store.set(self.scope, self.token)

    def callback(self):
        pass

    def request(self, url, params={}, headers={}):
        if self.token:
            headers['Authorization'] = 'AuthSub token="%s"' % self.token
        req = urllib2.Request(url, urllib.urlencode(params), headers)
        r = urllib2.urlopen(req)
        return r.headers, r.read()
