# -*- coding: utf-8 -*-
"""File for connecting to Active Collab."""
import json
import os
import urllib
from typing import Dict

import requests


class AuthenticationException(Exception):
    """Exception for authentication errors."""

    pass


class Config():
    """Configuration for ActiveCollab Session."""

    def __init__(self, filename: str='config.json') -> None:
        """Initialize config."""
        self.filename = filename
        self.url = None
        self.user = None
        self.password = None
        self.client_name = None
        self.client_vendor = None

    def load(self) -> None:
        """Load the config file."""
        with open(os.path.expanduser(self.filename), 'r') as f:
            json_data = json.load(f)
            self.__dict__.update(json_data)


class ActiveCollab(object):
    """Active Collab API."""

    def __init__(self, config: Config) -> None:
        """Initialize the class."""
        self.config = config
        self.session = requests.session()

    def authenticate(self) -> None:
        """Authenticate against the api."""
        data = {
            'username': self.config.user,
            'password': self.config.password,
            'client_name': self.config.client_name,
            'client_vendor': self.config.client_vendor
        }
        auth_url = '{}/issue-token'.format(self.config.url)
        r = self.session.post(auth_url, data=data)
        try:
            token = r.json()['token']
        except json.decoder.JSONDecodeError:
            raise AuthenticationException
        else:
            self.token = token

    def get(self, url: str) -> Dict:
        """Make a get call to the API."""
        if not getattr(self, 'token'):
            raise AuthenticationException
        headers = {'X-Angie-AuthApiToken': self.token}
        url = '{}{}'.format(self.config.url, url)
        r = self.session.get(url, headers=headers)
        return r.json()

    def post(self, url: str, data: Dict) -> Dict:
        """Make post call to the API."""
        if not getattr(self, 'token'):
            raise AuthenticationException
        headers = {'X-Angie-AuthApiToken': self.token}
        url = '{}{}'.format(self.config.url, url)
        r = self.session.post(url, data=data, headers=headers)
        return r.json()

    def get_info(self) -> Dict:
        """Get info about the system information."""
        return self.get('/info')

    def get_job_types(self) -> Dict:
        """Get the available job types."""
        return self.get('/job-types')

    def get_projects(self) -> Dict:
        """Get the projects."""
        return self.get('/projects')

    def get_users(self) -> Dict:
        """Get the projects."""
        return self.get('/users')

    def get_time_records(self, user_id: str) -> Dict:
        """Get the time records for a user."""
        return self.get('/users/{}/time-records'.format(user_id))
