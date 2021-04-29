#!/usr/bin/env python3

import os
import re
import sys
import shutil
from zipfile import ZipFile, ZIP_LZMA

from compiler_blog import compile_all_blog_posts, compile_blog_post
from compiler_core import clean_compiler_output
from compiler_graph import compile_all_graph_pages
from misc import read_file

if os.name != "nt":
    import readline
    str(readline)

from functools import partial
from typing import Optional, Callable

from sqlalchemy.exc import IntegrityError
from spellchecker.spellchecker import SpellChecker

from sqlbase import db, Author, BlogPost, Tag, TagAssociation, Friend, Nameable, ReferrerHostname, Comment

BACKUP_FILE_NAME = "backup.zip"

ERROR_NO_OBJECT_SELECTED = "No object selected!"
ERROR_ATTRIBUTE_DOES_NOT_EXIST = "Attribute does not exist!"

BANNER = """\
-=[ Blog Manager ]=-
"""

selected_object: Optional[Nameable] = None


def yes_or_no(message: str) -> bool:
    return input(f"{message} (y/n)? ").lower().startswith("y")


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
          f" \"{result}\" of the type \"{result.__class__.__name__}\".")


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
        print(f" * {getattr(selected_object, field).__class__.__name__.ljust(16)} - {field}")


def select_object(row_class: type) -> None:
    object_id = int(input(f"{row_class.__name__} ID: "))
    if not (result := db.query(row_class).get(object_id)):
        print(f"No object of type {row_class.__name__} with ID {object_id} exists.")
        return

    global selected_object
    selected_object = result
    print(f"Selected object with name \"{selected_object.name}\"!")


def show_rows(row_class: type) -> None:
    if rows := db.query(row_class).all():
        print(f"Currently registered {row_class.__name__}s:")
        for row in rows:
            print(f" * {str(row.id).rjust(3)} - \"{row.name}\"")
    else:
        print(f"There are currently no registered {row_class.__name__}s.")


def x_if_true(value: bool) -> str:
    return "x" if value else " "


def show_posts() -> None:
    if posts := db.query(BlogPost).all():
        longest_title = max(len(post.name) for post in posts)
        longest_author = max(len(post.author.name) for post in posts)
        print(f"|  ID | {'Title'.rjust(longest_title)} | {'Author'.rjust(longest_author)} | "
              f"Hits | Commentable | In Graph | Hidden |")

        print(f"|-----|-{'-' * longest_title}-|-{'-' * longest_author}-|------|-------------|----------|--------|")
        for post in posts:
            print(f"| {str(post.id).rjust(3)} | {post.name.rjust(longest_title)} | "
                  f"{post.author.name.rjust(longest_author)} | "
                  f"{str(post.hits).rjust(4)} | "
                  f"     {x_if_true(post.allow_comments)}      | "
                  f"    {x_if_true(post.include_in_graph)}    | "
                  f"   {x_if_true(post.hidden)}   |")

    else:
        print("There are currently no posts.")


def show_help(commands: any) -> None:
    print("Possible Commands:")
    for base_command in commands:
        print(f" * {base_command}", end="")
        sub_commands_string = "|".join([command for command in commands[base_command] if type(command) is str])
        if sub_commands_string:
            print(f" ({sub_commands_string})", end="")
        print()


def delete_comment() -> None:
    comment_id = int(input("Comment ID: "))
    if comment := db.query(Comment).get(comment_id):
        db.delete(comment)
        print(f"Deleted comment \"{comment.name}\".")
        save_tip()
        return

    print(f"No comment with ID: {comment_id}.")


def create_author() -> None:
    name = input("Author Name: ")
    biography = input("Biography: ")

    author = Author(name, biography)
    db.add(author)
    save_tip()


def delete_author() -> None:
    author_name = input("Author Name: ")
    if author := db.query(Author).filter_by(name=author_name).first():
        for blog_post in author.blog_posts:
            print(f"Deleted blog post \"{blog_post.name}\".")
            shutil.rmtree(blog_post.slug_path)
            db.delete(blog_post)

        db.delete(author)
        print(f"Deleted author \"{author.name}\".")
        save_tip()
        return

    print(f"No author with name: \"{author_name}\".")


