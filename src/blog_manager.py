#!/usr/bin/env python3

import os
import sys
import shutil

from functools import partial

from sqlalchemy.exc import IntegrityError

from sqlbase import db, Author, BlogPost, Tag, TagAssociation
from compiler import compile_all_posts


ERROR_NO_OBJECT_SELECTED = "No object selected!"
ERROR_ATTRIBUTE_DOES_NOT_EXIST = "Attribute does not exist!"

BANNER = """\
-=[ Blog Manager ]=-
"""

selected_object: any = None


def save_tip() -> None:
    print("You probably want to save.")


def get_selected_object_attribute() -> None:
    if selected_object is None:
        print(ERROR_NO_OBJECT_SELECTED)
        return

    attribute_name = input("Enter attribute name: ")
    if not hasattr(selected_object, attribute_name):
        print(ERROR_ATTRIBUTE_DOES_NOT_EXIST)
        return

    result = getattr(selected_object, attribute_name)
    print(f"The attribute \"{attribute_name}\" of the object with name \"{selected_object.name}\" has the value" +
          f" \"{result}\" of the type \"{result.__class__.__name__}\"")


def set_selected_object_attribute() -> None:
    if selected_object is None:
        print(ERROR_NO_OBJECT_SELECTED)
        return

    attribute_name = input("Enter attribute name: ")
    if not hasattr(selected_object, attribute_name):
        print(ERROR_ATTRIBUTE_DOES_NOT_EXIST)
        return

    type_name = input("Enter attribute type: ")
    attribute_value = input("Enter attribute value: ")

    converted_value = eval(f"{type_name}('{attribute_value}')")
    setattr(selected_object, attribute_name, converted_value)

    print(f"\nThe attribute \"{attribute_name}\" of the object with name \"{selected_object.name}\"" +
          f" was set to the value \"{converted_value}\".")

    save_tip()


def attributes() -> None:
    if selected_object is None:
        print(ERROR_NO_OBJECT_SELECTED)
        return

    print("The select object has the following attributes:")
    for field in [field for field in dir(selected_object) if not field.startswith("_")]:
        print(f" * {field}")


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
    save_tip()


def delete_author() -> None:
    author_name = input("Author Name: ")
    author = db.query(Author).filter_by(name=author_name).first()
    if author:
        for blog_post in author.blog_posts:
            print(f"Deleted blog post \"{blog_post.name}\".")
            shutil.rmtree(blog_post.slug_path)
            db.delete(blog_post)

        db.delete(author)
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
    save_tip()


def delete_blog_post() -> None:
    blog_post_id = int(input("Blog Post ID: "))
    blog_post = db.query(BlogPost).get(blog_post_id)
    if blog_post:
        if os.path.exists(blog_post.slug_path):
            shutil.rmtree(blog_post.slug_path)

        db.delete(blog_post)
        print(f"Deleted blog post \"{blog_post.name}\".")

    else:
        print(f"No blog post with ID: {blog_post_id}.")


def create_tag() -> None:
    tag_name = input("Tag Name: ")
    tag = Tag(tag_name)
    db.add(tag)
    save_tip()


def delete_tag() -> None:
    tag_name = input("Tag Name: ")
    tag = db.query(BlogPost).filter_by(name=tag_name).first()
    if tag:
        db.delete(tag)
        print(f"Deleted tag \"{tag.name}\".")

    else:
        print(f"No tag with name: \"{tag_name}\".")


def delete_selected() -> None:
    if selected_object is None:
        print(ERROR_NO_OBJECT_SELECTED)
        return

    print(f"Deleted select object with name \"{selected_object.name}\"!")
    db.delete(selected_object)


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


def exit_program() -> None:
    print("Exiting...\n")
    sys.exit(-1)


def save_changes() -> None:
    print("Saving changes... ", end="")

    try:
        db.commit()
        print("Done!")
    except IntegrityError:
        print("Error!\n\n" +
              "This error was caused by invalid data.\n" +
              "You probably created multiple records with non-unique names.")


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
            None: delete_selected,
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

        "set": {
            None: set_selected_object_attribute,
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

        "attributes": {
            None: attributes,
        },

        "cls": {
            None: lambda: os.system("cls") if os.name == "nt" else os.system("clear"),
        },

        "save": {
            None: save_changes,
        },
    }

    while True:
        command_list = [command.lower() for command in input("> ").split()]
        if not command_list:
            continue

        if len(command_list) not in [1, 2] or command_list[0] not in commands.keys():
            print("Invalid command!\n")
            continue

        base_command = commands[command_list[0]]
        sub_command_key = command_list[1] if 1 < len(command_list) else None
        if sub_command_key is not None:
            sub_command_key = sub_command_key.rstrip("s")  # Allow "post" and "posts"

        if sub_command_key not in base_command.keys():
            print("Invalid sub-command!\n")
            continue

        base_command[sub_command_key]()
        print()


if __name__ == "__main__":
    main()
