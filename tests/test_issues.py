from unittest import TestCase
from pprint import pprint
from os import path
import time
from constants import Constants
from fortifyapi import FortifySSCClient, Issue, CloneVersionTemplate


class TestIssues(TestCase):
    c = Constants()

    def test_issue(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        pname = 'Unit Test Python - issue'

        pv = client.projects.upsert(pname, 'default')
        self.assertIsNotNone(pv)
        try:
            true_path = path.abspath(path.join(__file__, '../..', 'tests/resources/scan_20.1.fpr'))
            print(f"Uploading {true_path}")

            a = pv.upload_artifact(true_path, process_block=True)
            print(a)
            self.assertEqual(a['status'], 'PROCESS_COMPLETE')
            # even though it's process complete, randomly it won't have issues (yet?)
            # that means this test is flaky, and needs to be fixed - sleep to help the issue.
            time.sleep(5)
            issues = list(pv.issues.list())
            print(issues)
            self.assertEqual(7, len(issues), 'It either failed to process or someone modified the FPR')
            for issue in issues:
                issue.audit(Issue.EXPLOITABLE, "Testing Audit")

            issues = list(pv.issues.list())
            self.assertEqual(7, len(issues), 'It either failed to process or someone modified the FPR')
            for issue in issues:
                self.assertEqual('Exploitable', issue['primaryTag'])
                #print(issue)
                #print('')

            #TODO: fix clone issue
            '''
            pv2 = pv.create("clone-default", template=CloneVersionTemplate(pv['id']))
            self.assertIsNotNone(pv2)
            print(pv2)
            time.sleep(5)

            issues = list(pv2.issues.list())
            self.assertEqual(7, len(issues), 'It either failed to process or someone modified the FPR')
            for issue in issues:
                self.assertEqual('Exploitable', issue['primaryTag'])
            '''

        finally:
            pv.parent.delete()
            pass
