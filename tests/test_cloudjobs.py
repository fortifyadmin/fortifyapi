from unittest import TestCase
from pprint import pprint
from constants import Constants
from fortifyapi import FortifySSCClient


class TestCloudJobs(TestCase):
    c = Constants()

    def test_job_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        jobs = list(client.cloudjobs.list())
        # no guarantee a job is running, this is all we'll test for now
        self.assertIsNotNone(jobs)
