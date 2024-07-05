import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Union, Tuple, Any
from .exceptions import *
from . import __version__


class FortifySSCAPI:
    """
    API object to talk to SSC via REST
    """

    def __init__(self, url: str,  auth: Union[str, Tuple[str, str]], proxies=None, verify=True):
        """
        :param url: url to ssc, including the path. E.g. `https://fortifyssc/ssc`
        :param auth: Authentication, either a token str or a (username, password) tuple
        """
        self.url = url.rstrip('/')
        self._token = None
        self.__user = None
        self.__pass = None
        self.proxies = proxies
        self.verify = verify

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
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"FortifyToken {self._token}",
            "Accept": 'application/json',
            "User-Agent": f"fortifyapi {__version__}"
        })
        # ssc is not reliable
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        self._session.mount('https://', HTTPAdapter(max_retries=retries))
        return self

    def _authorize(self):
        self._token = self.create_token()

    def __exit__(self, type, value, traceback):
        if self.__user and self.__pass:
            self._unauthorize()

    def _unauthorize(self):
        self.revoke_token(self._token)
        self._token = None

    def create_token(self, description: str = 'PySSC Python API', type: str = 'UnifiedLoginToken') -> str:
        """
        Create a token with given username and password. Does not need to be manually called for API to work.
        Must use username:password authentication for this to work

        :param description: The description the token is created with
        :param type: The type of token to create, default being `UnifiedLoginToken`
        :raises AuthException: If we are unable to create a token
        :returns: The token itself
        """
        assert self.__user and self.__pass, "Cannot use token based authentication to create tokens."
        kwargs = dict(
            auth=(self.__user, self.__pass),
            json=dict(type=type, description=description)
        )
        if self.proxies:
            kwargs['proxies'] = self.proxies
        r = requests.post(f"{self.url}/api/v1/tokens", **kwargs)
        if r.status_code != 201:
            raise AuthException(f"Failed to authenticate - {r.status_code} - {r.text}")
        # could store user from the response, not sure why though
        return r.json()['data']['token']

    def revoke_token(self, token: str) -> None:
        """
        Revoke the given token
        Must use username:password authentication for this to work

        :param token: The token to revoke
        :raises AuthException: If we are unable to revoke the token
        """
        assert self.__user and self.__pass, "Cannot use token based authentication to create tokens."
        kwargs = dict(
            auth=(self.__user, self.__pass),
            json=dict(tokens=[token])
        )
        if self.proxies:
            kwargs['proxies'] = self.proxies
        r = requests.post(f"{self.url}/api/v1/tokens/action/revoke", **kwargs)
        if r.status_code != 200:
            raise AuthException(f"Failed to revoke token - {r.status_code} - {r.text}")

    def construct_request(self, method: str, path: str, data: Any) -> dict:
        """
        Construct a request for the bulk request API

        :param method: The HTTP method
        :param path: The relative path to the API endpoint (the `uri` argument)
        :param data: the postData
        """
        return {
            'uri': f"{self.url}/{path.lstrip('/')}",
            'httpVerb': method,
            'postData': data
        }

    def bulk_request(self, reqs):
        """
        :param reqs: The requests generated by py:func:`construct_request`
        """
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
            kwargs['start'] = kwargs['start'] + kwargs['limit']
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
        :param args: Args as a dict
        :param kwargs: The query parameters
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
        return self._request('put', endpoint, json=data)
    
    def put_array(self, endpoint, array):
        return self._request('put', endpoint, json=array)

    def delete(self, endpoint, *args, **kwargs):
        data = args[0] if args else {}
        data = {**data, **kwargs}
        return self._request('delete', endpoint, params=data)

    def _request(self, method: str, endpoint: str, **kwargs):
        if self.proxies:
            kwargs['proxies'] = self.proxies
        if not self.verify:
            kwargs['verify'] = self.verify
        r = self.session.request(method, f"{self.url}/{endpoint.lstrip('/')}", **kwargs)
        if 200 <= r.status_code >= 299:
            if r.status_code == 409:
                raise ResourceNotFound(f"ResponseException - {r.status_code} - {r.text}")
            raise ResponseException(f"ResponseException - {r.status_code} - {r.text}")
        data = r.json()
        #print(f"{method} {endpoint}\n\t{r.text}")
        return data