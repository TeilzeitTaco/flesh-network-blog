#!/usr/bin/env python3

import os
import sys
import shutil

from sqlbase import db, Author, BlogPost, Tag, TagAssociation
from compiler import compile_all_posts


BANNER = """\
-=[ Blog Manager ]=-
"""


def create_author() -> None:
    name = input("Author Name: ")
    biography = input("Biography: ")

    author = Author(name, biography)
    db.add(author)
    db.commit()


def show_authors() -> None:
    print("Currently registered authors:")
    for author in db.query(Author):
        print(f" * {str(author.id).rjust(3)} - \"{author.name}\"")


def delete_author() -> None:
    author_id = int(input("Author ID: "))
    author = db.query(Author).get(author_id)
    if author:
        for blog_post in author.blog_posts:
            print(f"Deleted blog post \"{blog_post.title}\".")
            shutil.rmtree(blog_post.slug_path)
            db.delete(blog_post)

        db.delete(author)
        db.commit()
        print(f"Deleted author \"{author.name}\".")

    else:
        print(f"No author with ID: {author_id}.")


def create_blog_post() -> None:
    author_id = int(input("Author ID: "))
    title = input("Blog Post Title: ")

    blog_post = BlogPost(title, author_id)
    os.makedirs(blog_post.resources_path)

    open(blog_post.markdown_path, "w").close()

    db.add(blog_post)
    db.commit()


def show_blog_posts() -> None:
    print("Current blog posts:")
    for blog_post in db.query(BlogPost):
        print(f" * {str(blog_post.id).rjust(3)} - \"{blog_post.title}\"")


def delete_blog_post() -> None:
    blog_post_id = int(input("Blog Post ID: "))
    blog_post = db.query(BlogPost).get(blog_post_id)
    if blog_post:
        shutil.rmtree(blog_post.slug_path)
        db.delete(blog_post)
        db.commit()
        print(f"Deleted blog post \"{blog_post.title}\".")

    else:
        print(f"No blog post with ID: {blog_post_id}.")


def create_tag() -> None:
    tag_name = input("Tag Name: ")
    tag = Tag(tag_name)
    db.add(tag)
    db.commit()


def show_tags() -> None:
    print("Current tags:")
    for tag in db.query(Tag):
        print(f" * {str(tag.id).rjust(3)} - \"{tag.name}\"")


def delete_tag() -> None:
    tag_id = int(input("Tag ID: "))
    tag = db.query(BlogPost).get(tag_id)
    if tag:
        db.delete(tag)
        db.commit()
        print(f"Deleted tag \"{tag.name}\".")

    else:
        print(f"No tag with ID: {tag_id}.")


def attach_tag() -> None:
    tag_id = int(input("Tag ID: "))
    blog_post_id = int(input("Blog Post ID: "))

    tag = db.query(Tag).get(tag_id)
    blog_post = db.query(BlogPost).get(blog_post_id)

    if not (tag and blog_post):
        print("Tag or blog post not found.")

    else:
        tag_association = TagAssociation(blog_post_id, tag_id)
        db.add(tag_association)
        db.commit()


def exit_program() -> None:
    print("Exiting...")


def main() -> None:
    print(BANNER)

    options = {
        "Author Management": [
            ("Create Author", create_author),
            ("Show Authors", show_authors),
            ("Delete Author", delete_author),
        ],

        "Blog Post Management": [
            ("Create Blog Post", create_blog_post),
            ("Show Blog Posts", show_blog_posts),
            ("Delete Blog Post", delete_blog_post),
        ],

        "Tag Management": [
            ("Create Tag", create_tag),
            ("Show Tags", show_tags),
            ("Delete Tag", delete_tag),
            ("Attach Tag", attach_tag),
        ],

        "Miscellaneous Options": [
            ("Compile Blog Posts", compile_all_posts),
            ("Exit", exit_program),
        ],
    }

    # Print the options menu
    i = 1
    option_functions = list()
    for key, value in options.items():
        print(f"{key}:")
        for option in value:
            option_functions.append(option[1])
            print(f" * {str(i).rjust(2)} - {option[0]}")
            i += 1
        print()

    # Get input and invoke the selected function
    selected_option = int(input("Enter Option: ") or str(len(option_functions))) - 1
    print()

    if 0 <= selected_option < len(option_functions):
        option_functions[selected_option]()  # Execute option
        sys.exit(0)

    print("Invalid option.")
    sys.exit(-1)


if __name__ == "__main__":
    main()
