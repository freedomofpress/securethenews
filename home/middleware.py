import time
import uuid

import structlog


logger = structlog.get_logger('request_log')


class RequestLogMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.request_keys = ('method', 'path_info', 'scheme', 'user')
        self.request_meta_keys = (
            'REMOTE_ADDR',
            'HTTP_USER_AGENT',
            'HTTP_REFERER',
            'HTTP_HOST',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_X_SCEHEME',
        )
        self.response_keys = ('charset', 'reason_phrase', 'status_code')

    def process_exception(self, request, exception):
        logger.exception("request_failed")

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        structlog.contextvars.clear_contextvars()

        request_id = str(uuid.uuid4())

        request_dict = {
            key: getattr(request, key, '') for key in self.request_keys
        }
        request_dict["user"] = str(request_dict["user"])
        request_dict["meta"] = {
            key: request.META.get(key, "") for key in self.request_meta_keys
        }
        structlog.contextvars.bind_contextvars(
            request_id=request_id, request=request_dict
        )

        start_time = time.perf_counter_ns()

        response = self.get_response(request)

        duration = (time.perf_counter_ns() - start_time) // 1_000_000

        structlog.contextvars.bind_contextvars(duration_ms=duration)

        response_dict = {
            key: getattr(response, key, '') for key in self.response_keys
        }
        logger.info('request_finished', response=response_dict)

        # Code to be executed for each request/response after
        # the view is called.
        return response
