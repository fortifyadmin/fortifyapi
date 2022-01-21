from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient, Query


class TestPools(TestCase):
    c = Constants()

    def test_pool_list_get(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        pools = list(client.pools.list())
        self.assertIsNotNone(pools)
        self.assertNotEqual(len(pools), 0)

        pool = pools[0]

        #pprint(pool)

        uuid = pool['uuid']

        self.assertIsNotNone(uuid)

        got_pool = client.pools.get(uuid)
        self.assertIsNotNone(got_pool)
        #print(got_pool)
        self.assertEqual(uuid, got_pool['uuid'])

        # test query
        pools = list(client.pools.list(q=Query().query('name', 'Default Pool')))
        self.assertIsNotNone(pools)
        self.assertEqual(1, len(pools))

    def test_pool_create_delete(self):
        pool_name = 'unit_test_pool_zz'
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        # assert that the pool doesn't already exist
        pools = list(client.pools.list(q=Query().query('name', pool_name)))
        self.assertIsNotNone(pools)
        self.assertEqual(0, len(pools))

        new_pool = client.pools.create(pool_name)
        pprint(new_pool)
        self.assertIsNotNone(new_pool)

        pools = list(client.pools.list(q=Query().query('name', pool_name)))
        self.assertIsNotNone(pools)
        self.assertEqual(1, len(pools))

        new_pool.delete()

        pools = list(client.pools.list(q=Query().query('name', pool_name)))
        self.assertIsNotNone(pools)
        self.assertEqual(0, len(pools))

    def test_list_jobs(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        pools = list(client.pools.list())
        self.assertIsNotNone(pools)
        self.assertNotEqual(len(pools), 0)
        jobs = list(pools[0].jobs())
        self.assertIsNotNone(jobs)



