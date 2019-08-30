""" Utility functions related to database queries """
from __future__ import absolute_import

from django.conf import settings


def use_read_replica_if_available(queryset):
    """
    If there is a database called 'read_replica',
    use that database for the queryset / manager.
    """
    return queryset.using("read_replica") if "read_replica" in settings.DATABASES else queryset


class ReadOnlyObjectsMixin(object):
    """
    Defines a utility classmethod `objects_readonly`,
    allowing querying like:
        ProgramEnrollments.objects_readonly().filter(...)
    as opposed to:
        use_read_replica_if_available(ProgramEnrollments.objects.filter(...))

    This is purely a wrapper around `use_read_replica_if_available`
    for the purpose of syntactic convenience.

    Assumes that subclass is a model with a manager named `objects`.
    """

    @classmethod
    def objects_readonly(cls):
        """
        Returns the the default queryset of `cls.objects`, using the
        read replica if it is available, and the default database if not.
        """
        return use_read_replica_if_available(cls.objects.all())
