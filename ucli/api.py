import logging

import click
import requests

from .utils import exit

log = logging.getLogger(__name__)


class Api(object):
    '''UData API client'''

    HTTPError = requests.HTTPError  # For easy access

    DEFAULT_HEADERS = {
        'User-Agent': 'ucli',
        'Content-Type': 'application/json',
    }

    def __init__(self, root, token, **kwargs):
        self.root = root
        if not self.root.endswith('/'):
            self.root += '/'
        if not self.root.endswith('api/1/'):
            self.root += 'api/1/'
        self.token = token
        self.ssl_check = kwargs.get('ssl_check', True)
        # Disable the urllib3 warning
        if not self.ssl_check:
            try:
                import requests.packages.urllib3
                requests.packages.urllib3.disable_warnings()
            except:
                pass

    def headers(self, **kwargs):
        headers = self.DEFAULT_HEADERS.copy()
        if self.token:
            headers['X-API-KEY'] = self.token
        headers.update(kwargs)
        return headers

    def url(self, path):
        return ''.join((self.root, path))

    def check(self, response, raw=False, allow_failure=False):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                details = response.json()['message']
            except:
                details = None
            if allow_failure:
                response.error_details = details
                return response
            else:
                exit(e, details)
        return response if raw else response.json()

    def get(self, path, headers=None, fields=None, allow_failure=False, **params):
        headers = headers or {}
        if fields:
            headers['X-Fields'] = fields
        headers = self.headers(**headers)
        url = self.url(path)
        try:
            response = requests.get(url, params=params, headers=headers, verify=self.ssl_check)
        except requests.exceptions.RequestException as e:
            exit(e)
        return self.check(response, allow_failure=allow_failure)

    def post(self, path, data, headers=None, fields=None, allow_failure=False):
        headers = headers or {}
        if fields:
            headers['X-Fields'] = fields
        headers = self.headers(**headers)
        url = self.url(path)
        try:
            response = requests.post(url, json=data, headers=headers, verify=self.ssl_check)
        except requests.exceptions.RequestException as e:
            exit(e)
        return self.check(response, allow_failure=allow_failure)

    def put(self, path, data, headers=None, fields=None, allow_failure=False):
        headers = headers or {}
        if fields:
            headers['X-Fields'] = fields
        headers = self.headers(**headers)
        url = self.url(path)
        try:
            response = requests.put(url, headers=headers, json=data, verify=self.ssl_check)
        except requests.exceptions.RequestException as e:
            exit(e)
        return self.check(response, allow_failure=allow_failure)

    def delete(self, path, allow_failure=False):
        headers = self.headers()
        url = self.url(path)
        try:
            response = requests.delete(url, headers=headers, verify=self.ssl_check)
        except requests.exceptions.RequestException as e:
            exit(e)
        return self.check(response, raw=True, allow_failure=allow_failure)


pass_api = click.make_pass_decorator(Api)
