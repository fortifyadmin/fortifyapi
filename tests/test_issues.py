from unittest import TestCasi don't kne
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient, Query, Issue, CloneVersionTemplate


class TestIssues(TestCase):
    c = Constants()

    def test_issue(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        pname = 'Unit Test Python - issue'

        pv = client.projects.upsert(pname, 'default')
        self.assertIsNotNone(pv)
        try:
            a = pv.upload_artifact('tests/resources/scan_20.1.fpr', process_block=True)
            print(a)
            issues = list(pv.issues.list())
            self.assertEqual(7, len(issues), 'It either failed to process or someone modified the FPR')
            for issue in issues:
                issue.audit(Issue.EXPLOITABLE, "Testing Audit")

            issues = list(pv.issues.list())
            self.assertEqual(7, len(issues), 'It either failed to process or someone modified the FPR')
            for issue in issues:
                self.assertEqual('Exploitable', issue['primaryTag'])
                #print(issue)
                #print('')

            pv2 = pv.create("clone-default", template=CloneVersionTemplate(pv['id']))
            self.assertIsNotNone(pv2)
            print(pv2)

            issues = list(pv2.issues.list())
            self.assertEqual(7, len(issues), 'It either failed to process or someone modified the FPR')
            for issue in issues:
                print(issue)
                print('')
                self.assertEqual('Exploitable', issue['primaryTag'])

        finally:
            pv.parent.delete()
            pass
