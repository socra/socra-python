from socra.agents.context import Context
import os
import typing

from socra.parsers import parse_json
from socra.io.files import read_file, write_file
import socra
from socra.utils.decorators import throttle


def create_file(context: Context):
    """
    Create a new file
    """
    file_path = get_file_path(context)

    # next, make sure file path does not exist
    context.start_thinking(f"Checking if file path exists: {file_path}")
    if os.path.exists(file_path):
        # if file path is a directory, return taht
        if os.path.isdir(file_path):
            context.stop_thinking(
                f"File path is a directory. Need to ask user for a file name: {file_path}"
            )
            return

        context.stop_thinking(f"File already exists: {file_path}")
        return
    context.stop_thinking(f"File path does not exist: {file_path}")

    # next, create the file with blank content
    context.start_thinking(f"Creating a new file at {file_path}")
    write_file(file_path, "")
    context.stop_thinking(f"Created a new file at {file_path}")

    # finally, we'll modify the file content
    modify_file_content(context, file_path)


def create_directory(context: Context):
    file_path = get_file_path(context)

    if os.path.exists(file_path):
        context.start_thinking(f"Checking if file path exists: {file_path}")
        context.stop_thinking(f"Path path already exists: {file_path}")
        return

    context.start_thinking(f"Creating a new directory at {file_path}")
    os.makedirs(file_path)
    context.stop_thinking(
        f"I successfully created the directory at {file_path}. I will now move on."
    )


def list_files_and_folders(context: Context):
    file_path = get_file_path(context)

    # next, make sure file path exists
    if not os.path.exists(file_path):
        context.stop_thinking(f"File path '{file_path}' does not exist")

    context.start_thinking(f"Listing files and folders at {file_path}")
    files = os.listdir(file_path)
    context.stop_thinking(f"Files and folders at {file_path}: {files}")


def rename_file_or_folder(context: Context):
    old_path, new_path = get_old_and_new_file_paths(context)

    # next, make sure file path exists
    if not os.path.exists(old_path):
        context.start_thinking(f"Checking if file path exists: {old_path}")
        context.stop_thinking(f"Path does not exist '{old_path}' does not exist")

    context.start_thinking(f"Renaming {old_path} to {new_path}")
    os.rename(old_path, new_path)
    context.stop_thinking(f"DONE: Successfully renamed {old_path} to {new_path}.")


def get_old_and_new_file_paths(context: Context) -> typing.Tuple[str, str]:
    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=get_old_and_new_file_paths_prompt,
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    context.start_thinking("Getting old and new file paths")

    @throttle(0.1)
    def on_chunk(chunk):
        context.spinner.spin()

    cr = socra.Completion(
        model,
        prompt,
        # mock_response=inputs.mock_response,
        on_chunk=on_chunk,
    )
    resp = cr.process()
    context.track_completion(cr)

    content = resp.content
    dct = parse_json(content)
    if "old_path" not in dct:
        raise ValueError("Missing 'old_path' in response")
    if "new_path" not in dct:
        raise ValueError("Missing 'new_path' in response")

    old_path = dct["old_path"]
    new_path = dct["new_path"]
    context.stop_thinking(f"Extracted old and new file paths: {old_path}, {new_path}")

    return old_path, new_path


get_old_and_new_file_paths_prompt = """Based on the context above, extract the old and new file paths from the context.

Your response must be in JSON format, and should include the following keys:
- old_path: The old path of the file or folder
- new_path: The new path of the file or folder

Example:
{{
    "old_path": "path/to/old.py",
    "new_path": "path/to/new.py",
}}

Respond only in JSON format.
"""


def get_file_path(context: Context) -> str:
    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=get_file_path_prompt,
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    context.start_thinking("Getting file path")

    @throttle(0.1)
    def on_chunk(chunk):
        context.spinner.spin()

    cr = socra.Completion(
        model,
        prompt,
        # mock_response=inputs.mock_response,
        on_chunk=on_chunk,
    )
    resp = cr.process()
    context.track_completion(cr)

    content = resp.content
    dct = parse_json(content)
    if "path" not in dct:
        raise ValueError("Missing 'path' in response")

    path = dct["path"]
    context.stop_thinking(f"Extracted file path: {path}")

    return path


