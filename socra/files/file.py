import os

from socra.actions.files.should_update import ActionShouldUpdateFile
from socra.io.files import read_file
from socra.actions.files.modify_file import ActionImproveFile


class File:
    """
    Operations we can perform on a file instance
    """

    def __init__(self, file: str):
        self.file = file
        self._content = None
        self._last_read = None

        if not os.path.exists(file):
            raise FileNotFoundError(f"Target '{file}' not found.")

        # make sure target is a file (for now)
        if not self.is_file(file):
            raise ValueError(f"Target '{file}' must be a file.")

    @classmethod
    def is_file(cls, file: str) -> bool:
        return os.path.isfile(file)

    @property
    def content(self) -> str:
        should_read = False
        last_modified = os.path.getmtime(self.file)

        should_read = (
            self._content is None
            or self._last_read is None
            or self._last_read != last_modified
        )

        if should_read:
            self._content = read_file(self.file)
            self._last_read = last_modified

        return self._content

    def should_update(self, prompt: str):
        """
        Check if a file should be updated based on a prompt
        """

        a = ActionShouldUpdateFile()
        return a.run(a.Inputs(target=self.file, prompt=prompt))

    def update(self, prompt: str):
        """
        Update a file with a particular prompt
        """

        a = ActionImproveFile()
        a.run(a.Inputs(target=self.file, prompt=prompt))
        # trigger re-read
        return self.content
