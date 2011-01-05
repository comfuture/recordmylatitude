from authsub import Client

class Latitude(Client):

    SCOPE = 'https://www.googleapis.com/auth/latitude'
    API_BASE = 'https://www.googleapis.com/latitude/v1/'

    def __init__(self, key, **kwargs):
        options = dict(location='all', granularity='city', session=1)
        options.update(kwargs)
        Client.__init__(self, self.SCOPE, **options)
        self.key = key
        self.token = self.store.get(self.SCOPE)
        print self.token

    def api(self, what):
        """call api"""
        return self.request('%s%s?key=%s' % (self.API_BASE, what, self.key,))

    def current_location(self):
        """returns current location json string"""
        headers, content = self.api('currentLocation')
        return content

