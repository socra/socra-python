import typing
from socra.agents.base import Agent
from socra.agents.file_system.actions import create_directory, create_file, update_file


class FileSystemAgent(Agent):
    key: str = "file_system"
    name: str = "use file system"
    description: str = (
        "Create, update, and manipulate files on the local file system. Call to perform any actions on files."
    )

    children: typing.List[Agent] = [
        Agent(
            key="files",
            name="Files",
            description="Create, update, and manipulate files.",
            children=[
                Agent(
                    key="create_file",
                    name="Create File",
                    description="Create a new file.",
                    runs=create_file,
                ),
                Agent(
                    key="update_file",
                    name="Update File",
                    description="Update the contents of a file.",
                    runs=update_file,
                ),
            ],
        ),
        Agent(
            key="directories",
            name="Directories",
            description="Create, update, and manipulate directories.",
            children=[
                Agent(
                    key="create_directory",
                    name="Create Directory",
                    description="Create a new directory.",
                    runs=create_directory,
                ),
            ],
        ),
    ]
