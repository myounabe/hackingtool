import unittest
from unittest.mock import patch, MagicMock
import os

from tools.tool_manager import Tool, ToolManager


class TestTool(unittest.TestCase):

    def _make_tool(self, name="nmap"):
        return Tool(
            name=name,
            description="Network scanner",
            install_command="apt-get install -y nmap",
            category="network",
            repo_url="https://github.com/nmap/nmap",
            dependencies=["libssl-dev"],
        )

    @patch("tools.tool_manager.shutil.which", return_value="/usr/bin/nmap")
    def test_is_installed_true(self, _mock):
        tool = self._make_tool()
        self.assertTrue(tool.is_installed())

    @patch("tools.tool_manager.shutil.which", return_value=None)
    def test_is_installed_false(self, _mock):
        tool = self._make_tool()
        self.assertFalse(tool.is_installed())

    @patch("tools.tool_manager.subprocess.run")
    def test_install_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        tool = self._make_tool()
        result = tool.install()
        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch("tools.tool_manager.subprocess.run",
           side_effect=__import__("subprocess").CalledProcessError(1, "apt", stderr="error"))
    def test_install_failure(self, _mock):
        tool = self._make_tool()
        result = tool.install()
        self.assertFalse(result)

    @patch("tools.tool_manager.subprocess.run")
    @patch("tools.tool_manager.os.path.exists", return_value=False)
    def test_clone_repo_success(self, _exists, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        tool = self._make_tool()
        result = tool.clone_repo(target_dir="/tmp")
        self.assertTrue(result)

    def test_clone_repo_no_url(self):
        tool = Tool(name="mytool", description="x", install_command="echo", category="misc")
        result = tool.clone_repo()
        self.assertFalse(result)

    @patch("tools.tool_manager.os.path.exists", return_value=True)
    def test_clone_repo_already_exists(self, _mock):
        tool = self._make_tool()
        result = tool.clone_repo(target_dir="/tmp")
        self.assertTrue(result)


class TestToolManager(unittest.TestCase):

    def setUp(self):
        self.manager = ToolManager()
        self.manager.register(Tool("nmap", "scanner", "apt install nmap", "network"))
        self.manager.register(Tool("sqlmap", "sql injection", "apt install sqlmap", "web"))
        self.manager.register(Tool("hydra", "brute force", "apt install hydra", "network"))

    def test_get_all(self):
        self.assertEqual(len(self.manager.get_all()), 3)

    def test_get_by_category(self):
        network_tools = self.manager.get_by_category("network")
        self.assertEqual(len(network_tools), 2)
        names = [t.name for t in network_tools]
        self.assertIn("nmap", names)
        self.assertIn("hydra", names)

    def test_get_by_category_case_insensitive(self):
        tools = self.manager.get_by_category("WEB")
        self.assertEqual(len(tools), 1)

    def test_get_by_category_empty(self):
        tools = self.manager.get_by_category("nonexistent")
        self.assertEqual(tools, [])

    @patch("tools.tool_manager.shutil.which", return_value=None)
    @patch.object(Tool, "install", return_value=True)
    def test_install_all(self, mock_install, _mock_which):
        self.manager.install_all()
        self.assertEqual(mock_install.call_count, 3)


if __name__ == "__main__":
    unittest.main()
