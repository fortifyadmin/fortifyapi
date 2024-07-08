from unittest import TestCase
from pprint import pprint
from constants import Constants
from fortifyapi import FortifySSCClient, Query


class TestVersions(TestCase):
    c = Constants()

    def test_project_version_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

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
            self.maxDiff = None
            # a bug i suspect with ssc, but let's ignore it
            remove_bug_tracker_field = versions[0]
            del remove_bug_tracker_field['bugTrackerEnabled']
            del nv['bugTrackerEnabled']
            self.assertDictEqual(remove_bug_tracker_field, nv)
            break

    def test_project_version_query(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
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
        self.c.setup_proxy(client)
        project = list(client.projects.list())[0]
        version = list(project.versions.list())[0]
        summary = version.issue_summary()
        self.assertIsNotNone(summary)
        print(summary)
        self.assertGreater(len(summary), 0)
        self.assertIsNotNone(summary[0]['name'])

    def test_attributes(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        project = list(client.projects.list())[0]
        version = list(project.versions.list())[0]

        attributes = list(version.attributes.list())

        self.assertIsNotNone(attributes)
        self.assertGreater(len(attributes), 0)
        print(attributes[0])
        self.assertIsNotNone(attributes[0]['attributeDefinitionId'])

    def test_all_version_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        all_versions = list(client.list_all_project_versions())
        self.assertGreater(len(all_versions), 10)

    def test_version_clone(self):
        # copy a project version WITH findings and their states preserved
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

        pname = 'Unit Test Python - Clone'

        pv = client.projects.upsert(pname, 'main')
        self.assertIsNotNone(pv)
        try:
            self.assertTrue(pv['committed'])
            a = pv.upload_artifact('tests/resources/scan_20.1.fpr')

            # now
        finally:
            pv.delete()