def create_blog_post() -> None:
    author_name = input("Author Name: ")
    if not (author := db.query(Author).filter_by(name=author_name).first()):
        print(f"No author with name: \"{author_name}\".")
        exit()

    title = input("Blog Post Title: ")

    blog_post = BlogPost(title, author)
    os.makedirs(blog_post.resources_path)

    open(blog_post.markdown_path, "w").close()
    db.add(blog_post)
    save_tip()


def mark_post_as_graph_page() -> None:
    blog_post_id = int(input("Blog Post ID: "))
    if blog_post := db.query(BlogPost).get(blog_post_id):
        blog_post.include_in_graph = yes_or_no("Enable graph annotations")
        blog_post.allow_comments = yes_or_no("Allow comments")
        blog_post.hidden = yes_or_no("Hide post")

        print(f"Changed flags of \"{blog_post.name}\".")
        save_tip()
        return

    print(f"No blog post with ID: {blog_post_id}.")


def delete_blog_post() -> None:
    blog_post_id = int(input("Blog Post ID: "))
    if blog_post := db.query(BlogPost).get(blog_post_id):
        if os.path.exists(blog_post.slug_path):
            shutil.rmtree(blog_post.slug_path)

        db.delete(blog_post)
        print(f"Deleted blog post \"{blog_post.name}\".")
        save_tip()
        return

    print(f"No blog post with ID: {blog_post_id}.")


def create_friend() -> None:
    friend_name = input("Friend Name: ")
    friend_link = input("Link: ")
    friend_description = input("Description: ")

    friend = Friend(friend_name, friend_link, friend_description)
    db.add(friend)
    save_tip()


def create_tag() -> None:
    tag_name = input("Tag Name: ")
    tag_short_desc = input("Tag short description: ")
    tag_long_desc = input("Tag long description: ")
    tag_main = yes_or_no("Is tag a section")
    tag = Tag(tag_name, tag_short_desc, tag_long_desc, tag_main)
    db.add(tag)
    save_tip()


def generic_delete_by_name(row_class: type, input_question: str, deleted_prefix: str, error_prefix: str) -> Callable:
    def concrete():
        name = input(input_question)
        if obj := db.query(row_class).filter_by(name=name).first():
            print(f"{deleted_prefix} \"{obj.name}\".")
            db.delete(obj)
            save_tip()
            return

        print(f"{error_prefix} \"{name}\".")

    return concrete


def delete_selected() -> None:
    if selected_object is None:
        print(ERROR_NO_OBJECT_SELECTED)
        return

    print(f"Deleted select object with name \"{selected_object.name}\"!")
    db.delete(selected_object)
    save_tip()


def attach_tag() -> None:
    tag_name = input("Tag Name: ")
    blog_post_id = int(input("Blog Post ID: "))

    if not (tag := db.query(Tag).filter_by(name=tag_name).first()):
        print("Tag not found!")
        return

    if not (blog_post := db.query(BlogPost).get(blog_post_id)):
        print("Post not found!")
        return

    print(f"Attached tag \"{tag.name}\" to post \"{blog_post.name}\"!")
    tag_association = TagAssociation(blog_post_id, tag.id)
    db.add(tag_association)
    save_tip()


def detach_tag() -> None:
    tag_name = input("Tag Name: ")
    blog_post_id = int(input("Blog Post ID: "))

    if not (tag := db.query(Tag).filter_by(name=tag_name).first()):
        print("Tag not found!")
        return

    if not (blog_post := db.query(BlogPost).get(blog_post_id)):
        print("Post not found!")
        return

    if (tag_association := db.query(TagAssociation).filter_by(blog_post_id=blog_post_id, tag_id=tag.id)
            .first()) is None:
        print("Tag is not attached to post!")
        return

    print(f"Detached tag \"{tag.name}\" from post \"{blog_post.name}\"!")
    db.delete(tag_association)
    save_tip()


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


def zip_dir(pathname: str, zipfile: ZipFile) -> None:
    for root, dirs, files in os.walk(pathname):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(os.path.join(root, file), os.path.join(pathname, ".."))
            zipfile.write(file_path, relative_path)


