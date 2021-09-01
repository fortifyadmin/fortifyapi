import requests
from .exceptions import *


class FortifySSCAPI:

    def __init__(self, url,  auth):
        self.url = url.rstrip('/')
        self._token = None
        self.__user = None
        self.__pass = None

        if isinstance(auth, str):
            self._token = auth
        elif len(auth) == 2:
            # (user,pass)
            self.__user = auth[0]
            self.__pass = auth[1]
        else:
            raise AuthException("No valid authentication information")

    def __enter__(self):
        if self._token is None:
            self._authorize()
        return self

    def _authorize(self):
        self._token = self.create_token()

    def __exit__(self, type, value, traceback):
        if self.__user and self.__pass:
            self._unauthorize()

    def _unauthorize(self):
        self.revoke_token(self._token)
        self._token = None

    def create_token(self, description='PySSC Python API', type='UnifiedLoginToken'):
        r = requests.post(f"{self.url}/api/v1/tokens",
                          auth=(self.__user, self.__pass),
                          json=dict(type=type, description=description))
        if r.status_code != 201:
            raise AuthException(f"Failed to authenticate - {r.status_code} - {r.text}")
        # could store user from the response, not sure why though
        return r.json()['data']['token']

    def revoke_token(self, token):
        r = requests.post(f"{self.url}/api/v1/tokens/action/revoke",
                          auth=(self.__user, self.__pass),
                          json=dict(tokens=[token]))
        if r.status_code != 200:
            raise AuthException(f"Failed to revoke token - {r.status_code} - {r.text}")

    def construct_request(self, method, path, data):
        return {
            'uri': f"{self.url}/{path}",
            'httpVerb': method,
            'postData': data
        }

    def bulk_request(self, reqs):
        return self.post('/api/v1/bulk', requests=reqs)

    def page_data(self, endpoint, **kwargs):
        if 'start' not in kwargs:
            kwargs['start'] = 0
        if 'limit' not in kwargs:
            kwargs['limit'] = 200  # default

        r = self.get(endpoint, **kwargs)

        for e in r['data']:
            yield e

        data_len = len(r['data'])
        count = r['count']

        if (data_len + kwargs['start']) < count:
            print('poop')
            kwargs['start'] = kwargs['start'] + kwargs['limit']
            print(f"new start {kwargs['start']}")
            for e in self.page_data(endpoint, **kwargs):
                yield e

    def get(self, endpoint, *args, **kwargs):
        """
        The available query parameters are:

        * q - field name + value pair that filters results
        * fields - comma-delimited list of fields to include in response
        * embed - item detail links to traverse and embed in the current response
        * orderby - field name by which to order results
        * start - used by paging to specify first item to retrieve
        * limit - used by paging to determine page size (defaults to 200 items)
        * groupby - used to group results

        :param endpoint:
        :param kwargs:
        :return:
        """
        data = args[0] if args else {}
        data = {**data, **kwargs}
        return self._request('get', endpoint, params=data)

    def post(self, endpoint, *args, **kwargs):
        data = args[0] if args else {}
        data = {**data, **kwargs}
        return self._request('post', endpoint, json=data)

    def put(self, endpoint, *args, **kwargs):
        data = args[0] if args else {}
        data = {**data, **kwargs}
        print(data)
        return self._request('put', endpoint, json=data)

    def delete(self, endpoint, *args, **kwargs):
        data = args[0] if args else {}
        data = {**data, **kwargs}
        return self._request('delete', endpoint, params=data)

    def _request(self, method, endpoint, **kwargs):
        headers = dict(Authorization=f"FortifyToken {self._token}", Accept='application/json')
        r = requests.request(method, f"{self.url}/{endpoint.lstrip('/')}", headers=headers, **kwargs)
        if 200 <= r.status_code >= 299:
            if r.status_code == 409:
                raise ResourceNotFound(f"ResponseException - {r.status_code} - {r.text}")
            raise ResponseException(f"ResponseException - {r.status_code} - {r.text}")
        data = r.json()
        #if '_href' in data:
        #    del data['_href']
        # some things include link data... why just some? get rid of it all.
        #if 'links' in data:
        #    del data['links']
        return data
