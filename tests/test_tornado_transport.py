import pytest
from pretend import stub
from lxml import etree
from tornado.httpclient import HTTPResponse, HTTPRequest
from tornado.testing import gen_test, AsyncTestCase
from tornado.concurrent import Future
from requests import Session
from requests.structures import CaseInsensitiveDict

from tornado.httputil import HTTPHeaders

from mock import patch, ANY
from zeep import tornado


class TornadoAsyncTransportTest(AsyncTestCase):
    @pytest.mark.requests
    def test_no_cache(self):
        transport = tornado.TornadoAsyncTransport()
        assert transport.cache is None

    @pytest.mark.requests
    @patch('tornado.httpclient.HTTPClient.fetch')
    @gen_test
    def test_load(self, mock_httpclient_fetch):
        cache = stub(get=lambda url: None, add=lambda url, content: None)
        response = HTTPResponse(HTTPRequest('http://tests.python-zeep.org/test.xml'), 200)
        response.buffer = True
        response._body = 'x'
        mock_httpclient_fetch.return_value = response

        transport = tornado.TornadoAsyncTransport(cache=cache)

        result = transport.load('http://tests.python-zeep.org/test.xml')

        assert result == 'x'

    @pytest.mark.requests
    @patch('tornado.httpclient.AsyncHTTPClient.fetch')
    @gen_test
    def test_post(self, mock_httpclient_fetch):
        cache = stub(get=lambda url: None, add=lambda url, content: None)

        response = HTTPResponse(HTTPRequest('http://tests.python-zeep.org/test.xml'), 200)
        response.buffer = True
        response._body = 'x'
        http_fetch_future = Future()
        http_fetch_future.set_result(response)
        mock_httpclient_fetch.return_value = http_fetch_future

        transport = tornado.TornadoAsyncTransport(cache=cache)

        envelope = etree.Element('Envelope')

        result = yield transport.post_xml(
            'http://tests.python-zeep.org/test.xml',
            envelope=envelope,
            headers={})

        assert result.content == 'x'
        assert result.status_code == 200