def make_backup() -> None:
    if os.path.exists(BACKUP_FILE_NAME):
        print("Removing old backup...")
        os.remove(BACKUP_FILE_NAME)

    print("Backing up...")
    with ZipFile(BACKUP_FILE_NAME, "w", ZIP_LZMA) as f:
        zip_dir("blogposts", f)
        f.write("blog.db")
        f.write("config.json")

    print(f"Done! ({os.path.getsize(BACKUP_FILE_NAME)} bytes)")


def compile_post_by_id() -> None:
    blog_post_id = int(input("Blog Post ID: "))
    if not (blog_post := db.query(BlogPost).get(blog_post_id)):
        print("Post not found!")
        return

    compile_blog_post(blog_post)


def recompile_all_posts() -> None:
    clean_compiler_output()
    compile_all_blog_posts()
    compile_all_graph_pages()


def spellcheck() -> None:
    en_checker = SpellChecker(language="en")
    de_checker = SpellChecker(language="de")
    for post in db.query(BlogPost):
        markdown = read_file(post.markdown_path)
        for i, line in enumerate(markdown.splitlines()):
            words = [re.sub(r"[^a-zA-Z ]", " ", word).strip() for word in line.split()]
            words = [word for word in words if word]

            unknown_en_words = en_checker.unknown(words)
            unknown_de_words = de_checker.unknown(words)

            unknown_words = [word for word in unknown_en_words if word in unknown_de_words]

            for unknown_word in unknown_words:
                print(f"In \"{post.name}\" (line {i + 1}): Unknown word \"{unknown_word}\".")

    print("Done!")


def main() -> None:
    print(BANNER)

    commands = {
        "create": {
            "author": create_author,
            "post": create_blog_post,
            "friend": create_friend,
            "tag": create_tag,
        },

        "delete": {
            "author": delete_author,
            "post": delete_blog_post,
            "friend": generic_delete_by_name(Friend, "Friend Name: ", "Deleted friend", "No friend with name:"),
            "tag": generic_delete_by_name(Tag, "Tag Name: ", "Deleted tag", "No tag"),
            "hostname": generic_delete_by_name(ReferrerHostname, "Hostname: ", "Deleted hostname", "No hostname"),
            "comment": delete_comment,
            None: delete_selected,
        },

        "show": {
            "author": partial(show_rows, Author),
            "post": show_posts,
            "friend": partial(show_rows, Friend),
            "tag": partial(show_rows, Tag),
            "hostname": partial(show_rows, ReferrerHostname),
            "comment": partial(show_rows, Comment),
        },

        "tag": {
            "attach": attach_tag,
            "detach": detach_tag,
        },

        "select": {
            "author": partial(select_object, Author),
            "post": partial(select_object, BlogPost),
            "friend": partial(select_object, Friend),
            "tag": partial(select_object, Tag),
            "hostname": partial(select_object, ReferrerHostname),
            "comment": partial(select_object, Comment),
        },

        "compile": {
            "all": recompile_all_posts,
            "id": compile_post_by_id,
            "graph": compile_all_graph_pages,
            "blog": compile_all_blog_posts,
        },

        "get": {None: get_selected_object_attribute},
        "set": {None: set_selected_object_attribute},
        "attributes": {None: attributes},
        "mark": {None: mark_post_as_graph_page},

        "save": {None: save_changes},
        "exit": {None: exit_program},

        "spellcheck": {None: spellcheck},
        "backup": {None: make_backup},
        "clear": {None: lambda: os.system("cls") if os.name == "nt" else os.system("clear")},
        "help": {None: lambda: show_help(commands)},
    }

    while True:
        if not (command_list := [command.lower() for command in input("> ").split()]):
            continue

        if len(command_list) not in [1, 2] or command_list[0] not in commands.keys():
            print("Invalid command!\n")
            continue

        base_command = commands[command_list[0]]
        sub_command_key = command_list[1].rstrip("s") if 1 < len(command_list) else None  # Allow "post" and "posts"
        if sub_command_key not in base_command.keys():
            print("Invalid sub-command!\n")
            continue

        base_command[sub_command_key]()
        print()


if __name__ == "__main__":
    main()
