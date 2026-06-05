"""
This module contains tests for handling OAuth login and response decoding
using the Tornado HTTP client and Panel's OAuthLoginHandler.
"""

import asyncio

from unittest.mock import Mock, patch

import pytest

from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.web import HTTPError

from panel.auth import OAuthLoginHandler, decode_response_body
from panel.config import config


def _create_mock_response(body, code=401):
    """
    Create a mock HTTPResponse object with the specified body and status code.

    Parameters
    ----------
    body : bytes
        The body content of the mock response.
    code : int, optional
        The HTTP status code of the mock response (default is 401).

    Returns
    -------
    Mock
        A mock HTTPResponse object with the specified attributes.
    """
    mock_request = Mock(spec=HTTPRequest)
    mock_response = Mock(spec=HTTPResponse)
    mock_response.body = body
    mock_response.request = mock_request
    mock_response.code = code
    return mock_response

def test_decode_invalid_response_body():
    """
    Test the decode_response_body function with an invalid JSON response body.

    Ensures that the function can handle and correct invalid JSON containing
    single quotes, which are not valid in JSON strings.
    """
    # The body below from azure contains \' which is not valid json.
    body = b'{"error_description":"... for a secret added to app \'some-value\'."}'
    invalid_response = _create_mock_response(body)
    result = decode_response_body(invalid_response)
    assert result == {'error_description': '... for a secret added to app "some-value".'}

def test_raise_error():
    """
    Test the _raise_error method of OAuthLoginHandler with an invalid JSON response.

    Mocks the OAuthLoginHandler to bypass initialization and verifies that
    an HTTPError is raised when the response contains invalid JSON.
    """
    response = _create_mock_response(b'{"invalid_json": "missing_end_quote}')
    with patch.object(OAuthLoginHandler, '__init__', lambda self, *args, **kwargs: None):
        handler = OAuthLoginHandler()
        with pytest.raises(HTTPError):
            handler._raise_error(response=response, body=None, status=401)


def test_get_authenticated_user_forwards_extra_oauth_params():
    """
    Extra OAuth parameters configured via ``config.oauth_extra_params``
    (e.g. ``prompt`` or ``login_hint``) should be forwarded to the
    authorization endpoint, while keys consumed internally by the provider
    (e.g. ``tenant``) must not be.
    """
    with patch.object(OAuthLoginHandler, '__init__', lambda self, *args, **kwargs: None):
        handler = OAuthLoginHandler()
        handler.authorize_redirect = Mock()
        original = config._oauth_extra_params
        config._oauth_extra_params = {
            'prompt': 'login',
            'login_hint': 'user@example.org',
            'tenant': 'my-tenant',  # reserved (Azure) -> must NOT be forwarded
            'audience': 'my-audience',
        }
        try:
            asyncio.run(handler.get_authenticated_user(
                redirect_uri='https://example.org',
                client_id='client-id',
                state='state-123',
            ))
        finally:
            config._oauth_extra_params = original

    assert handler.authorize_redirect.called
    extra_params = handler.authorize_redirect.call_args.kwargs['extra_params']
    assert extra_params['state'] == 'state-123'
    # New behaviour: arbitrary authorization params are forwarded
    assert extra_params['prompt'] == 'login'
    assert extra_params['login_hint'] == 'user@example.org'
    # Existing behaviour is preserved
    assert extra_params['audience'] == 'my-audience'
    # Provider-internal keys are not leaked to the authorize URL
    assert 'tenant' not in extra_params
