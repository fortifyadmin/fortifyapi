from unittest import TestCase
from constants import Constants
from fortifyapi import FortifySSCAPI


class TestAPI(TestCase):
    c = Constants()

    def test_api_init(self):
        api = FortifySSCAPI(self.c.url, self.c.credentials)
        if self.c.proxies:
            api.proxies = self.c.proxies

    def test_api_with(self):
        fapi = FortifySSCAPI(self.c.url, self.c.token)
        if self.c.proxies:
            fapi.proxies = self.c.proxies
        with fapi as api:
            self.assertIsNotNone(api)

    def test_api_auth(self):
        fapi = FortifySSCAPI(self.c.url, self.c.credentials)
        if self.c.proxies:
            fapi.proxies = self.c.proxies

        self.assertIsNone(fapi._token)
        fapi._authorize()
        self.assertIsNotNone(fapi._token)
        fapi._unauthorize()
        self.assertIsNone(fapi._token)

    def test_api_get(self):
        fapi = FortifySSCAPI(self.c.url, self.c.credentials)
        if self.c.proxies:
            fapi.proxies = self.c.proxies
        with fapi as api:
            r = api.get('/api/v1/projects', start=500)
            self.assertIsNotNone(r)

    def test_api_get_token(self):
        fapi = FortifySSCAPI(self.c.url, self.c.token)
        if self.c.proxies:
            fapi.proxies = self.c.proxies
        with fapi as api:
            r = api.get('/api/v1/projects', start=500)
            self.assertIsNotNone(r)

    def test_page(self):
        fapi = FortifySSCAPI(self.c.url, self.c.token)
        if self.c.proxies:
            fapi.proxies = self.c.proxies
        with fapi as api:
            # let's see how long this is...
            count = api.get('/api/v1/projects', limit=0)['count']
            self.assertGreater(count, 0)

            results = []

            for e in api.page_data('/api/v1/projects', limit=5):
                results.append(e)

            self.assertGreater(len(results), 0)
            self.assertEqual(count, len(results))


