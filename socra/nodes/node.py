import typing
from enum import Enum
import datetime
from socra.schemas import Schema
import os
from socra.io.files import read_file


class NodeType(Enum):
    FILE = "file"
    DIRECTORY = "directory"


class Node(Schema):
    """
    Object representing a node in a file system.
    """

    Type: typing.ClassVar[NodeType] = NodeType

    path: str
    """
    The path to the node.
    """

    last_modified: datetime.datetime
    """
    Last modified time of the node.
    """

    type: NodeType
    """
    The node type. Either a file or a directory.
    """

    summary: str = None
    """
    Summary of the contents of the node.
    - for files, this is the summary of the file content.
    - for directories, this is a summary of the directory contents.
    """

    content: str | None = None
    """
    File-only. The content of the file.
    """

    @property
    def name(self) -> str:
        """
        The name of the node.
        """
        return os.path.basename(self.path)

    @property
    def parent(self) -> "Node":
        """
        The parent of the node.
        """
        return Node.for_path(os.path.dirname(self.path))

    @classmethod
    def for_path(cls, path: str) -> "Node":
        """
        Create a new node for the given path.

        Args:
            path (str): The path to the node.

        Returns:
            Node: A Node object representing the file or directory.

        Raises:
            FileNotFoundError: If the specified path does not exist.
        """

        if not os.path.exists(path):
            raise FileNotFoundError(f"Target '{path}' not found.")

        is_file = os.path.isfile(path)
        # TODO: retrieve summary from cache
        if is_file:
            return Node(
                path=path,
                last_modified=datetime.datetime.fromtimestamp(os.path.getmtime(path)),
                type=NodeType.FILE,
                content=read_file(path),
            )
        else:
            return Node(
                path=path,
                last_modified=datetime.datetime.fromtimestamp(os.path.getmtime(path)),
                type=NodeType.DIRECTORY,
            )

    def save(self):
        """
        Save the node to the file system.

        If the node is a file, it saves the content to the file.
        If the node is a directory, it creates the directory.

        Raises:
            ValueError: If the node type is not recognized.
        """

        if not os.path.exists(self.path):
            # create the file or directory
            if self.type == NodeType.FILE:
                with open(self.path, "w", encoding="utf-8") as f:
                    if self.content:
                        f.write(self.content)
            elif self.type == NodeType.DIRECTORY:
                os.mkdir(self.path)
            else:
                raise ValueError(f"Unknown node type: {self.type}")
        else:
            if self.type == NodeType.FILE:
                with open(self.path, "w", encoding="utf-8") as f:
                    if self.content:
                        f.write(self.content)
            else:
                # Updating the directory's last modified time
                os.utime(self.path, None)

        # TODO: update name, summary in cache

    def get_children(self) -> typing.List["Node"]:
        """
        Get the children of the node.

        Returns:
            List[Node]: A list of child Node objects.

        Raises:
            ValueError: If the node is not a directory.
        """
        if self.type != NodeType.DIRECTORY:
            raise ValueError(f"Node '{self.path}' is not a directory.")

        return [
            Node.for_path(os.path.join(self.path, child))
            for child in os.listdir(self.path)
        ]

    def add_child(
        self,
        name: str,
        type: NodeType,
        content: str = None,
    ) -> "Node":
        """
        Add a child node to the directory.

        Args:
            name (str): The name of the child node.
            type (NodeType): The type of the child node (file or directory).
            content (str, optional): The content if the child is a file.

        Returns:
            Node: The created child Node object.

        Raises:
            ValueError: If the node is not a directory.
        """
        if self.type != NodeType.DIRECTORY:
            raise ValueError(f"Node '{self.path}' is not a directory.")

        child_path = os.path.join(self.path, name)
        if type == NodeType.FILE:
            child = Node(
                path=child_path,
                last_modified=datetime.datetime.now(),
                type=type,
                content=content,
            )
        else:
            child = Node(
                path=child_path,
                last_modified=datetime.datetime.now(),
                type=type,
            )

        child.save()

        return child

    def delete(self):
        """
        Delete the node from the file system.

        Raises:
            FileNotFoundError: If the node does not exist.
            ValueError: If the node type is not recognized.
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Node '{self.path}' does not exist.")

        if self.type == NodeType.FILE:
            os.remove(self.path)
        elif self.type == NodeType.DIRECTORY:
            os.rmdir(self.path)
        else:
            raise ValueError(f"Unknown node type: {self.type}")
