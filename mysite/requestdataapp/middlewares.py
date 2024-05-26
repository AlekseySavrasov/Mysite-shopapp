from django.http import HttpRequest, HttpResponse
from datetime import datetime, timedelta


def set_useragent_on_request_middleware(get_response):

    def middleware(request: HttpRequest) -> HttpResponse:
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)

        return response

    return middleware


class CountRequestMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.requests_count += 1
        response = self.get_response(request)
        self.responses_count += 1

        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1


class ThrottlingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.dict_time_requests = {}

    def __call__(self, request: HttpRequest) -> HttpResponse:
        client_ip = request.META.get('REMOTE_ADDR')
        time_request = datetime.now()
        diff_time = (
                time_request - self.dict_time_requests.get(client_ip, time_request - timedelta(seconds=1))
        ).total_seconds()

        # if int(diff_time) >= 1:
        self.dict_time_requests[client_ip] = time_request
        response = self.get_response(request)
        # else:
        #     raise Exception("Превышен лимит запросов")

        return response
