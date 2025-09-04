"""
This module contains API tests for the Catty app.
"""

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

from playwright.sync_api import APIRequestContext
from testlib.inputs import User


# --------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------

def test_successful_api_login(catty_api: APIRequestContext, user: User, base_url: str):
  response = catty_api.post('/login', form={'username': user.username, 'password': user.password})
  assert response.ok
  assert response.url == f'{base_url}/reminders'

  cookie = catty_api.storage_state()['cookies'][0]
  assert cookie['name'] == 'reminders_session'
  assert cookie['value']
