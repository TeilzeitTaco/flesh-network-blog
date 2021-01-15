#!/usr/bin/env python3

import os
import sys
import shutil

from functools import partial

from sqlbase import db, Author, BlogPost, Tag, TagAssociation
from compiler import compile_all_posts


BANNER = """\
-=[ Blog Manager ]=-
"""

selected_object: any = None


def get_selected_object_attribute() -> None:
    if selected_object is None:
        print("No object selected!")
        return

    attribute_name = input("Enter attribute name: ")
    if not hasattr(selected_object, attribute_name):
        print("Attribute does not exist!")
        return

    result = getattr(selected_object, attribute_name)
    print(f"The attribute \"{attribute_name}\" of the object with name \"{selected_object.name}\" has the value:")
    print(f"-> \"{result}\"")


def select_object(row_class: type) -> None:
    object_id = int(input(f"{row_class.__name__} ID: "))
    result = db.query(row_class).get(object_id)
    if not result:
        print(f"No object of type {row_class.__name__} with ID {object_id} exists.")
        return

    global selected_object
    selected_object = result
    print(f"Selected object with name \"{selected_object.name}\"!")


def show_rows(row_class: type) -> None:
    print(f"Currently registered {row_class.__name__}s:")
    for row in db.query(row_class):
        print(f" * {str(row.id).rjust(3)} - \"{row.name}\"")


def show_help(commands: any) -> None:
    print("Possible Commands:")
    for base_command in commands:
        print(f" * {base_command}", end="")
        sub_commands_string = "|".join([command for command in commands[base_command] if type(command) is str])
        if sub_commands_string:
            print(f" ({sub_commands_string})", end="")
        print()


def create_author() -> None:
    name = input("Author Name: ")
    biography = input("Biography: ")

    author = Author(name, biography)
    db.add(author)
    db.commit()


def delete_author() -> None:
    author_name = input("Author Name: ")
    author = db.query(Author).filter_by(name=author_name).first()
    if author:
        for blog_post in author.blog_posts:
            print(f"Deleted blog post \"{blog_post.name}\".")
            shutil.rmtree(blog_post.slug_path)
            db.delete(blog_post)

        db.delete(author)
        db.commit()
        print(f"Deleted author \"{author.name}\".")

    else:
        print(f"No author with name: \"{author_name}\".")


def create_blog_post() -> None:
    author_name = input("Author Name: ")
    author = db.query(Author).filter_by(name=author_name).first()
    if not author:
        print(f"No author with name: \"{author_name}\".")
        exit()

    title = input("Blog Post Title: ")

    blog_post = BlogPost(title, author)
    os.makedirs(blog_post.resources_path)

    open(blog_post.markdown_path, "w").close()

    db.add(blog_post)
    db.commit()


def delete_blog_post() -> None:
    blog_post_id = int(input("Blog Post ID: "))
    blog_post = db.query(BlogPost).get(blog_post_id)
    if blog_post:
        if os.path.exists(blog_post.slug_path):
            shutil.rmtree(blog_post.slug_path)

        db.delete(blog_post)
        db.commit()
        print(f"Deleted blog post \"{blog_post.name}\".")

    else:
        print(f"No blog post with ID: {blog_post_id}.")


def create_tag() -> None:
    tag_name = input("Tag Name: ")
    tag = Tag(tag_name)
    db.add(tag)
    db.commit()


def delete_tag() -> None:
    tag_name = input("Tag Name: ")
    tag = db.query(BlogPost).filter_by(name=tag_name).first()
    if tag:
        db.delete(tag)
        db.commit()
        print(f"Deleted tag \"{tag.name}\".")

    else:
        print(f"No tag with name: \"{tag_name}\".")


def attach_tag() -> None:
    tag_name = input("Tag Name: ")
    blog_post_id = int(input("Blog Post ID: "))

    tag = db.query(Tag).filter_by(name=tag_name).first()
    blog_post = db.query(BlogPost).get(blog_post_id)

    if not tag:
        print("Tag not found!")
        return

    if not blog_post:
        print("Post not found")
        return

    tag_association = TagAssociation(blog_post_id, tag.id)
    db.add(tag_association)
    db.commit()


def detach_tag() -> None:
    tag_name = input("Tag Name: ")
    blog_post_id = int(input("Blog Post ID: "))

    tag = db.query(Tag).filter_by(name=tag_name).first()
    blog_post = db.query(BlogPost).get(blog_post_id)

    if not tag:
        print("Tag not found!")
        return

    if not blog_post:
        print("Post not found")
        return

    tag_association = db.query(TagAssociation).filter_by(blog_post_id=blog_post_id, tag_id=tag.id).first()
    if tag_association is None:
        print("Tag is not attached to post!")
        return

    print(f"Detached tag \"{tag.name}\" from post \"{blog_post.name}\"!")
    db.delete(tag_association)
    db.commit()


def exit_program() -> None:
    print("Exiting...\n")
    sys.exit(-1)


def main() -> None:
    print(BANNER)

    commands = {
        "create": {
            "author": create_author,
            "post": create_blog_post,
            "tag": create_tag,
        },

        "delete": {
            "author": delete_author,
            "post": delete_blog_post,
            "tag": delete_tag,
        },

        "show": {
            "author": partial(show_rows, Author),
            "post": partial(show_rows, BlogPost),
            "tag": partial(show_rows, Tag),
        },

        "tag": {
            "attach": attach_tag,
            "detach": detach_tag,
        },

        "select": {
            "author": partial(select_object, Author),
            "post": partial(select_object, BlogPost),
            "tag": partial(select_object, Tag),
        },

        "get": {
            None: get_selected_object_attribute,
        },

        "compile": {
            None: compile_all_posts,
        },

        "exit": {
            None: exit_program,
        },

        "help": {
            None: lambda: show_help(commands),
        },

        "cls": {
            None: lambda: os.system("cls") if os.name == "nt" else os.system("clear")
        },
    }

    while True:
        command_list = input("> ").split()
        if not command_list:
            continue

        if len(command_list) not in [1, 2] or command_list[0] not in commands.keys():
            print("Invalid command!\n")
            continue

        base_command = commands[command_list[0]]
        sub_command_key = command_list[1] if 1 < len(command_list) else None

        if sub_command_key not in base_command.keys():
            print("Invalid sub-command!\n")
            continue

        base_command[sub_command_key]()
        print()


if __name__ == "__main__":
    main()
