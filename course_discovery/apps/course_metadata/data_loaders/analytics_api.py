import logging
from django.utils.functional import cached_property

from analyticsclient.client import Client
from course_discovery.apps.course_metadata.data_loaders import AbstractDataLoader
from course_discovery.apps.course_metadata.models import (
    Course, CourseRun, Program
)

logger = logging.getLogger(__name__)


class AnalyticsAPIDataLoader(AbstractDataLoader):

    API_TIMEOUT = 5 # time in seconds

    def __init__(self, partner, api_url, access_token=None, token_type=None, max_workers=None,
                 is_threadsafe=False, **kwargs):
        super(AnalyticsAPIDataLoader, self).__init__(
            partner, api_url, access_token, token_type, max_workers, is_threadsafe, **kwargs
        )
        logger.info("IN INIT FOR ANALYTICS")

        # uuid: {course, count}
        self.course_dictionary = {}
        # uuid: {program, count}
        self.program_dictionary = {}

        if not (self.partner.analytics_url and self.partner.analytics_token):
            msg = 'Analytics API credentials are not properly configured for Partner [{partner}]!'.format(
                partner=partner.short_code)
            raise Exception(msg)

    @cached_property
    def api_client(self):

        analytics_api_client = Client(base_url=self.partner.analytics_url,
                             auth_token=self.partner.analytics_token,
                             timeout=self.API_TIMEOUT)

        return analytics_api_client

    def get_query_kwargs(self):
        return {}

    def ingest(self):
        logger.info("IN INGEST FOR ANALYTICS")
        """ Load data for all course runs. """
        course_summaries_response = self.api_client.course_summaries()
        # self._process_response(course_summaries_response)
        course_run_summaries = course_summaries_response.course_summaries(fields=['course_id', 'count'])
        import pprint
        # logger.info(pprint.pformat(course_run_summaries))

        # logger.info(course_run_summaries)
        logger.info("Test complete!")

        for course_run_summary in course_run_summaries:
            # Add one to avoid requesting the first page again and to make sure
            # we get the last page when range() is used below.
            # logger.info(course_run_summary)
            self._process_course_run_summary(course_run_summary=course_run_summary)

        for course, count in self.course_dictionary.items():
            # update course count
            # get programs for course
            # add course total to program total
            logger.info(course)
            logger.info(count)

        for program,count in self.program_dictionary:
            # update program count
            logger.info(program)
            logger.info(count)

    def _process_course_run_summary(self, course_run_summary):
        # logger.info("Course run summary:")
        # logger.info(course_run_summary)
        # get course run from course key
        course_run = None
        course_run_key = course_run_summary['course_id']
        course_run_count = course_run_summary['count']
        try:
            course_run = CourseRun.objects.get(key__iexact=course_run_key)
            import pprint
            # logger.info(pprint.pformat(course_run_summaries))
            # logger.info(pprint.pformat(course_run.course.__dict__))
            # logger.info('Course run: [{course_run_key}] found in DB.'.format(course_run_key=course_run_key))
        except CourseRun.DoesNotExist:
            logger.info('Course run: [{course_run_key}] not found in DB.'.format(course_run_key=course_run_key))
            return

        course = course_run.course
        course_uuid = course.uuid
        # update course run count
        # course_run.count = course_run_count
        # course_run.save()
        # logger.info('Updating course run')
        # get course for course run

        # add course run total to course total in dictionary
        if course_uuid in self.course_dictionary:
            logger.info('incrementing from {old_count} to {new_count}'.format(old_count=self.course_dictionary[course_uuid]['count'],new_count=self.course_dictionary[course_uuid]['count']+course_run_count))
            self.course_dictionary[course_uuid]['count'] += course_run_count
        else:
            logger.info('setting to {count}'.format(count=course_run_count))
            self.course_dictionary[course_uuid] = {'course':course, 'count':course_run_count}

