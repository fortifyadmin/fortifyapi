from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient


class TestPools(TestCase):
    c = Constants()

    def test_pool_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        pools = list(client.pools.list())
        self.assertIsNotNone(pools)
        self.assertNotEqual(len(pools), 0)

        pool = pools[0]

        pprint(pool)

        uuid = pool['uuid']

        self.assertIsNotNone(uuid)
