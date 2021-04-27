import imghdr
import os
import re
from shutil import copyfile, rmtree

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
    html_src = markdown.markdown(markdown_src)
    write_file(post.html_path, html_src)


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

        # An author reference
        if decoded_reference := has_prefix(reference, "author:"):
            if author := db.query(Author).filter_by(name=decoded_reference).first():
                return f"/authors/{author.id}/{author.slug}/"

            critical_error(f"Missing author \"{decoded_reference}\"!")

        # A post reference
        if decoded_reference := has_prefix(reference, "post:"):
            if post := db.query(BlogPost).get(int(decoded_reference)):
                return f"/posts/{post.id}/{post.slug}/"

            critical_error(f"Missing post \"{decoded_reference}\"!")

        # A tag reference
        if decoded_reference := has_prefix(reference, "tag:"):
            if tag := db.query(Tag).filter_by(name=decoded_reference).first():
                return f"/tags/{tag.id}/{tag.slug}/"

            critical_error(f"Missing tag \"{decoded_reference}\"!")

        critical_error(f"Invalid reference type: \"{reference}\".")

    return RESOURCE_PATH_INSERT.sub(processor, markdown_src)


def recreate_file_resources_for_post(blog_post: BlogPost):
    for file_resource in blog_post.file_resources:
        file_resource.delete()
    process_resource_files(blog_post)


def process_resource_files(blog_post: BlogPost) -> None:
    for root, _, files in os.walk(blog_post.resources_path, topdown=True):
        for file in files:
            file_path = os.path.join(root, file)
            extension = "." + file.rsplit(".",  1)[-1]

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
