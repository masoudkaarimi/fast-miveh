from rest_framework.pagination import PageNumberPagination as BasePageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(BasePageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'meta': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'page': self.page.number,
                'per_page': self.page.paginator.per_page,
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                }
            },
            'results': data
        })
