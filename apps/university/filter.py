from django.core.handlers.wsgi import WSGIRequest
from django.contrib.admin import SimpleListFilter
from django.db.models import QuerySet

from university.admin import StudentAdmin
from university.models import Student


class StudentStateFilter(SimpleListFilter):

    def lookup(
        self,
        request: WSGIRequest,
        *args,
        **kwargs
    ) -> list:
        """LOOKUPS"""

        return [
            ('deleted', 'Удалённые'),
            ('not_deleted', 'Не удалённые')
        ]


    def queryset(
        self, 
        request: WSGIRequest, 
        queryset: QuerySet
    ) -> QuerySet:
        

        if self.value() == 'deleted':
            return queryset.filter(datetime_deleted__isnull = False)
        if self.value() == 'not_deleted':
            return queryset.filter(datetime_deleted__isnull = True)