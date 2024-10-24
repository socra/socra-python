import os

from socra.files import File


class Folder:
    """
    Operations we can perform on a directory instance.
    """

    def __init__(self, loc: str):
        self.loc = loc

        if not os.path.exists(loc):
            raise FileNotFoundError(f"Target '{loc}' not found.")

        if self.is_dir(loc):
            raise ValueError(f"Target '{loc}' must be a directory.")

    @classmethod
    def is_dir(cls, loc: str) -> bool:
        return os.path.isdir(loc)

    @classmethod
    def create(cls, loc: str):
        """
        Create a new directory.
        """
        if os.path.exists(loc):
            raise FileExistsError(f"Directory '{loc}' already exists.")
        os.mkdir(loc)
        return cls(loc)

    def choose_mutation(self, prompt: str):
        """
        Map a prompt to a mutation
        """
        pass

    def add_folder(self, name: str) -> File:
        """
        Add a file to the directory.
        """

        return File.create(os.path.join(self.loc, name))

    def add_directory(self, name: str) -> "Folder":
        """
        Add a child directory to the directory.
        """

        return Folder.create(os.path.join(self.loc, name))

    def rename(self, new_name: str):
        """
        Rename the directory.
        """
        os.rename(self.loc, new_name)
        self.loc = new_name