get_file_path_prompt = """Based on the context above, extract the file path from the context.

Your response must be in JSON format, and should include the following keys:
- path: The path of the file

Example:
{{
    "path": "...",
}}

Respond only in JSON format.
"""


def update_file(context: Context):
    # first, we need to get the file path from the context
    file_path = get_file_path(context)

    # next, make sure file path exists
    if not os.path.exists(file_path):
        return f"File path '{file_path}' does not exist"

    # determine if the file should be updated.
    should_update = should_update_file_content(context, file_path)

    # now, we'll perform an action to modify the file.
    if should_update:
        modify_file_content(context, file_path)


def should_update_file_content(context: Context, file_path: str) -> bool:
    """
    Decide if file path should be update.
    """

    file_content = read_file(file_path)

    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)

    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=should_update_file_content_prompt.format(content=file_content),
            ),
        ]
    )

    context.start_thinking(f"Deciding whether to update {file_path}")

    @throttle(0.1)
    def on_chunk(chunk):
        context.spinner.spin()

    cr = socra.Completion(
        model,
        prompt,
        # mock_response=inputs.mock_response,
        on_chunk=on_chunk,
    )
    resp = cr.process()
    context.track_completion(cr)

    content = resp.content

    # parse JSON response
    dct = parse_json(content)

    if "should_update" not in dct:
        raise ValueError("Missing 'should_update' in response")
    if "reason" not in dct:
        raise ValueError("Missing 'reason' in response")

    should_update = dct["should_update"]

    if should_update:
        message = f"Decided to update {file_path} because {dct['reason'].lower()}"
    else:
        message = f"Decided not to update {file_path} because {dct['reason'].lower()}"

    context.stop_thinking(message)
    return should_update


should_update_file_content_prompt = """Base on the context above and the content below, decide whether or not the file should be updated.


File content:
<content>
{content}
</content>

Your response must be in JSON format, and should include the following keys:
- should_update: Boolean value indicating whether the file should be updated
- reason: Extremely brief thought on why the file should be updated or not

Example if the file should be updated:
{{
    "should_update": true,
    "reason": "the file..."
}}

Example if the file should not be updated:
{{
    "should_update": false,
    "reason": "the file..."
}}

Respond only in JSON format.
"""


def modify_file_content(context: Context, file_path: str):
    file_content = read_file(file_path)

    prompt = socra.Prompt(
        messages=[
            *context.messages,
            socra.Message(
                role=socra.Message.Role.HUMAN,
                content=modify_file_content_prompt.format(content=file_content),
            ),
        ]
    )
    model = socra.Model.for_key(socra.Model.Key.GPT_4O_MINI_2024_07_18)
    context.start_thinking("Modifying the file content")

    @throttle(0.1)
    def on_chunk(chunk):
        context.spinner.spin()

    cr = socra.Completion(
        model,
        prompt,
        # mock_response=inputs.mock_response,
        on_chunk=on_chunk,
    )
    resp = cr.process()
    context.track_completion(cr)

    content = resp.content
    dct = parse_json(content)
    if "content" not in dct:
        raise ValueError("Missing 'content' in response")
    if "reasoning" not in dct:
        raise ValueError("Missing 'reasoning' in response")

    content = dct["content"]
    reasoning = dct["reasoning"]

    context.stop_thinking(f"Modified the file content: {reasoning}")
    write_file(file_path, content)


modify_file_content_prompt = """Based on the context above, modify the below file content.

File content:
<content>
{content}
</content>

Your response must be in JSON format, and should include the following keys:
- content: The new content of the file
- reasoning: Extremely brief thought on what was updated and why

Example:
{{
    "content": "...",
    "reasoning": "the content..."
}}

Respond only in JSON format.
"""
