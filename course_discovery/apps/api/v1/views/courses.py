from django.db.models.functions import Lower
from rest_framework import viewsets
from rest_framework.filters import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from course_discovery.apps.api import filters, serializers
from course_discovery.apps.api.v1.views import prefetch_related_objects_for_courses, get_query_param
from course_discovery.apps.course_metadata.constants import COURSE_ID_REGEX
from course_discovery.apps.course_metadata.models import Course


# pylint: disable=no-member
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ Course resource. """
    filter_backends = (DjangoFilterBackend,)
    filter_class = filters.CourseFilter
    lookup_field = 'key'
    lookup_value_regex = COURSE_ID_REGEX
    queryset = Course.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CourseWithProgramsSerializer

    def get_queryset(self):
        """ List one course
        ---
        parameters:
            - name: include_deleted_programs
              description: Will include deleted programs in the associated programs array
              required: false
              type: integer
              paramType: query
              multiple: false
        """
        q = self.request.query_params.get('q', None)

        if q:
            queryset = Course.search(q)
        else:
            queryset = super(CourseViewSet, self).get_queryset()
            queryset = prefetch_related_objects_for_courses(queryset)

        return queryset.order_by(Lower('key'))

    def get_serializer_context(self, *args, **kwargs):
        context = super().get_serializer_context(*args, **kwargs)
        context.update({
            'exclude_utm': get_query_param(self.request, 'exclude_utm'),
            'include_deleted_programs': get_query_param(self.request, 'include_deleted_programs'),
        })

        return context

    def list(self, request, *args, **kwargs):
        """ List all courses.
         ---
        parameters:
            - name: q
              description: Elasticsearch querystring query. This filter takes precedence over other filters.
              required: false
              type: string
              paramType: query
              multiple: false
            - name: keys
              description: Filter by keys (comma-separated list)
              required: false
              type: string
              paramType: query
              multiple: false
            - name: exclude_utm
              description: Exclude UTM parameters from marketing URLs.
              required: false
              type: integer
              paramType: query
              multiple: false
            - name: include_deleted_programs
              description: Will include deleted programs in the associated programs array
              required: false
              type: integer
              paramType: query
              multiple: false
        """
        return super(CourseViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve details for a course. """
        return super(CourseViewSet, self).retrieve(request, *args, **kwargs)