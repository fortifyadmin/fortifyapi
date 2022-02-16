from unittest import TestCase
from constants import Constants
from fortifyapi import FortifySSCClient
from fortifyapi.client import Project


class TestClient(TestCase):
    c = Constants()

    def test_client_init(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.assertIsNotNone(client)

    def test_engine_types(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

        res = list(client.list_engine_types())
        print(res)
        self.assertGreater(len(res), 0)
        self.assertIsNotNone(res[0]['name'])
        self.assertIsNotNone(res[0].parent)

    def test_create(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        project = Project(client.api)
        self.assertIsNotNone(project)
        self.assertFalse('id' in project)
        project['id'] = 'test'
        self.assertTrue('id' in project)
        self.assertEqual(project['id'], 'test')

        project = Project(client.api, {'test': True})
        self.assertTrue('test' in project)
        self.assertTrue(project['test'])

    def test_ssc_object(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        project = Project(client.api)
        self.assertEqual(str(project), "<class 'fortifyapi.client.Project'>({})")
        project.foo = False
        project['bar'] = True
        self.assertEqual(str(project), "<class 'fortifyapi.client.Project'>({'bar': True})")

