"""
Python APIs exposed by the program_enrollments app to other in-process apps,
concerning reading and writing program and program-course enrollments.
"""
from __future__ import absolute_import, unicode_literals

from ..constants import ProgramEnrollmentStatuses
from ..models import ProgramEnrollment


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
        return ProgramEnrollment.objects_readonly().get(
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
    return ProgramEnrollment.objects_readonly().get(
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
    return ProgramEnrollment.objects_readonly().get(
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
    return ProgramEnrollment.objects_readonly().filter(
        program_uuid=program_uuid,
        user=user,
        status__in=ProgramEnrollmentStatuses.__ACTIVE__,
    )
