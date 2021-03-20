import hashlib
import imghdr
import os
import re
import sys
from shutil import copyfile, rmtree
from typing import Optional, NoReturn

import markdown
from PIL import Image

from sqlbase import db, BlogPost, Author, Tag, FileResource

RESOURCE_PATH_INSERT = re.compile(r"{{(.*?)}}")
GENERATED_RESOURCES_PATH = "static/gen/res/"
RESOURCE_FILE_NAME_LENGTH = 16
MAX_THUMBNAIL_WIDTH = 512
IMAGE_FORMAT = "png"


def done() -> None:
    print("Done!")


def in_res_path(path: str) -> str:
    return GENERATED_RESOURCES_PATH + path


def compiler_error(message: str) -> NoReturn:
    print(f"\nError! {message}")
    sys.exit(-1)


def has_prefix(string: str, prefix: str) -> Optional[str]:
    if string.lower().startswith(prefix.lower()):
        return string[len(prefix):].strip()


def file_name_to_title(file_name: str) -> str:
    return " ".join(file_name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").split()).title()


def process_resource_files(blog_post: BlogPost) -> None:
    for root, _, files in os.walk(blog_post.resources_path, topdown=True):
        for file in files:
            # Get file path and file extension
            file_path = os.path.join(root, file)
            extension = "." + file.rsplit(".",  1)[-1]

            # Hash file contents, this is the new file name
            file_hash = hash_file(file_path)
            file_title = file_name_to_title(file)

            # Optimize images for web
            if imghdr.what(file_path):
                full_size_file_name = f"{file_hash}.{IMAGE_FORMAT}"
                thumbnail_file_name = f"{file_hash}-thumb.{IMAGE_FORMAT}"

                # Add database entries
                db.add(FileResource(full_size_file_name, "high-res-" + file, file_title, blog_post))
                db.add(FileResource(thumbnail_file_name, file, file_title + " (Thumbnail)", blog_post))

                with Image.open(file_path) as image:
                    image.thumbnail((MAX_THUMBNAIL_WIDTH, -1))
                    image.save(in_res_path(thumbnail_file_name), IMAGE_FORMAT, optimize=True)

                with Image.open(file_path) as image:
                    image.save(in_res_path(full_size_file_name), IMAGE_FORMAT, optimize=True)

            else:
                # Copy the file to the resources dir
                new_file_name = file_hash + extension
                db.add(FileResource(new_file_name, file, file_title, blog_post))
                copyfile(file_path, in_res_path(new_file_name))

    db.commit()


def pre_process_markdown(markdown_src: str, blog_post: BlogPost) -> str:
    def processor(match: any) -> str:
        # The reference syntax inside of the {{ brackets }}.
        reference = match.group(1).strip()

        # A file reference
        if decoded_reference := has_prefix(reference, "file:"):
            name_mapping = {fr.clear_name: fr.name for fr in blog_post.file_resources}
            if hashed_file_name := name_mapping.get(decoded_reference):
                return "/" + in_res_path(hashed_file_name)

            # If the filename isn't in the mapping, the file doesn't exist.
            compiler_error(f"Missing resource \"{decoded_reference}\"!")

        # A author reference
        if decoded_reference := has_prefix(reference, "author:"):
            if author := db.query(Author).filter_by(name=decoded_reference).first():
                return f"/authors/{author.id}/{author.slug}/"

            compiler_error(f"Missing author \"{decoded_reference}\"!")

        # A post reference
        if decoded_reference := has_prefix(reference, "post:"):
            if post := db.query(BlogPost).get(int(decoded_reference)):
                return f"/posts/{post.id}/{post.slug}/"

            compiler_error(f"Missing post \"{decoded_reference}\"!")

        # A tag reference
        if decoded_reference := has_prefix(reference, "tag:"):
            if tag := db.query(Tag).filter_by(name=decoded_reference).first():
                return f"/tags/{tag.id}/{tag.slug}/"

            compiler_error(f"Missing tag \"{decoded_reference}\"!")

        compiler_error(f"Invalid reference type: \"{reference}\".")

    return RESOURCE_PATH_INSERT.sub(processor, markdown_src)


def read_file(path: str) -> str:
    if not os.path.exists(path):
        compiler_error(f"Missing file: \"{path}\"!")

    with open(path, "r", encoding="latin-1") as f:
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
    print("Cleaning directory... ", end="")
    if os.path.exists(GENERATED_RESOURCES_PATH):
        rmtree(GENERATED_RESOURCES_PATH)
    os.makedirs(GENERATED_RESOURCES_PATH)
    done()

    print("Cleaning database... ", end="")
    db.query(FileResource).delete()
    done()

    for blog_post in db.query(BlogPost):
        print(f"Compiling blog post \"{blog_post.name}\"... ", end="", flush=True)

        # Process the files in the res/ directory
        process_resource_files(blog_post)

        # Convert the markdown post content into a HTML file.
        markdown_src = read_file(blog_post.markdown_path)
        markdown_src = pre_process_markdown(markdown_src, blog_post)
        html_src = markdown.markdown(markdown_src)
        write_file(blog_post.html_path, html_src)
        done()
