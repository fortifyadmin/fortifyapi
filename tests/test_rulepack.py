from unittest import TestCase
from constants import Constants
from fortifyapi import FortifySSCClient


class TestRulepack(TestCase):
    c = Constants()

    def test_rulepack_update(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        rules = client.rulepack.update()

        for rule in rules:
            for message in rule['statuses']:
                rulepack_content = message['message']
                self.assertNotEqual(len(rulepack_content), 0)
                self.assertIsNotNone(message['message'])
                #print("{}".format(message['message']))

