import getpass
import os

try:
    import yaml
except ImportError:
    yaml = None


class Constants(object):
    CONF_FILE = 'settings-test.yaml'

    _url = None
    _username = 'admin'

    def __init__(self, conf=None):
        if conf:
            self.CONF_FILE = conf
        try:
            if yaml:
                true_path = os.path.abspath(os.path.join(__file__, '../..', self.CONF_FILE))
                with open(true_path, 'r') as f:
                    self._settings = yaml.load(f, Loader=yaml.FullLoader)
            else:
                self._settings = {}
        except:
            self._settings = {}

        try:
            # Attempt to pull from environment
            self._settings['ssc_url'] = os.environ['PYSSC_URL']
            self._settings['username'] = os.environ['PYSSC_USERNAME']
            self._settings['password'] = os.environ['PYSSC_PASSWORD']
            self._settings['token'] = os.environ['PYSSC_TOKEN']
        except:
            pass

    @property
    def password(self):
        if 'password' in self._settings:
            self._password = self._settings['password']
        try:
            with open('.password','r') as f:
                self._password = f.read().strip()
        except:
            pass
        if not hasattr(self, '_password'):
            self._password = getpass.getpass('\nPassword: ')
        return self._password

    @property
    def username(self):
        if 'username' in self._settings:
            return self._settings['username']
        return self._username

    @property
    def credentials(self):
        return (self.username, self.password)

    @property
    def token(self):
        if 'token' in self._settings:
            return self._settings['token']

        return None

    @property
    def url(self):
        if 'ssc_url' in self._settings:
            return self._settings['ssc_url']
        return self._url

    @property
    def proxies(self):
        if 'proxies' in self._settings:
            return self._settings['proxies']
        return None

    def setup_proxy(self, client):
        if self.proxies:
            client._api.proxies = self.proxies
