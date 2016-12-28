from unittest2 import TestCase
import tempfile
import shutil
import os
from mock import patch

from afp_cli.config import load_config


class AwsCredentialsFileTest(TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @patch("afp_cli.config.os.path.expanduser")
    def test_merges_global_and_user_configuration(self, mock_expanduser):
        # Create global config file
        global_config_dir = os.path.join(self.tempdir, "global")
        os.mkdir(global_config_dir)
        global_config_file = os.path.join(global_config_dir, "config.yaml")
        with open(global_config_file, "w") as config:
            config.write('{"spam": 1, "ham": 2}')

        # Create per-user config file
        user_config_dir = os.path.join(self.tempdir, ".afp-cli")
        os.mkdir(user_config_dir)
        user_config_file = os.path.join(user_config_dir, "config.yaml")
        with open(user_config_file, "w") as config:
            config.write('{"spam": 42, "eggs": 43}')

        mock_expanduser.return_value = user_config_dir

        # User config must overwrite the global "spam" setting.
        # Global config provides the "ham" setting.
        # User config privdes the "eggs" setting.
        config = load_config(global_config_dir=global_config_dir)
        self.assertEqual(config, {"spam": 42, "ham": 2, "eggs": 43})
