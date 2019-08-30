"""
Python APIs exposed by the program_enrollments app to other in-process apps,
concering the structure of programs.
"""
from uuid import UUID

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.catalog.utils import course_run_keys_for_program, get_programs


def get_program_data(program_uuid):
    """
    Returns program data from the Discovery cache,
    or None if program does not exist or `program_uuid` isn't a valid UUID.

    Arguments:
        program_uuid (UUID|string)

    Returns: dict | None
    """
    if isinstance(program_uuid, UUID):
        uuid = program_uuid
    else:
        try:
            uuid = UUID(program_uuid)
        except ValueError:
            return None
    return get_programs(uuid=str(uuid))


def does_program_exist(program_uuid):
    """
    Check whether a program exists in the Discovery cache.

    Arguments:
        program_uuid (UUID|string)

    Returns: bool
    """
    return get_program_data(program_uuid) is not None


def does_course_run_exist_in_program(program_uuid, course_run_id):
    """
    Check whether a course run is part of the given program in the
    Discovery cache.

    Returns True if:
        * program_uuid and course_run_id are valid AND
        * program exists AND
        * course run is part of program
    Returns False otherwise.

    Arguments:
        program_uuid (UUID|string)
        course_run_id (CourseKey|string)

    Returns: bool
    """
    program = get_program_data(program_uuid)
    if not program:
        return False
    if isinstance(course_run_id, CourseKey):
        course_run_key = course_run_id
    else:
        try:
            course_run_key = CourseKey.from_string(course_run_id)
        except InvalidKeyError:
            return False
    # We just load all the course keys in the program and check if
    # course_run_key is in it.
    # If this becomes a performance issue, we could instead write a new
    # catalog utility to function to compare course keys while walking the
    # program structure instead of building a set.
    course_run_ids = course_run_keys_for_program(program)
    return course_run_key in (
        CourseKey.from_string(course_run_id)
        for course_run_id in course_run_ids
    )
