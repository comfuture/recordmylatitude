import urllib2
import urllib

class BaseStore(object):
    jar = {}

    def __init__(self):
        pass

    def get(self, scope, **kwargs):
        """get token string from given scope"""
        return self.jar.get(scope)

    def set(self, scope, value, **kwargs):
        """set token value of scope"""
        self.jar[scope] = value

class FileStore(BaseStore):

    def __init__(self, filename):
        self.filename = filename
        self.load()

    def load(self):
        try:
            with open(self.filename) as r:
                self.jar.update(dict([tuple(line.strip().split(' ', 2))
                    for line in r.readlines()]))
        except IOError, e:
            pass
        
    def save(self):
        content = '\n'.join(['%s %s' % (k, v) for k, v in self.jar.iteritems()])
        try:
            with open(self.filename, 'w') as r:
                r.write(content)
        except IOError, e:
            print "Can't open file '%s' for write" % self.filename

    def set(self, scope, value, **kwargs):
        """save token for scope to file"""
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
        """create authsub authorize url"""
        self.params['next'] = next
        url = '%s?%w'% (self.AUTHSUB_URL, urllib.urlencode(self.params))
        if callback:
            callback(url)
        return url

    def upgrade_token(self):
        """upgrade single token to session token"""
        headers, content = self.request(self.SESSION_TOKEN_URL,
            {'token': self.store.get(self.scope)})
        dummy, self.token = map(lambda s: s.strip(), content.split('='))
        self.store.set(self.scope, self.token)

    def request(self, url, params={}, headers={}):
        """make http request with authsub authorization header"""
        if self.token:
            headers['Authorization'] = 'AuthSub token="%s"' % self.token
        req = urllib2.Request(url, urllib.urlencode(params), headers)
        r = urllib2.urlopen(req)
        return r.headers, r.read()
