import typing
from socra.agents.base import Agent
from socra.agents.file_system.actions import (
    create_directory,
    create_file,
    list_files_and_folders,
    rename_file_or_folder,
    update_file,
)


class FileSystemAgent(Agent):
    key: str = "file_system"
    name: str = "use file system"
    description: str = "Create, update, list, and manipulate files and folders on the local file system. Call to perform any actions on files."

    children: typing.List[Agent] = [
        Agent(
            key="create_file",
            name="Create File",
            description="Create a new file. Must already have the file path and file name in mind.",
            runs=create_file,
        ),
        Agent(
            key="update_file",
            name="Update File",
            description="Update the contents of a file.",
            runs=update_file,
        ),
        Agent(
            key="create_directory",
            name="Create Directory",
            description="Create a new directory.",
            runs=create_directory,
        ),
        Agent(
            key="rename",
            name="rename file or folder",
            description="Rename a file or folder. Must already have the previous and new paths in mind.",
            runs=rename_file_or_folder,
        ),
        Agent(
            key="list_files_and_folders",
            name="List Files and Folders",
            description="List all files and folders for a given path. You must already have the path in mind.",
            runs=list_files_and_folders,
        ),
    ]
