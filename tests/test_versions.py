from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient, Query


class TestVersions(TestCase):
    c = Constants()

    def test_project_version_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)

        for project in client.projects.list():
            self.assertIsNotNone(project)

            versions = list(project.versions.list())
            pprint(versions[0])
            self.assertIsNotNone(versions)
            self.assertGreater(len(versions), 0)

            # try to get it too
            nv = project.versions.get(versions[0]['id'])
            self.assertIsNotNone(nv)
            pprint(nv)
            self.assertDictEqual(versions[0], nv)
            break

    def test_project_version_query(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        project = list(client.projects.list())[0]
        # for this arbitrary version, let's QUERY using it
        version = list(project.versions.list())[-1]
        pprint(version)

        self.assertIsNotNone(version['name'])
        v = list(project.versions.list(q=Query().query('name', version['name'])))
        self.assertIsNotNone(v)
        self.assertGreater(len(v), 0)

    def test_issue_summary(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        project = list(client.projects.list())[0]
        version = list(project.versions.list())[0]
        summary = version.issue_summary()
        self.assertIsNotNone(summary)
        print(summary)
        self.assertGreater(len(summary), 0)
        self.assertIsNotNone(summary[0]['name'])

    def test_attributes(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        project = list(client.projects.list())[0]
        version = list(project.versions.list())[0]

        attributes = list(version.attributes.list())
        self.assertIsNotNone(attributes)
        self.assertGreater(len(attributes), 0)
        print(attributes[0])
        self.assertIsNotNone(attributes[0]['attributeDefinitionId'])

    def test_all_version_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        all_versions = list(client.list_all_project_versions())
        self.assertGreater(len(all_versions), 10)
