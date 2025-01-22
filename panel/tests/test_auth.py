"""
This module contains tests for handling OAuth login and response decoding
using the Tornado HTTP client and Panel's OAuthLoginHandler.
"""

from unittest.mock import Mock, patch

import pytest

from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.web import HTTPError

from panel.auth import OAuthLoginHandler, decode_response_body


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
