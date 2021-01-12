#!/usr/bin/env python3

import os
import sys
import shutil

from sqlbase import db, Author, BlogPost
from compiler import compile_all_posts


BANNER = """\
-=[ Blog Manager ]=-
"""


def create_author() -> None:
    name = input("Name: ")
    biography = input("Biography: ")

    author = Author(name, biography)
    db.add(author)
    db.commit()


def show_authors() -> None:
    print("Currently registered authors:")
    for author in db.query(Author):
        print(f" ({author.id}) - \"{author.name}\"")


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
    title = input("Title: ")

    blog_post = BlogPost(title, author_id)
    os.makedirs(blog_post.resources_path)

    open(blog_post.markdown_path, "w").close()

    db.add(blog_post)
    db.commit()


def show_blog_posts() -> None:
    print("Current blog posts:")
    for blog_post in db.query(BlogPost):
        print(f" ({blog_post.id}) - \"{blog_post.title}\"")


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


def exit_program() -> None:
    print("Exiting...")


def main() -> None:
    print(BANNER)

    options = [
        ("Create Author", create_author),
        ("Show Authors", show_authors),
        ("Delete Author", delete_author),
        ("Create Blog Post", create_blog_post),
        ("Show Blog Posts", show_blog_posts),
        ("Delete Blog Post", delete_blog_post),
        ("Compile Blog Posts", compile_all_posts),
        ("Exit", exit_program),
    ]

    for i in range(len(options)):
        print(f" ({i + 1}) - {options[i][0]}")

    print()
    selected_option = int(input("Enter Option: ") or str(len(options))) - 1
    print()
    if 0 <= selected_option < len(options):
        options[selected_option][1]()  # Execute option
        sys.exit(0)

    print("Invalid option.")
    sys.exit(-1)


if __name__ == "__main__":
    main()
