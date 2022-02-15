from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi.exceptions import *
from fortifyapi import FortifySSCClient, Query


class TestRulepack(TestCase):
    c = Constants()

    def test_rulepack_update(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        response = client.rulepack.update()
        rules = response.data['data']

        for rule in rules:
            for message in rule['statuses']:
                print("{}".format(message['message']))
                self.assertIsNotNone(message)


