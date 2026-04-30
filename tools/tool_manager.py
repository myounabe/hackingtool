import subprocess
import os
import shutil
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Tool:
    name: str
    description: str
    install_command: str
    category: str
    repo_url: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def is_installed(self) -> bool:
        """Check if the tool binary is available on PATH."""
        return shutil.which(self.name) is not None

    def install(self) -> bool:
        """Run the install command. Returns True on success."""
        try:
            result = subprocess.run(
                self.install_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"[+] {self.name} installed successfully.")
            return True
        except subprocess.CalledProcessError as exc:
            print(f"[-] Failed to install {self.name}: {exc.stderr.strip()}")
            return False

    def clone_repo(self, target_dir: str = ".") -> bool:
        """Clone the tool repository if repo_url is set."""
        if not self.repo_url:
            print(f"[-] No repo URL defined for {self.name}.")
            return False
        dest = os.path.join(target_dir, self.name)
        if os.path.exists(dest):
            print(f"[*] Repository already cloned at {dest}.")
            return True
        try:
            subprocess.run(
                ["git", "clone", self.repo_url, dest],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(f"[+] Cloned {self.repo_url} into {dest}.")
            return True
        except subprocess.CalledProcessError as exc:
            print(f"[-] Git clone failed for {self.name}: {exc.stderr.decode().strip()}")
            return False


class ToolManager:
    """Registry and manager for hacking tools."""

    def __init__(self):
        self._tools: List[Tool] = []

    def register(self, tool: Tool) -> None:
        self._tools.append(tool)

    def get_by_category(self, category: str) -> List[Tool]:
        return [t for t in self._tools if t.category.lower() == category.lower()]

    def get_all(self) -> List[Tool]:
        return list(self._tools)

    def install_all(self, category: Optional[str] = None) -> None:
        tools = self.get_by_category(category) if category else self.get_all()
        for tool in tools:
            if tool.is_installed():
                print(f"[*] {tool.name} is already installed, skipping.")
            else:
                tool.install()

    def status_report(self) -> None:
        # Added a count summary at the end so I can quickly see how many tools
        # are installed vs total without having to count the rows manually.
        print(f"{'Tool':<20} {'Category':<20} {'Installed':<10}")
        print("-" * 50)
        installed_count = 0
        for tool in self._tools:
            installed = tool.is_installed()
            if installed:
                installed_count += 1
            status = "Yes" if installed else "No"
            print(f"{tool.name:<20} {tool.category:<20} {status:<10}")
        print("-" * 50)
        print(f"Installed: {installed_count}/{len(self._tools)}")
