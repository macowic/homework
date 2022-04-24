from django.http import HttpResponse
from django.template import loader
from django.template.backends.django import Template
from django.core.handlers.wsgi import WSGIRequest


class HttpResponseMixin:

    CONTENT_TYPE = 'text/html'

    def get_http_response(self,
                          request: WSGIRequest,
                          template_name: str,
                          context: dict = {}) -> HttpResponse:
        template: Template = loader.get_template(template_name)

        return HttpResponse(
            template.render(
                context,
                request
            ),
            content_type=self.CONTENT_TYPE
        )