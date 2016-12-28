from afp_cli.cli import main
from unittest2 import TestCase


class CliTest(TestCase):
    def test_importing_cli_works(self):
        # If we get here, afp_cli.cli has no syntax errors or broken imports.
        print(main)
