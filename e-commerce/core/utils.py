from django.core.cache import cache
from django.core.paginator import InvalidPage, Page, PageNotAnInteger, Paginator
from django.db import models
from django.utils.functional import cached_property
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CachedLimitOffsetPagination(LimitOffsetPagination):
    cache_key = "cached_paginator"  # Base cache key
    cache_timeout = 300  # Cache timeout in seconds

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset using CachedPaginator with limit-offset support.
        """
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)

        if self.limit is None:
            return None

        # Set up the paginator
        paginator = CachedPaginator(
            queryset,
            self.limit,
            cache_key=self._generate_cache_key(request),
            cache_timeout=self.cache_timeout,
        )

        # Calculate the page number based on the offset
        page_number = (self.offset // self.limit) + 1

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            self.page = None
            self._handle_invalid_page(exc)

        # Set the total count required by LimitOffsetPagination
        self.count = paginator.count
        self.request = request

        return list(self.page)

    def get_paginated_response(self, data):
        """
        Return a formatted paginated response.
        """
        return Response(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def _generate_cache_key(self, request):
        """
        Generate a unique cache key based on the request path, limit, and offset.
        """
        return f"{self.cache_key}:{request.path}:{self.limit}:{self.offset}"


class CachedPaginator(Paginator):
    """A paginator that caches the results on a page by page basis."""

    def __init__(
        self,
        object_list,
        per_page,
        orphans=0,
        allow_empty_first_page=True,
        cache_key=None,
        cache_timeout=300,
    ):
        super(CachedPaginator, self).__init__(
            object_list, per_page, orphans, allow_empty_first_page
        )
        self.cache_key = cache_key
        self.cache_timeout = cache_timeout

    @cached_property
    def count(self):
        """
        The original django.core.paginator.count attribute in Django1.8
        is not writable and cant be setted manually, but we would like
        to override it when loading data from cache. (instead of recalculating it).
        So we make it writable via @cached_property.
        """
        return super(CachedPaginator, self).count

    def set_count(self, count):
        """
        Override the paginator.count value (to prevent recalculation)
        and clear num_pages and page_range which values depend on it.
        """
        self.count = count
        # if somehow we have stored .num_pages or .page_range (which are cached properties)
        # this can lead to wrong page calculations (because they depend on paginator.count value)
        # so we clear their values to force recalculations on next calls
        try:
            del self.num_pages
        except AttributeError:
            pass
        try:
            del self.page_range
        except AttributeError:
            pass

    @cached_property
    def num_pages(self):
        """This is not writable in Django1.8. We want to make it writable"""
        return super(CachedPaginator, self).num_pages

    @cached_property
    def page_range(self):
        """This is not writable in Django1.8. We want to make it writable"""
        return super(CachedPaginator, self).page_range

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.

        This will attempt to pull the results out of the cache first, based on
        the requested page number. If not found in the cache,
        it will pull a fresh list and then cache that result + the total result count.
        """
        if self.cache_key is None:
            return super(CachedPaginator, self).page(number)

        # In order to prevent counting the queryset
        # we only validate that the provided number is integer
        # The rest of the validation will happen when we fetch fresh data.
        # so if the number is invalid, no cache will be setted
        # number = self.validate_number(number)
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger("That page number is not an integer")

        page_cache_key = "%s:%s:%s" % (self.cache_key, self.per_page, number)
        page_data = cache.get(page_cache_key)

        if page_data is None:
            page = super(CachedPaginator, self).page(number)
            # cache not only the objects, but the total count too.
            page_data = (page.object_list, self.count)
            cache.set(page_cache_key, page_data, self.cache_timeout)
        else:
            cached_object_list, cached_total_count = page_data
            self.set_count(cached_total_count)
            page = Page(cached_object_list, number, self)

        return page
