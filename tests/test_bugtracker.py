from unittest import TestCase
from constants import Constants
from fortifyapi import FortifySSCAPI
from fortifyapi.client import FortifySSCClient


class TestBugtracker(TestCase):
    c = Constants()

    def test_bugtracker_list(self):
        """
        Checks listing of all bug trackers. Will fail if none are installed.
        """
        client = FortifySSCClient(self.c.url, self.c.token)
        bugtrackers = client.list_all_bugtrackers()
        i = 0
        for bugtracker in bugtrackers:            
            self.assertIsNotNone(bugtracker['id'])
            i+=1
        self.assertGreater(i,0)
    
    def test_bugtracker_get_set(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        v = client.projects.upsert("Unit Test Python", 'default')
        v.set_bugtracker({"assignedPluginId": None})
        self.assertIsNone(v.get_bugtracker())
