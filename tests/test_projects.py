from unittest import TestCase
from constants import Constants
from random import randint
from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient, Query

import time


class TestProjects(TestCase):
    c = Constants()

    def test_project_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

        projects = list(client.projects.list())
        self.assertGreater(len(projects), 0)

        proj = projects[0]
        self.assertIsNotNone(proj)
        self.assertIsNotNone(proj['id'])
        self.assertIsNotNone(proj['_href'])

    def test_test(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        projects = list(client.projects.list())
        print(projects[0])

        r = client.projects.test("random name that doesnt exist")
        self.assertFalse(r)

        r = client.projects.test(projects[0]['name'])
        self.assertTrue(r)

    def test_project_get(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        projects = list(client.projects.list())
        r = client.projects.get(projects[0]['id'])
        print(r)
        self.assertEqual(projects[0], r)

    def test_project_update(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        project = list(client.projects.list())[0]
        print(project)
        old_description = project['description']
        self.assertIsNotNone(old_description)

        new_d = f"PySSC Unit Test - Sorry -  {randint(0,100)}"
        project['description'] = new_d
        self.assertEqual(project['description'], new_d)

        project.update()

        nproject = client.projects.get(project['id'])
        print(nproject)
        self.assertIsNotNone(nproject)
        self.assertEqual(new_d, nproject['description'])

    def test_project_upsert(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        version = client.projects.upsert("Unit Test Python", 'upsert')
        self.assertIsNotNone(version)
        #pprint(version)
        try:
            self.assertTrue(version['active'])
            # is it committed?
            self.assertTrue(version['committed'])
        finally:
            version.delete()

    def test_project_query(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        return #TODO: put back in

        client.projects.upsert("Unit Test Python", 'default')
        q = Query().query("name", "Unit Test Python")#.query('createdBy', self.c.username)
        print(q)
        project = list(client.projects.list(q=q))
        print(project)

        self.assertIsNotNone(project)
        self.assertEqual(len(project), 1)

    def test_create_delete_name(self):
        '''
        This is a complex test case that uses a lot of other features.
        '''
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

        client.projects.upsert("Unit Test Python", 'default')

        q = Query().query("name", "Unit Test Python")
        project = list(client.projects.list(q=q))[0]
        id = project['id']
        self.assertIsNotNone(id)
        p = client.projects.get(id)
        self.assertIsNotNone(p)

        project.delete()

        time.sleep(5)

        self.assertRaises(ResponseException, client.projects.get, id)

    def test_project_create(self):
        project_name = 'HealthScan ACL Issues UI Actions'

        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        res = client.projects.upsert(project_name, 'default')
        self.assertIsNotNone(res)
        print(res)
        self.assertEqual(res['project']['name'], project_name)
