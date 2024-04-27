
import os
import pathlib
import subprocess
from typing import Dict, List, Tuple


class Finder:
    def __init__(self, version: str, *apps: str):
        if not version or not version.strip():
            raise ValueError(f"Illegal 'version' argument in Finder('{version}', {apps})")
        if not apps:
            raise ValueError(f"Illegal 'apps' argument in Finder('{version}', {apps})")
        self.matchers: Dict[str, pathlib.PurePath] = {app: pathlib.PurePath(f"'{app}','{app}'.exe") for app in apps}
        self.results: Dict[str, pathlib.Path] = {}
        self.version = version.strip()

    def find(self, path: pathlib.Path, recurse: bool = True) -> bool:
        try:
            for root, dirs, files in os.walk(path, followlinks=True):
                for file in files:
                    file_path = pathlib.Path(root) / file
                    for name, matcher in self.matchers.items():
                        if name not in self.results and matcher.match(file_path.name) and os.access(file_path, os.X_OK) and self.check(file_path, name, self.version):
                            self.results[name] = file_path
                            if len(self.results) == len(self.matchers):
                                return True
                if not recurse:
                    dirs.clear()
            return len(self.results) == len(self.matchers)
        except (IOError, OSError):
            return False

    def get(self, name: str) -> pathlib.Path:
        if not name or not name.strip():
            raise ValueError(f"Illegal 'name' argument in Finder.get('{name}')")
        return self.results.get(name.strip())

    def is_found(self) -> bool:
        return len(self.results) == len(self.matchers)

    def test(self, name: str, file: pathlib.Path) -> bool:
        if not name or not name.strip() or name.strip() not in self.matchers:
            raise ValueError(f"Illegal 'name' argument in Finder.test('{name}', {file})")
        if name in self.results:
            return True
        if file and file.name and self.matchers[name.strip()].match(file.name) and os.access(file, os.X_OK) and self.check(file, name, self.version):
            self.results[name] = file
            return True
        return False

    @staticmethod
    def check(executable: pathlib.Path, *match: str) -> bool:
        if not executable or not executable.exists() or not os.access(executable, os.X_OK):
            return False
        if not match or not any(match):
            return False
        try:
            command = [str(executable), "--version"]
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            if process.returncode == 0:
                output = process.stdout.lower()
                for pattern in match:
                    if pattern.lower() in output:
                        return True
            return False
        except (IOError, OSError, subprocess.CalledProcessError):
            return False

