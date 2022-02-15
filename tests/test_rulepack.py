from unittest import TestCase
from pprint import pprint

from constants import Constants

from fortifyapi import FortifySSCClient


class TestRulepack(TestCase):
    c = Constants()

    def test_rulepack_update(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        response = client.rulepack.update()
        rules = response.data['data']

        for rule in rules:
            for message in rule['statuses']:
                rulepack_content = message['message']
                self.assertNotEqual(len(rulepack_content), 0)
                self.assertIsNotNone(message['message'])
                #print("{}".format(message['message']))


