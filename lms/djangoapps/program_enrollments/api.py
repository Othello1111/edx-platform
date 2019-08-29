"""
Python APIs exposed by the program_enrollments app to other in-process apps.
"""
from __future__ import absolute_import, unicode_literals

from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.catalog.utils import (
    course_run_keys_for_program,
    get_programs,
)
from util.query import use_read_replica_if_available

from .constants import *  # pylint: disable=wildcard-import
from .models import ProgramCourseEnrollment, ProgramEnrollment


def get_program_enrollment_by_external_key(program_uuid, external_key):
    """
    Fetch a program enrollment for a given program and external user key.
    Returns None if not found.

    Arguments:
        program_uuid (UUID)
        external_key (str)

    Returns: ProgramEnrollment | None
    """
    try:
        return ProgramEnrollment.objects.get(
            program_uuid=program_uuid,
            external_user_key=external_key,
        )
    except ProgramEnrollment.DoesNotExist:
        return None


def get_program_enrollments_by_external_keys(program_uuid, external_keys):
    """
    Fetch a queryset of program enrollments for a given program and
    set of external user keys.

    Arguments:
        program_uuid (UUID)
        external_keys (iterable[str])

    Returns: QuerySet[ProgramEnrollment]
    """
    return ProgramEnrollment.objects.get(
        program_uuid=program_uuid,
        external_user_key__in=external_keys,
    )


def get_program_enrollment_by_user(program_uuid, user):
    """
    Fetch a program enrollment for a given program and user.
    Returns None if not found.

    Arguments:
        program_uuid (UUID)
        user (User)

    Returns: ProgramEnrollment | None
    """
    return ProgramEnrollment.objects.get(
        program_uuid=program_uuid,
        user=user,
    )


def is_user_actively_enrolled(program_uuid, user):
    """
    Check whether a user has an active program enrollment.
    
    At this time, an "actively enrolled" means that a matching program
    enrollment exists with the status 'enrolled'.
    
    Arguments:
        program_uuid (UUID)
        user (User)

    Returns: bool
    """
    return ProgramEnrollment.objects.filter(
        program_uuid=program_uuid,
        user=user,
        status__in=ProgramEnrollmentStatuses.__ACTIVE__,
    )


def does_program_exist(program_uuid):
    """
    Check whether a program exists in the Discovery cache.

    Arguments:
        program_uuid (UUID)
    
    Returns: bool
    """
    return get_programs(uuid=program_uuid) is not None


def does_course_run_exist_in_program(program_uuid, course_key):
    """
    Check whether a course run is part of the given program in the
    Discovery cache.

    Returns True iff program exists AND course run is part of it.

    Arguments:
        program_uuid (UUID)
        course_key (CourseKey)
    
    Returns: bool
    """
    program = get_programs(uuid=program_uuid)
    if not program:
        return None
    # We just load all the course keys in the program and check if
    # course_key is in it.
    # If this becomes a performance issue, we could instead write a new
    # catalog utility to function to compare course keys while walking the
    # program structure instead of building a set.
    course_run_ids = course_run_keys_for_program(program)
    return course_key in (
        CourseKey.from_string(course_run_id)
        for course_run_id in course_run_ids
    )

