import contextlib
from unittest import mock

import structlog
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from wagtail.core.models import Page

from home.middleware import RequestLogMiddleware


@contextlib.contextmanager
def capture_logs_with_contextvars():
    """Modified version of structlog.testing.capture_logs that captures
    data bound to structlog's loggers with ``bind_contextvars``.

    """
    cap = structlog.testing.LogCapture()
    old_processors = structlog.get_config()['processors']
    try:
        structlog.configure(
            processors=[structlog.contextvars.merge_contextvars, cap]
        )
        yield cap.entries
    finally:
        structlog.configure(processors=old_processors)


class RequestLogTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='username1',
            password='test',
            email='test@test.com',
        )

    def setUp(self):
        self.factory = RequestFactory()
        self.response_charset = 'utf-8'
        self.response_status_code = 200
        self.response_reason_phrase = 'OK'

    @mock.patch.object(Page, 'serve')
    def test_request_log_failed(self, serve):
        serve.side_effect = Exception('Application Error')

        with self.assertRaises(Exception):
            with capture_logs_with_contextvars() as cap_logs:
                with self.modify_settings(
                    MIDDLEWARE={
                        'append': 'home.middleware.RequestLogMiddleware',
                    }
                ):
                    self.client.get('/')

        log_entry = cap_logs[0]
        self.assertEqual(log_entry['event'], 'request_failed')
        self.assertEqual(log_entry['log_level'], 'error')

    def test_request_log_finished(self):
        response = mock.Mock(
            status_code=self.response_status_code,
            charset=self.response_charset,
            reason_phrase=self.response_reason_phrase,
        )
        get_response = mock.Mock(return_value=response)

        user_agent = 'Mozilla'
        forwarded_for = '1.2.3.4'
        host = '1.1.1.1'
        referer = 'http://localhost:8000/'
        real_ip = '2.2.2.2'

        request = self.factory.get(
            '/',
            HTTP_USER_AGENT=user_agent,
            HTTP_X_FORWARDED_FOR=forwarded_for,
            HTTP_HOST=host,
            HTTP_REFERER=referer,
            HTTP_X_REAL_IP=real_ip,
        )
        request.user = self.user

        middleware = RequestLogMiddleware(get_response)

        with capture_logs_with_contextvars() as cap_logs:
            response = middleware(request)

        self.assertEqual(len(cap_logs), 1)
        log_entry = cap_logs[0]

        self.assertEqual(
            log_entry['response'],
            {
                'charset': self.response_charset,
                'status_code': self.response_status_code,
                'reason_phrase': self.response_reason_phrase,
            },
        )
        self.assertEqual(
            log_entry['request'],
            {
                'meta': {
                    'REMOTE_ADDR': '127.0.0.1',
                    'HTTP_HOST': host,
                    'HTTP_REFERER': referer,
                    'HTTP_USER_AGENT': user_agent,
                    'HTTP_X_FORWARDED_FOR': forwarded_for,
                    'HTTP_X_REAL_IP': real_ip,
                    'HTTP_X_SCEHEME': '',
                },
                'method': 'GET',
                'path_info': '/',
                'scheme': 'http',
                'user': 'username1',
            },
        )

        self.assertIsNotNone(log_entry['duration_ms'])
        self.assertEqual(log_entry['event'], 'request_finished')
        self.assertEqual(log_entry['log_level'], 'info')
        self.assertRegex(
            log_entry['request_id'],
            r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}',  # noqa: E501
        )
