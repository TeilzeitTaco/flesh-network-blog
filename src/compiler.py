import os
import re
import sys

import markdown
import hashlib

from typing import Dict, Optional, NoReturn
from shutil import copyfile, rmtree
from sqlbase import db, BlogPost, Author


RESOURCE_PATH_INSERT = re.compile(r"{{(.*?)}}")
GENERATED_RESOURCES_PATH = "static/gen/res/"
RESOURCE_FILE_NAME_LENGTH = 16


def compiler_error(message: str) -> NoReturn:
    print(f"\nError! {message}")
    sys.exit(-1)


def has_prefix(string: str, prefix: str) -> Optional[str]:
    if string.lower().startswith(prefix.lower()):
        return string[len(prefix):].strip()


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


def pre_process_markdown(markdown_src: str, resources_name_mapping: Dict[str, str]) -> str:
    def processor(match) -> str:
        # The reference syntax inside of the {{ brackets }}.
        reference = match.group(1).strip()

        # A file reference
        decoded_reference = has_prefix(reference, "file:")
        if decoded_reference:
            hashed_file_name = resources_name_mapping.get(decoded_reference)
            if hashed_file_name is None:
                # If the filename isn't in the mapping, the file doesn't exist.
                compiler_error(f"Missing resource \"{decoded_reference}\"!")

            return f"/{GENERATED_RESOURCES_PATH + hashed_file_name}"

        # A author reference
        decoded_reference = has_prefix(reference, "author:")
        if decoded_reference:
            author = db.query(Author).filter_by(name=decoded_reference).first()
            if author is None:
                compiler_error(f"Missing author \"{decoded_reference}\"!")

            return f"/authors/{author.id}/{author.slug}/"

        # A post reference
        decoded_reference = has_prefix(reference, "post:")
        if decoded_reference:
            post = db.query(BlogPost).get(int(decoded_reference))
            if post is None:
                compiler_error(f"Missing post \"{decoded_reference}\"!")

            return f"/posts/{post.id}/{post.slug}/"

        compiler_error(f"Invalid reference type: \"{reference}\".")

    return RESOURCE_PATH_INSERT.sub(processor, markdown_src)


def read_file(path: str) -> str:
    if not os.path.exists(path):
        compiler_error(f"Missing file: \"{path}\"!")

    with open(path, "r") as f:
        return f.read().strip()


def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


def hash_file(path: str) -> str:
    with open(path, "rb") as f:
        hash_sum = hashlib.shake_256()
        hash_sum.update(f.read())

    return hash_sum.hexdigest(RESOURCE_FILE_NAME_LENGTH)


def compile_all_posts() -> None:
    print("Compiling all blog posts...")
    if os.path.exists(GENERATED_RESOURCES_PATH):
        rmtree(GENERATED_RESOURCES_PATH)
    os.mkdir(GENERATED_RESOURCES_PATH)

    for blog_post in db.query(BlogPost):
        print(f"Compiling blog post \"{blog_post.name}\"... ", end="")

        # Process the files in the res/ directory
        resources_name_mapping = process_resource_files(blog_post.resources_path)

        # Convert the markdown post content into a HTML file.
        markdown_src = read_file(blog_post.markdown_path)
        markdown_src = pre_process_markdown(markdown_src, resources_name_mapping)
        html_src = markdown.markdown(markdown_src)
        write_file(blog_post.html_path, html_src)

        print("Done!")

    print("Done!")
