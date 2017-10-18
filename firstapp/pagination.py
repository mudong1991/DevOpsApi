# -*- coding: UTF-8 -*-
__author__ = 'MD'
from django.conf import settings
from rest_framework import pagination
from rest_framework.views import Response
from rest_framework.exceptions import NotFound
from django.utils import six


# 自定义分页类
class CustomPagination(pagination.PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = "rows"  # 分页的项集合

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except pagination.InvalidPage as exc:
            try:
                self.page = paginator.page(1)
            except pagination.InvalidPage as exc:
                msg = self.invalid_page_message.format(
                    page_number=page_number, message=six.text_type(exc)
                )
                raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response({
            'pageNo': self.page.number,
            'totalPage': self.page.paginator.num_pages,
            'totalCount': self.page.paginator.count,
            'pageSize': self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'tableList': data,
        })
