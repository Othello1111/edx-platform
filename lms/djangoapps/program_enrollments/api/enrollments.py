"""
Python APIs exposed by the program_enrollments app to other in-process apps,
concerning reading and writing program and program-course enrollments.
"""
from __future__ import absolute_import, unicode_literals

from ..constants import ProgramEnrollmentStatuses
from ..models import ProgramEnrollment


def get_program_enrollments_by_student(
        user=None,
        external_user_key=None,
        program_uuids=None,
        curriculum_uuids=None,
        statuses=None,
):
    """
    Fetch program enrollments for a student.
    At least one of `user` and `external_user_key` must be specified.

    Otherwise, the arguments are optional; specifying them will filter
    the query accordingly.

    Arguments:
        user (User|None)
        external_user_key (str|None)
        program_uuids (set[UUID|string]|None)
        curriculum_uuids (set[UUID|string]|None)
        statuses (set[str]|None)

    Returns: queryset[ProgramEnrollment]
    """
    if not (user or external_user_key):
        raise ValueError(
            "get_programs_enrollments_by_user: at least one of "
            "{{user, external_user_key}} must be specified."
        )
    return _program_enrollments_queryset(
        user=user,
        external_user_key=external_user_key,
        program_uuid=program_uuids,
        curriculum_uuid=curriculum_uuids,
        status=statuses,
    )


def get_program_enrollments_by_program(
        program_uuid,
        curriculum_uuids=None,
        users=None,
        external_user_keys=None,
        statuses=None,
):
    """
    Fetch program enrollments for a program.
    `program_uuid` must be specified.

    Otherwise, the arguments are optional; specifying them will filter
    the query accordingly.

    Arguments:
        program_uuid (UUID|string)
        curriculum_uuids (set[UUID|string]|None)
        users (set[User]|None)
        external_user_keys (set[str]|None)
        statuses (set[str]|None)

    Returns: ProgramEnrollment | None
    """
    if users:
        enrollments = enrollments.filter(user__in=users)
    if external_user_keys:
        enrollments = enrollments.filter(external_user_key__in=external_user_keys)
    if curriculum_uuids:
        enrollments = enrollments.filter(curriculum_uuid__in=curriculum_uuids)
    if statuses:
        enrollments = enrollments.filter(status__in=statuses)
    return enrollments


def get_program_enrollment_by(program_uuid, user):
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


def does_enrollment_exist(
        program_uuids=None,
        users=None,
        external_user_keys=None,
        curriculum_uuids=None,
        course_ids=None,
        statuses=None,
    ):
    """
    Check whether a user has an active program enrollment.

    Arguments:
        program_uuid (UUID)
        user (User)
        must_be_active (bool): If True, then this function will only
            return true if the enrollment as an active status --
            that is, 'enrolled' or 'pending'

    Returns: bool
    """
    return get_en


def _program_enrollments_queryset(readonly=True, **kwargs):
    """
    Get queryset of program enrollments, filtering using `kwargs`.
    If readonly is True, then we will use the Read Replica if available.
    
    None arguments are ignored.
    Lists tuples, and sets are passed to __in.
    Other arguments are tested for equality.

    Available filters and their types:
        user (User)
        external_user_key (str)
        program_uuid (UUID|string)
        curriculum_uuid (UUID|string)
        status (str)

    For example,
        _filter_program_enrollments(
            users=students, program_uuid=pgm1, status=None, readonly=False
        ) 
    Becomes:
        ProgramEnrollment.filter(users__in=students, program_uuid=pgm1)
    """
    filter_keys = {
        'program_uuid', 'curriculum_uuid', 'user', 'external_user_key', 'status'
    }
    bad_kwargs = set(kwargs) - filter_keys
    if bad_kwargs:
        raise ValueError("Cannot filter program enrollments on: " + str(bad_kwargs))
    filters = {}
    for field_name, filter_val in kwargs.items():
        if isinstance(filter_val, (list, set, tuple)):
            filter_key = field_name + "__in"
        else:
            filter_key = field_name
        filtres[filter_key] = filter_val
    all_enrollments = (
        ProgramEnrollment.objects_readonly() if readonly
        else ProgramEnrollment.objects.all()
    )
    return all_enrollments.filter(**filters)
