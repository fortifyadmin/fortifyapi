from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient


class TestJobs(TestCase):
    c = Constants()

    def test_job_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        jobs = list(client.jobs.list())
        self.assertIsNotNone(jobs)
        self.assertNotEqual(len(jobs), 0)

        job = jobs[0]

        pprint(job)

        token = job['jobToken']
        self.assertIsNotNone(token)

        job2 = client.jobs.get(token)
        self.assertEqual(job['jobToken'], job2['jobToken'])

    def test_job_cancel(self):
        return # one off test - TODO: actually write this
        client = FortifySSCClient(self.c.url, self.c.token)
        jobs = list(client.jobs.list())
        self.assertIsNotNone(jobs)
        self.assertNotEqual(len(jobs), 0)

        for job in jobs:
            print(job)
            job.cancel()



