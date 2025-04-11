from unittest import TestCase
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any, Iterator

from constants import Constants
from fortifyapi import FortifySSCClient
from fortifyapi.client import LocalUser, SSCObject
from fortifyapi.api import FortifySSCAPI

if __name__ == "__main__" or __name__ == "pytest_mock.plugin":
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


class TestLocalUser(TestCase):
    c = Constants()

    def test_local_user_init(self) -> None:
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        
        # Test local user initialization
        local_user = LocalUser(client.api)
        self.assertIsNotNone(local_user)
        self.assertIsInstance(local_user, SSCObject)
        self.assertIsInstance(local_user, LocalUser)
        
        # Test initialization with data
        user_data = {'username': 'test_user', 'id': 123}
        local_user = LocalUser(client.api, user_data)
        self.assertEqual(local_user['username'], 'test_user')
        self.assertEqual(local_user['id'], 123)
    
    @patch('fortifyapi.api.FortifySSCAPI.page_data')
    def test_local_user_list(self, mock_page_data: MagicMock) -> None:
        """
        Test the list method of the LocalUser class.
        Uses mocking to avoid actual API calls.
        
        Args:
            mock_page_data: Mocked page_data method of the FortifySSCAPI class
        """
        # Define mock data to be returned
        mock_users = [
            {'username': 'user1', 'id': 1, 'email': 'user1@example.com'},
            {'username': 'user2', 'id': 2, 'email': 'user2@example.com'},
            {'username': 'user3', 'id': 3, 'email': 'user3@example.com'}
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
            self.assertEqual(user['username'], mock_users[i]['username'])
            self.assertEqual(user['id'], mock_users[i]['id'])
            self.assertEqual(user['email'], mock_users[i]['email'])
            self.assertEqual(user.parent, client)
    
    def test_local_user_as_dict(self) -> None:
        """
        Test that the LocalUser object behaves like a dictionary
        since it inherits from SSCObject which inherits from dict.
        """
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        
        # Create a user with initial data
        user_data = {'username': 'test_user', 'id': 123, 'email': 'test@example.com'}
        local_user = LocalUser(client.api, user_data)
        
        # Test dictionary-like access
        self.assertEqual(local_user['username'], 'test_user')
        self.assertEqual(local_user['id'], 123)
        self.assertEqual(local_user['email'], 'test@example.com')
        
        # Test modifying the dict
        local_user['username'] = 'modified_user'
        self.assertEqual(local_user['username'], 'modified_user')
        
        # Test adding new key
        local_user['new_key'] = 'new_value'
        self.assertEqual(local_user['new_key'], 'new_value')
        
        # Test iteration
        keys = set(local_user.keys())
        expected_keys = {'username', 'id', 'email', 'new_key'}
        self.assertEqual(keys, expected_keys)

    @patch('fortifyapi.api.FortifySSCAPI._request')
    def test_local_user_list_with_api_request_mock(self, mock_request: MagicMock) -> None:
        """
        Test the list method by mocking the API _request method directly,
        simulating a more realistic API call pattern.
        
        Args:
            mock_request: Mocked _request method of the FortifySSCAPI class
        """
        # Set up mock response data similar to what SSC API would return
        mock_response_data = {
            'data': [
                {'username': 'admin', 'id': 1, 'email': 'admin@example.com', 'firstName': 'Admin', 'lastName': 'User'},
                {'username': 'developer', 'id': 2, 'email': 'dev@example.com', 'firstName': 'Dev', 'lastName': 'User'},
            ],
            'count': 2,
            'responseCode': 200
        }
        
        # Configure the mock to return our data
        mock_request.return_value = mock_response_data
        
        # Create the client and local user object
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        
        # Call the list method and collect results
        result_users = list(client.local_user.list(q='role:admin'))
        
        # Verify the request was made with the right parameters
        mock_request.assert_called_with('GET', '/api/v1/localUsers', q='role:admin', start=0, limit=200)
        
        # Verify we got the expected users
        self.assertEqual(len(result_users), 2)
        
        # Check the first user details
        self.assertEqual(result_users[0]['username'], 'admin')
        self.assertEqual(result_users[0]['email'], 'admin@example.com')
        self.assertEqual(result_users[0]['firstName'], 'Admin')
        
        # Check the second user details
        self.assertEqual(result_users[1]['username'], 'developer')
        self.assertEqual(result_users[1]['email'], 'dev@example.com')
        self.assertEqual(result_users[1]['firstName'], 'Dev')
        
        # Check that each result is properly wrapped in a LocalUser object
        for user in result_users:
            self.assertIsInstance(user, LocalUser)
            self.assertEqual(user.parent, client)

    @patch('fortifyapi.api.FortifySSCAPI._request')
    def test_local_user_list_pagination(self, mock_request: MagicMock) -> None:
        """
        Test that the pagination functionality works correctly in the list method.
        
        Args:
            mock_request: Mocked _request method of the FortifySSCAPI class
        """
        # Create mock responses for the first and second pages
        first_page_response = {
            'data': [
                {'username': 'user1', 'id': 1, 'email': 'user1@example.com'},
                {'username': 'user2', 'id': 2, 'email': 'user2@example.com'},
            ],
            'count': 4,  # Total 4 users, but only 2 per page
            'responseCode': 200
        }
        
        second_page_response = {
            'data': [
                {'username': 'user3', 'id': 3, 'email': 'user3@example.com'},
                {'username': 'user4', 'id': 4, 'email': 'user4@example.com'},
            ],
            'count': 4,
            'responseCode': 200
        }
        
        # Configure the mock to return different responses for different calls
        mock_request.side_effect = [first_page_response, second_page_response]
        
        # Create the client and local user object
        client = FortifySSCClient(self.c.url, self.c.token)
        self.c.setup_proxy(client)
        
        # Call the list method with a smaller limit to force pagination
        result_users = list(client.local_user.list(limit=2))
        
        # Verify we got all 4 users despite pagination
        self.assertEqual(len(result_users), 4)
        
        # Verify the first API call used start=0
        mock_request.assert_any_call('GET', '/api/v1/localUsers', start=0, limit=2)
        
        # Verify the second API call used start=2
        mock_request.assert_any_call('GET', '/api/v1/localUsers', start=2, limit=2)
        
        # Verify all users were properly constructed
        self.assertEqual(result_users[0]['username'], 'user1')
        self.assertEqual(result_users[1]['username'], 'user2')
        self.assertEqual(result_users[2]['username'], 'user3')
        self.assertEqual(result_users[3]['username'], 'user4') 
