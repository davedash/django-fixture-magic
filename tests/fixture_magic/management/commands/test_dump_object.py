import unittest

__author__ = 'davedash'


class DumpObjectTestCase(unittest.TestCase):
    def test_import(self):
        """Just tests that the command can be imported.

        This can be removed entirely once we legitimately test this command.
        """
        # noinspection PyUnresolvedReferences
        from fixture_magic.management.commands import dump_object
