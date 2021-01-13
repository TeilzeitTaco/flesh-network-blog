import os
import re
import sys

import markdown
import hashlib

from typing import Dict
from shutil import copyfile, rmtree
from sqlbase import db, BlogPost


MARKDOWN_IMAGE_REFERENCE = re.compile(r"!\[([^]]*?)]\(([^)]*?)( \"([^\"]*?)\")?\)", re.IGNORECASE)

GENERATED_RESOURCES_PATH = "static/gen/res/"
RESOURCE_FILE_NAME_LENGTH = 16


def process_resource_files(resource_path: str) -> Dict[str, str]:
    resources_name_mapping = dict()
    for root, _, files in os.walk(resource_path, topdown=True):
        for file in files:
            # Get file path and file extension
            file_path = os.path.join(root, file)
            extension = "." + file.rsplit(".",  1)[-1]

            # Hash file contents, this is the new file name
            new_file_name = hash_file(file_path) + extension
            resources_name_mapping[file] = new_file_name

            # Copy the file to the resource dir
            copyfile(file_path, GENERATED_RESOURCES_PATH + new_file_name)

    return resources_name_mapping


def post_process_image_clause(markdown_src: str, resources_name_mapping: Dict[str, str]) -> str:
    def processor(match) -> str:
        # Replace the image filename in a markdown image embed with the
        # newly generated hash filename referring to the file which is
        # now stored in the static/gen/res/ folder.
        alt_text = match.group(1)
        resource_file_name = match.group(2)
        hashed_file_name = resources_name_mapping.get(resource_file_name)

        # If the filename isn't in the mapping, the file doesn't exist.
        if hashed_file_name is None:
            print(f"\nError! Missing resource \"{resource_file_name}\"!")
            sys.exit(-1)

        title_text = match.group(4)
        new_markdown = f"![{alt_text}](/{GENERATED_RESOURCES_PATH + hashed_file_name}"
        if title_text is not None:
            new_markdown += f" \"{title_text}\""

        return new_markdown + ")"

    return MARKDOWN_IMAGE_REFERENCE.sub(processor, markdown_src)


def read_file(path: str) -> str:
    if not os.path.exists(path):
        print(f"\nError! Missing file: \"{path}\"!")
        sys.exit(-1)

    with open(path, "r") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def hash_file(path: str) -> str:
    with open(path, "rb") as f:
        hash_sum = hashlib.shake_256()
        hash_sum.update(f.read())

    return hash_sum.hexdigest(RESOURCE_FILE_NAME_LENGTH)


def compile_all_posts() -> None:
    if os.path.exists(GENERATED_RESOURCES_PATH):
        rmtree(GENERATED_RESOURCES_PATH)
    os.mkdir(GENERATED_RESOURCES_PATH)

    for blog_post in db.query(BlogPost):
        print(f"Compiling blog post \"{blog_post.title}\"... ", end="")

        # Process the files in the res/ directory
        resources_name_mapping = process_resource_files(blog_post.resources_path)

        # Convert the markdown post content into a HTML file.
        markdown_src = read_file(blog_post.markdown_path)
        markdown_src = post_process_image_clause(markdown_src, resources_name_mapping)
        html_src = markdown.markdown(markdown_src)
        write_file(blog_post.html_path, html_src)

        print("ok")
