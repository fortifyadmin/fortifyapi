from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient


class TestReports(TestCase):
    c = Constants()

    def test_report_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

        for report in client.reports.list():
            self.assertIsNotNone(report)
            print(report)
            self.assertIsNotNone(report['id'])

