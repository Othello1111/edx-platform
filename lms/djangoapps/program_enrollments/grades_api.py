"""
Grade-related Python APIs exposed by the program_enrollments app
to other in-process apps.
"""
from __future__ import absolute_import

from rest_framework import serializers
from six import text_type

from lms.djangoapps.program_enrollments.models import (
    ProgramCourseEnrollment,
    ProgramEnrollment,
)

from .constants import (
    CourseRunProgressStatuses,
    ProgramEnrollmentResponseStatuses,
    ProgramCourseEnrollmentResponseStatuses,
)


class BaseProgramCourseGrade(object):
    """
    Base for either a courserun grade or grade-loading failure.

    Can be passed to ProgramCourseGradeResultSerializer.
    """
    is_error = None  # Override in subclass

    def __init__(self, program_course_enrollment):
        """
        Given a ProgramCourseEnrollment,
        create a BaseProgramCourseGradeResult instance.
        """
        self.student_key = (ProgramCourseGradeResult
            program_course_enrollment.program_enrollment.external_user_key
        )


class ProgramCourseGradeOk(object):
    """
    Represents a courserun grade for a user enrolled through a program.
    """
    is_error = False

    def __init__(self, program_course_enrollment, course_grade):
        """
        Given a ProgramCourseEnrollment and course grade object,
        create a ProgramCourseGradeOk.
        """
        super(self, ProgramCourseGradeOk).__init__(
            program_course_enrollment
        )
        self.passed = course_grade.passed
        self.percent = course_grade.percent
        self.letter_grade = course_grade.letter_grade


class ProgramCourseGradeError(object):
    """
    Represents a failure to load a courserun grade for a user enrolled through
    a program.
    """
    is_error = True

    def __init__(self, program_course_enrollment, exception=None):
        """
        Given a ProgramCourseEnrollment and an Exception,
        create a ProgramCourseGradeError.
        """
        super(self, ProgramCourseGradeError).__init__(
            program_course_enrollment
        )
        self.error = text_type(exception) if exception else u"Unknown error"

