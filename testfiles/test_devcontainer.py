"""Exercise image directory setup without Docker or a network connection."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class DevContainerDirectories(unittest.TestCase):
    def test_single_dev_service(self):
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / ".devcontainer/devcontainer.json").read_text())
        self.assertEqual(config["dockerComposeFile"], "compose.yml")
        self.assertEqual(config["service"], "dev")
        self.assertEqual(config["runServices"], ["dev"])

    def test_mount_targets_and_server_directories(self):
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / '.devcontainer/devcontainer.json').read_text())
        dockerfile = (root / '.devcontainer/Dockerfile').read_text()
        commands = dockerfile.replace('\\\n', '').splitlines()
        setup = next(line[4:] for line in commands if line.startswith('RUN mkdir '))
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / 'home'
            setup = setup.replace('/home/vscode', str(home))
            setup = setup.replace('vscode:vscode', f'{os.getuid()}:{os.getgid()}')
            subprocess.run(['sh', '-ec', setup], check=True)
            for mount in config['mounts']:
                target = next(item[7:] for item in mount.split(',') if item.startswith('target='))
                path = Path(target.replace('/home/vscode', str(home)))
                self.assertTrue(path.is_dir(), target)
                self.assertEqual(path.stat().st_uid, os.getuid())
                self.assertEqual(path.stat().st_gid, os.getgid())
            # These are the operations that failed during VS Code startup.
            for relative in [
                '.vscode-server/bin',
                '.vscode-server/data/Machine',
                '.vscode-server/data/agentSessionData',
                '.copilot/chats',
                '.copilot/session-state',
            ]:
                path = home / relative
                path.mkdir(parents=True, exist_ok=True)
                (path / 'write-probe').write_text('ok')
            for relative in ['.config/gh', '.ssh']:
                self.assertEqual((home / relative).stat().st_mode & 0o777, 0o700)

    def test_bash_history_is_appended_each_prompt(self):
        root = Path(__file__).resolve().parents[1]
        dockerfile = (root / '.devcontainer/Dockerfile').read_text()

        self.assertIn('shopt -s histappend', dockerfile)
        self.assertIn(
            'PROMPT_COMMAND="history -a${PROMPT_COMMAND:+; $PROMPT_COMMAND}"',
            dockerfile,
        )


if __name__ == '__main__':
    unittest.main()
