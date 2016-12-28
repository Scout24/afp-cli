from afp_cli.cliv2 import main
from unittest2 import TestCase


class CliV2Test(TestCase):
    def test_importing_cliv2_works(self):
        # If we get here, afp_cli.cliv2 has no syntax errors or broken imports.
        print(main)
