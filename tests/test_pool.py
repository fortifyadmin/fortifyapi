from unittest import TestCase, skip
from pprint import pprint
from constants import Constants
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

    @skip("Non-idempotent test, skipping")
    def test_unassign_worker(self):
        unassigned_pool = '00000000-0000-0000-0000-000000000001'
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        worker = [worker['uuid'] for worker in client.workers.list() if worker['totalPhysicalMemory'] < 30000000000]
        unassign = client.pools.assign(worker_uuid=worker[0], pool_uuid=unassigned_pool)
        print(f"{unassign['status']} worker {worker[0]} has been unassigned to the unassigned pool {unassigned_pool}")
        return worker[0]

    @skip("Flaky test never worked, corrected but skipped as we have no workers")
    def test_assign_worker(self):
        pool_name = 'unit_test_pool_zz'
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        existing_pool = [pool['name'] for pool in client.pools.list()]
        print("existing pools", existing_pool)
        if pool_name not in existing_pool:
            client.pools.create(pool_name)

        unassigned_worker = [worker['uuid'] for worker in client.workers.list() if worker['cloudPool']['name'] == 
                             "Unassigned Sensors Pool"]
        self.assertNotEqual(unassigned_worker, [], "Found no unassigned workers, cannot test assignment")
        unit_test_pool = client.pools.list(q=Query().query('name', pool_name))
        pool_uuid = next(unit_test_pool)['uuid']
        self.assertIsNotNone(pool_uuid)
        client.pools.assign(worker_uuid=unassigned_worker, pool_uuid=pool_uuid)
        worker = [worker['uuid'] for worker in client.workers.list() if worker['cloudPool']['name'] == unit_test_pool]
        self.assertNotEqual(len(worker), 0)



