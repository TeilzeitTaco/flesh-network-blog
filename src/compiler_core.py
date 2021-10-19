import imghdr
import os
import re
from shutil import copyfile, rmtree
from typing import Optional

import markdown
from PIL import Image

from sqlbase import BlogPost, Tag, Author, db, FileResource
from misc import critical_error, has_prefix, in_res_path, read_file, write_file, file_name_to_title, hash_file, done, \
    GENERATED_RESOURCES_PATH

RESOURCE_PATH_INSERT = re.compile(r"{{(.*?)}}")
MAX_THUMBNAIL_WIDTH = 512
IMAGE_FORMAT = "png"


def compile_post(post: BlogPost) -> None:
    recreate_file_resources_for_post(post)
    convert_markdown_for_post(post)


def convert_markdown_for_post(post: BlogPost) -> None:
    markdown_src = read_file(post.interstage_path)
    markdown_src = pre_process_markdown(markdown_src, post)
    html_src = markdown.markdown(markdown_src, extensions=["sane_lists", "md_in_html", "extra"])
    write_file(post.html_path, html_src)


class MarkupReference:
    def __init__(self, object_class: type, resolve_by_name: bool):
        self.__resolve_by_name = resolve_by_name
        self.__object_class = object_class
        self.__keyword = object_class.__name__.lower()

    def __produce_value_string(self, value: any) -> str:
        return f"\"{value}\"" if self.__resolve_by_name else value

    def produce_reference(self, value: any) -> str:
        """Create a reference of this type to be inserted into text."""
        if self.__resolve_by_name and type(value) is int:
            value = db.query(self.__object_class).get(value).name
        return f"{{{{ {self.__keyword}: {self.__produce_value_string(value)} }}}}"

    def maybe_match(self, reference: str) -> Optional[str]:
        """Maybe match and process a reference of this type."""
        if decoded_reference := has_prefix(reference, self.__keyword + ":"):
            if self.__resolve_by_name:
                decoded_reference = decoded_reference.strip("\"' ")
                found_object = db.query(self.__object_class).filter_by(name=decoded_reference).first()
            else:
                found_object = db.query(self.__object_class).get(int(decoded_reference))
            if found_object:
                return f"/{self.__keyword}s/{found_object.id}/{found_object.slug}/"

            user_provided_value = self.__produce_value_string(decoded_reference)
            critical_error(f"Missing {self.__keyword} {user_provided_value}!")


BLOGPOST_MARKUP_REFERENCE = MarkupReference(BlogPost, False)
AUTHOR_MARKUP_REFERENCE = MarkupReference(Author, True)
TAG_MARKUP_REFERENCE = MarkupReference(Tag, True)


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
            critical_error(f"Missing resource \"{decoded_reference}\"!")

        # Simple references
        for possible_reference in [BLOGPOST_MARKUP_REFERENCE, AUTHOR_MARKUP_REFERENCE, TAG_MARKUP_REFERENCE]:
            if result := possible_reference.maybe_match(reference):
                return result

        critical_error(f"Invalid reference type: \"{reference}\".")

    return RESOURCE_PATH_INSERT.sub(processor, markdown_src)


def recreate_file_resources_for_post(blog_post: BlogPost):
    for file_resource in blog_post.file_resources:
        db.delete(file_resource)
    db.commit()
    process_resource_files(blog_post)


def process_resource_files(blog_post: BlogPost) -> None:
    for root, _, files in os.walk(blog_post.resources_path, topdown=True):
        for file in files:
            file_path = os.path.join(root, file)
            extension = "." + file.rsplit(".", 1)[-1]

            # Hash file contents, this is the new file name
            file_hash = hash_file(file_path)
            file_title = file_name_to_title(file)

            # Optimize images for web (create thumbnails)
            if imghdr.what(file_path):
                full_size_file_name = f"{file_hash}.{IMAGE_FORMAT}"
                thumbnail_file_name = f"{file_hash}-thumb.{IMAGE_FORMAT}"

                db.add(FileResource(full_size_file_name, "high-res-" + file, file_title, blog_post,
                                    is_image=True, is_thumbnail=False))

                db.add(FileResource(thumbnail_file_name, file, file_title + " (Thumbnail)", blog_post,
                                    is_image=True, is_thumbnail=True))

                with Image.open(file_path) as image:
                    image.thumbnail((MAX_THUMBNAIL_WIDTH, -1))
                    image.save(in_res_path(thumbnail_file_name), IMAGE_FORMAT, optimize=True)

                with Image.open(file_path) as image:
                    image.save(in_res_path(full_size_file_name), IMAGE_FORMAT, optimize=True)

            else:
                # Copy the file to the resources dir, no processing
                new_file_name = file_hash + extension
                db.add(FileResource(new_file_name, file, file_title, blog_post))
                copyfile(file_path, in_res_path(new_file_name))

    db.commit()


def clean_compiler_output() -> None:
    print("Cleaning directory... ", end="")
    if os.path.exists(GENERATED_RESOURCES_PATH):
        rmtree(GENERATED_RESOURCES_PATH)
    os.makedirs(GENERATED_RESOURCES_PATH)
    done()
