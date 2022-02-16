from unittest import TestCase
from pprint import pprint
from constants import Constants
from fortifyapi import FortifySSCClient, Query


class TestArtifacts(TestCase):
    c = Constants()

    def test_version_artifact(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        pname = 'Unit Test Python - Artifact'

        pv = client.projects.upsert(pname, 'default')
        self.assertIsNotNone(pv)
        self.assertTrue(pv['committed'])

        artifacts = list(pv.artifacts.list())
        self.assertEqual(0, len(artifacts), 'We actually had artifacts?')

        a = pv.upload_artifact('tests/resources/scan_20.1.fpr')
        self.assertIsNotNone(a)

        artifacts = list(pv.artifacts.list())
        self.assertEqual(1, len(artifacts))

        a = artifacts[0]
        pprint(a)

        # clean up
        pv = list(client.projects.list(q=Query().query('name', pname)))
        for e in pv:
            e.delete()

