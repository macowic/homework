from typing import (
    Optional,
)
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

from abstracts.mixins import HttpResponseMixin


class ViewHandler(HttpResponseMixin):

    template_login_page: str = 'university/login.html'

    def get_validated_response(
        self,
        request: WSGIRequest
    ) -> Optional[HttpResponse]:
        if request.user.is_authenticated:
            return None

        return self.get_http_response(
            request,
            self.template_login_page
        )