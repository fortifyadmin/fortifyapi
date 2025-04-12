from unittest import TestCase
from unittest.mock import MagicMock

from constants import Constants
from fortifyapi import FortifySSCClient, Query
from fortifyapi.client import LocalUser, SSCObject

class TestLocalUser(TestCase):
    c = Constants()

    def test_user_list(self):
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)

        q = Query().query("suspended", False)
        active_users = list(client.local_user.list(q=q))
        print(active_users)

        self.assertIsNotNone(active_users)
        self.assertEqual(len(active_users), 1)

    def test_local_user_init(self) -> None:
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        
        # Test local user initialization
        local_user = LocalUser(client.api)
        self.assertIsNotNone(local_user)
        self.assertIsInstance(local_user, SSCObject)
        self.assertIsInstance(local_user, LocalUser)
        
        # Test initialization with data
        user_data = {'id': 1, 'userName': 'admin', 'firstName': 'DevSecOps', 'lastName': 'Administrator', 'email': 'devsecops@example.com', 'suspended': False}
        local_user = LocalUser(client.api, user_data)
        self.assertEqual(local_user['userName'], 'admin')
        self.assertEqual(local_user['id'], 1)
    
    def test_local_user_list(self, mock_page_data: MagicMock) -> None:
        """
        Test the list method of the LocalUser class.
        Uses mocking to avoid actual API calls.

        Args:
            mock_page_data: Mocked page_data method of the FortifySSCAPI class
        """
        # Define mock data to be returned
        mock_users = [
            {'id': 1, 'userName': 'admin', 'firstName': 'Fortify', 'lastName': 'Administrator', 'email': 'devsecops@example.com', 'requirePasswordChange': False, 'passwordNeverExpire': True, 'suspended': False, 'failedLoginAttempts': 0, 'dateFrozen': None, 'roles': [{'id': 'admin', 'name': 'Administrator'}]},
            {'id': 10989, 'userName': 'automation.admin', 'firstName': 'Automation', 'lastName': 'Automation Service', 'email': 'devsecops@example.com', 'requirePasswordChange': False, 'passwordNeverExpire': True, 'suspended': False, 'failedLoginAttempts': 0, 'dateFrozen': None, 'roles': [{'id': 'admin', 'name': 'Administrator'}]},
            {'id': 6625, 'userName': 'brandon.spruth', 'firstName': 'Brandon', 'lastName': 'Spruth', 'email': 'brandon.spruth@example.com', 'requirePasswordChange': False, 'passwordNeverExpire': True, 'suspended': False, 'failedLoginAttempts': 2, 'dateFrozen': None, 'roles': [{'id': 'admin', 'name': 'Developer'}]}
        ]
        
        # Setup the mock to return our test data
        mock_page_data.return_value = mock_users
        
        # Create client and local user object
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        
        # Call the list method and collect results
        result_users = list(client.local_user.list(filter='test'))
        
        # Verify the mock was called with correct parameters
        mock_page_data.assert_called_once_with('/api/v1/localUsers', filter='test')
        
        # Verify we got the expected number of users
        self.assertEqual(len(result_users), 3)
        
        # Verify each user has the correct type and data
        for i, user in enumerate(result_users):
            self.assertIsInstance(user, LocalUser)
            self.assertEqual(user['userName'], mock_users[i]['userName'])
            self.assertEqual(user['id'], mock_users[i]['id'])
            self.assertEqual(user['email'], mock_users[i]['email'])
            self.assertEqual(user.parent, client)
