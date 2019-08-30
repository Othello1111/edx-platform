"""
Python APIs exposed by the program_enrollments app to other in-process apps,
concering the structure of programs.
"""
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.catalog.utils import course_run_keys_for_program, get_programs


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
