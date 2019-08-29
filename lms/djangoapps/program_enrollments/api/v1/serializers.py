"""
API Serializers
"""
from __future__ import absolute_import

from rest_framework import serializers
from six import text_type

from lms.djangoapps.program_enrollments.models import (
    ProgramCourseEnrollment,
    ProgramEnrollment,
)
from lms.djangoapps.program_enrollments.grades_api import (
    ProgramCourseGradeError,
    ProgramCourseGradeOk,
)

from .constants import (
    CourseRunProgressStatuses,
    ProgramEnrollmentResponseStatuses,
    ProgramCourseEnrollmentResponseStatuses,
)


class InvalidStatusMixin(object):
    """
    Mixin to provide has_invalid_status method
    """
    def has_invalid_status(self):
        """
        Returns whether or not this serializer has an invalid error choice on
        the "status" field.
        """
        for status_error in self.errors.get('status', []):
            if status_error.code == 'invalid_choice':
                return True
        return False


class ProgramEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for displaying enrollments in a program.
    """
    student_key = serializers.CharField(source='external_user_key')
    status = serializers.CharField()
    account_exists = serializers.SerializerMethodField()
    curriculum_uuid = serializers.UUIDField()

    class Meta(object):
        model = ProgramEnrollment

    def get_account_exists(self, obj):
        return bool(obj.user)


class ProgramEnrollmentRequestMixin(serializers.Serializer, InvalidStatusMixin):
    """
    Base fields for all program enrollment related serializers.
    """
    student_key = serializers.CharField()
    status = serializers.ChoiceField(
        allow_blank=False,
        choices=ProgramEnrollmentResponseStatuses.__ALL__,
    )


class ProgramEnrollmentCreateRequestSerializer(ProgramEnrollmentRequestMixin):
    """
    Serializer for program enrollment creation requests.
    """
    curriculum_uuid = serializers.UUIDField()


class ProgramEnrollmentModifyRequestSerializer(ProgramEnrollmentRequestMixin):
    """
    Serializer for program enrollment modification requests
    """
    pass


# pylint: disable=abstract-method
class ProgramCourseEnrollmentRequestSerializer(serializers.Serializer, InvalidStatusMixin):
    """
    Serializer for request to create a ProgramCourseEnrollment
    """
    student_key = serializers.CharField(allow_blank=False)
    status = serializers.ChoiceField(
        allow_blank=False,
        choices=ProgramCourseEnrollmentResponseStatuses.__ALL__,
    )


class ProgramCourseEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for display program-course enrollments.
    """
    student_key = serializers.SerializerMethodField()
    status = serializers.CharField()
    account_exists = serializers.SerializerMethodField()
    curriculum_uuid = serializers.SerializerMethodField()

    class Meta(object):
        model = ProgramCourseEnrollment

    def get_student_key(self, obj):
        return obj.program_enrollment.external_user_key

    def get_account_exists(self, obj):
        return bool(obj.program_enrollment.user)

    def get_curriculum_uuid(self, obj):
        return text_type(obj.program_enrollment.curriculum_uuid)


class ProgramCourseGradeResultSerializer(serializers.Serializer):
    """
    Serializer for a user's grade in a program courserun.

    Meant to be used with BaseProgramCourseGrade.
    """
    # Required
    student_key = serializers.CharField()

    # From ProgramCourseGradeOk only
    passed = serializers.BooleanField(required=False)
    percent = serializers.FloatField(required=False)
    letter_grade = serializers.CharField(required=False)

    # From ProgramCourseGradeError only
    error = serializers.CharField(required=False)


class DueDateSerializer(serializers.Serializer):
    """
    Serializer for a due date.
    """
    name = serializers.CharField()
    url = serializers.CharField()
    date = serializers.DateTimeField()


class CourseRunOverviewSerializer(serializers.Serializer):
    """
    Serializer for a course run overview.
    """
    STATUS_CHOICES = [
        CourseRunProgressStatuses.IN_PROGRESS,
        CourseRunProgressStatuses.UPCOMING,
        CourseRunProgressStatuses.COMPLETED
    ]

    course_run_id = serializers.CharField()
    display_name = serializers.CharField()
    resume_course_run_url = serializers.CharField(required=False)
    course_run_url = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    course_run_status = serializers.ChoiceField(allow_blank=False, choices=STATUS_CHOICES)
    emails_enabled = serializers.BooleanField(required=False)
    due_dates = serializers.ListField(child=DueDateSerializer())
    micromasters_title = serializers.CharField(required=False)
    certificate_download_url = serializers.CharField(required=False)


class CourseRunOverviewListSerializer(serializers.Serializer):
    """
    Serializer for a list of course run overviews.
    """
    course_runs = serializers.ListField(child=CourseRunOverviewSerializer())
